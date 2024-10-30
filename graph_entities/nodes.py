import random
from typing import Sequence, Union, Callable, Dict, List, Optional

from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import ToolMessage, BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolInvocation, ToolExecutor

from constants import *
from tools import get_msf_sub_groups_list
from utils.common_utils import save_and_open_graph
from graph_entities.graph_executors import execute_graph
from graph_entities.statets import TeamState, PlanningTeamState


def create_tool_node(
        state: Union[PlanningTeamState, TeamState],
        tools: Sequence[Union[BaseTool, Callable]]
) -> Dict[str, List[ToolMessage]]:
    messages = state.messages

    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    tool_calls = last_message.tool_calls
    tool_messages = []
    for tool_call in tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"]
        )
        tool_executor = ToolExecutor(tools)
        # We call the tool_executor and get back a response
        response = tool_executor.invoke(action)
        # We use the response to create a ToolMessage
        tool_message = ToolMessage(
            content=str(response),
            name=action.tool,
            tool_call_id=tool_call["id"]
        )
        tool_messages.append(tool_message)
    # We return a list, because this will get added to the existing list
    return {MESSAGES_FIELD: tool_messages, SENDER_FIELD: [EXECUTOR_NODE]}


def create_ordinary_node(state: Union[TeamState, PlanningTeamState], agent, name: str):
    """
    Creates a standard node by invoking an agent with the current state and returning the updated state.

    Args:
        state: The current state (PlanningState or UnifiedState), containing messages and sender information.
        agent: The agent to invoke using the messages from the state.
        name: The name of the node or agent invoking the operation.

    Returns:
        A dictionary containing the updated messages and sender after invoking the agent.
    """

    messages: List[BaseMessage] = state.messages

    if name is PROCESS_EVALUATION_NODE:
        messages = [AIMessage(content=f'Feedback:\n{state.validator_feedback}')]

    if name is PLAN_COMPOSITION_NODE and state.modules:
        messages.append(AIMessage(content=f'The list of metasploit modules: {state.modules}!'))
    if name is CHOOSER_NODE:
        messages = [state.messages[-1]]

    # Invoke the agent with the current state
    response = agent.invoke({'messages': messages})

    # Return the updated state, which includes the new message and sender's name
    return {
        MESSAGES_FIELD: [response],  # Add the new message to the list of messages
        SENDER_FIELD: [name]  # Set the sender to the current agent's name
    }


def create_extraction_node(state: PlanningTeamState, agent, name: str):
    """
    Creates a module extraction node based on the last message sender in the team's state.

    This function invokes the given agent with the latest message from the team's state and
    determines what information needs to be extracted (module subgroups, modules, or the plan)
    based on the sender of the last message. Depending on the sender, it creates the appropriate
    output for updating the team's state.

    Args:
        state (TeamState): The current state of the team, which includes the list of messages and senders.
        agent: The agent responsible for processing the latest message and returning relevant information.
        name (str): The name of the current module extraction node, which will be added to the sender field.

    Returns:
        dict: A dictionary containing the updated fields (messages, sender, and either subgroups, modules, or the plan)
              based on the last sender in the state.

    Raises:
        ValueError: If the last sender is not recognized as one of the expected nodes: MODULE_GROUP_SELECTION_NODE,
                    MODULE_SELECTION_NODE, or PLAN_COMPOSITION_NODE.
    """

    # Get the agent's response to the last message in the team's state
    response: Dict[str, List[str]] = agent.invoke([state.messages[-1]])
    last_sender = state.sender[-1]  # Retrieve the last sender from the team's state

    # Check the last sender and update the appropriate fields based on its value
    if last_sender is PLAN_COMPOSITION_NODE:
        output = {
            MESSAGES_FIELD: [AIMessage(content=PLAN_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            PLAN_FIELD: [response.get(PLAN_FIELD)]
        }
    else:
        # Raise an error if the sender is not one of the expected nodes
        raise ValueError(f"Unexpected sender: '{last_sender}' in {name}. "
                         f"Expected -> {PLAN_COMPOSITION_NODE}.")

    # Return the constructed output dictionary for updating the team's state
    return output


def connector_to_sub_graph_for_planning_team_node(state: PlanningTeamState, name: str, graph):
    compiled_graph: CompiledStateGraph = graph.compile()

    border = SubGraphBorder(name)

    # drawing the graph
    save_and_open_graph(compiled_graph)

    # create a config
    randint: int = random.randint(0, 100000)
    config = {"configurable": {"thread_id": randint}}
    task_msg = state.messages[0]

    inputs: Optional[Dict] = None

    if name is GROUP_SELECTION_TEAM:
        inputs = {
            MESSAGES_FIELD: [task_msg],
            SENDER_FIELD: [name]
        }
    elif name is MODULE_SELECTION_TEAM:
        inputs = {
            MESSAGES_FIELD: [task_msg] + [HumanMessage(content=f'It is the list of relevant '
                                                               f'sub-groups: {state.sub_groups}! Use just them!')],
            SENDER_FIELD: [name]
        }
    elif name is PLAN_COMPOSITION_TEAM:
        if state.sender[-1] is PROCESS_EVALUATION_NODE:
            inputs = {
                MESSAGES_FIELD: [
                    HumanMessage(
                        content=f'It is your early generated plan:\n<<\n{state.plan}\n>>\nAnd Validator agent ask you '
                                f'to fix it accordingly his message :\n<<\n{state.validator_feedback}\n>>'
                    )
                ],
                SENDER_FIELD: [name]
            }
        else:
            inputs = {
                MESSAGES_FIELD: [task_msg] + [HumanMessage(content=f'It is the list of relevant metasploit modules: '
                                                                   f'{state.modules}! Use just them!')],
                SENDER_FIELD: [name]
            }
    elif name is VALIDATOR_TEAM:
        inputs = {
            MESSAGES_FIELD: [
                HumanMessage(
                    content=f"Please review the following pentesting plan based on the Metasploit Framework tools:"
                            f"\n<<\n{state.plan}\n>>\nAnd evaluate its alignment with the task:\n\"{task_msg.content}\""
                            f"\nFocus on identifying any gaps or inefficiencies and suggest improvements for automated "
                            f"testing."
                )],
            SENDER_FIELD: [name]
        }

    # Stream results from the graph execution and print the output
    border.sub_graph_beginning_border()
    event: Optional[Dict] = None
    for event in compiled_graph.stream(inputs, config, stream_mode='values'):
        message: AIMessage | HumanMessage = event['messages'][-1]

        # Print the message
        message.pretty_print()
    border.sub_graph_ending_border()

    if name is GROUP_SELECTION_TEAM:
        output = {
            MESSAGES_FIELD: [AIMessage(content=GROUPS_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            GROUPS_FIELD: event[GROUPS_FIELD]
        }
    elif name is MODULE_SELECTION_TEAM:
        output = {
            MESSAGES_FIELD: [AIMessage(content=MODULES_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            MODULES_FIELD: event[MODULES_FIELD]
        }

    elif name is PLAN_COMPOSITION_TEAM:
        output = {
            MESSAGES_FIELD: [AIMessage(content=PLAN_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            PLAN_FIELD: event[PLAN_FIELD]
        }
    elif name is VALIDATOR_TEAM:
        output = {
            MESSAGES_FIELD: [AIMessage(content=VALIDATOR_SAVED_MESSAGE)],
            SENDER_FIELD: [name],
            VALIDATOR_FIELD: event[VALIDATOR_FIELD]
        }
    else:
        raise ValueError(f"Unexpected sender: '{name}' in a connector_node. "
                         f"Expected -> {GROUP_SELECTION_NODE} or {MODULE_SELECTION_NODE} "
                         f"or {PLAN_COMPOSITION_NODE} or {VALIDATOR_TEAM}.")

    return output


def create_connector_sub_graph(state: PlanningTeamState, name: str, graph: StateGraph,
                               conditional_func: Callable = None):
    messages = state.messages

    task_for_team: BaseMessage = messages[-1]

    full_task_message = {
        MESSAGES_FIELD: [task_for_team],
        SENDER_FIELD: [name]
    }
    if conditional_func:
        extra_data = conditional_func(name=name, state=state)
        if extra_data:
            full_task_message[MESSAGES_FIELD].append(AIMessage(content=extra_data))

    if name is MODULE_SELECTION_TEAM:
        full_task_message[MESSAGES_FIELD].append(AIMessage(content=f"These are relevant groups: {state.sub_groups}! "
                                                                   f"Chose only the modules from them!"))

    # launch graph
    workflow_state = execute_graph(graph=graph, full_task_message=full_task_message)

    output = {
        SENDER_FIELD: [name]
    }

    fields_list = list(state.__fields__.keys())

    for field in fields_list:
        if field is MESSAGES_FIELD and workflow_state.get(field):
            output[field] = [workflow_state[field][-1]]
        elif field is not SENDER_FIELD and workflow_state.get(field):
            output[field] = workflow_state[field]

    return output


def create_chooser_node(state: Union[TeamState, PlanningTeamState], agent, name: str, chooser_options: List[str]):
    last_message = state.messages[-1]

    response = agent.invoke({'messages': [last_message]})

    if response not in chooser_options:
        output = {
            MESSAGES_FIELD: [AIMessage(content=f'You choose not from these options: {chooser_options} in a income '
                                               f'message. Try again! Income message is: {last_message.content}')],
            SENDER_FIELD: [name],
        }
    else:
        output = {
            CHOOSER_FIELD: response
        }

    return output


def connector_to_tools_team_node(
        state: PlanningTeamState,
        name: str,
        graph: StateGraph,
):
    main_task = state.messages[0].content

    all_groups = get_msf_sub_groups_list()

    input_message = {
        MESSAGES_FIELD: [
            AIMessage(
                content=f'Please prepare the list of metasploit modules of the relevant groups to this task, that '
                        f'I can create a pentesting plan according this task: {main_task}!\n'
                        f'All metasploit group: {all_groups}.'
            )
        ],
        SENDER_FIELD: [name],
    }

    event = execute_graph(graph=graph, full_task_message=input_message)

    modules = extract_results(event)

    output = {
        MESSAGES_FIELD: [AIMessage(content=f'Plan Composition Agent, the task was completed.')],
        MODULES_FIELD: modules
    }
    return output


def extract_results(event: Dict):
    messages = event.get(MESSAGES_FIELD)
    result = []
    for message in messages[::-1]:
        if not isinstance(message, ToolMessage):
            return result

        result += message.content.replace("['", "").replace("']", "").split("', '")


class SubGraphBorder:

    def __init__(self, name: str):
        self.name_for_separators = name.replace('_', ' ').capitalize()
        self.named_start = f"{33 * '*'} SUB GRAPH : {self.name_for_separators} {33 * '*'}"
        self.start = len(self.named_start) * '*'
        self.named_end = f"{33 * '*'} END SUB GRAPH {33 * '*'}"
        self.end = len(self.named_end) * '*'

    def sub_graph_beginning_border(self):
        print(self.start)
        print(self.named_start)
        print(self.start)

    def sub_graph_ending_border(self):
        print(self.end)
        print(self.named_end)
        print(self.end)
