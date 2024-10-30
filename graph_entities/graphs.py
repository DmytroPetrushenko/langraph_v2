import functools
from langgraph.constants import START, END

import utils.llm
from fabric.nodes_fabric import NodesFabric
from graph_entities.agents import *
from graph_entities.nodes import *
from graph_entities.routers import *
from graph_entities.schemes import *
from graph_entities.statets import *
from tools.msf_tools import *


MODULE_SELECTION_TOOLS = [get_msf_exact_sub_group_modules_list]


def initializer_plan_composition_graph(
        model_llm: ChatOpenAI,
        msg_path: Optional[Dict[str, str]] = None
) -> StateGraph:
    """
        Initializes the plan composition graph by setting up agents, nodes, and the graph structure.

        Args:
            model_llm (ChatOpenAI): The language model to be used for agents in the graph.
            msg_path (Optional[Dict[str, str]]): A dictionary containing custom paths for system messages.
                                                 Defaults will be used if not provided.

        Returns:
            StateGraph: The graph object containing nodes and edges for the plan composition process.
    """

    # CREATE SYSTEM MESSAGES
    if msg_path is None:
        plan_composition_msg_path: str = PLAN_COMPOSITION_MSG_PATH
        extraction_msg_path: str = EXTRACTION_MSG_PATH
    else:
        # Use custom paths if provided, otherwise fall back to defaults
        plan_composition_msg_path: str = msg_path.get('plan_composition_msg_path', PLAN_COMPOSITION_MSG_PATH)
        extraction_msg_path: str = msg_path.get('extraction_msg_path', EXTRACTION_MSG_PATH)

    plan_composition_sys_msg = create_message_from_file(plan_composition_msg_path)
    extraction_sys_msg = create_message_from_file(extraction_msg_path)

    # CREATE THE AGENTS
    plan_composition_agent = assistant_agent_without_tools(
        system_message=plan_composition_sys_msg,
        model_llm=model_llm
    )

    plan_extraction_agent = assistant_agent_with_constructed_output(
        system_message=extraction_sys_msg,
        model_llm=model_llm,
        oai_schema=plan_extraction_scheme
    )

    # CREATE THE NODES
    plan_composition_node = functools.partial(
        create_ordinary_node,
        agent=plan_composition_agent,
        name=PLAN_COMPOSITION_NODE
    )

    plan_extraction_node = functools.partial(
        create_extraction_node,
        agent=plan_extraction_agent,
        name=PLAN_EXTRACTION_NODE
    )

    # CREATE A GRAPH
    graph = StateGraph(PlanningTeamState)

    # Add the nodes
    graph.add_node(PLAN_COMPOSITION_NODE, plan_composition_node)
    graph.add_node(PLAN_EXTRACTION_NODE, plan_extraction_node)

    # Add the edges between the nodes
    graph.add_edge(START, PLAN_COMPOSITION_NODE)
    graph.add_edge(PLAN_COMPOSITION_NODE, PLAN_EXTRACTION_NODE)
    graph.add_edge(PLAN_EXTRACTION_NODE, END)

    return graph


def initializer_nmap_graph(model_llm, tools):
    nodes_fabric = NodesFabric(model_llm)

    nmap_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_tools,
        sys_msg_path='testing_team/tester_nmap#1.txt',
        node_func=create_ordinary_node,
        node_name=NMAP_TESTER_NODE,
        tools=tools
    )

    execution_node = functools.partial(
        create_tool_node,
        tools=tools
    )

    graph = StateGraph(PlanningTeamState)

    graph.add_node(NMAP_TESTER_NODE, nmap_node)
    graph.add_node(EXECUTOR_NODE, execution_node)

    graph.add_edge(START, NMAP_TESTER_NODE)
    graph.add_conditional_edges(
        NMAP_TESTER_NODE,
        router_nmap_node,
        {
            '__end__': END,
            'continue': NMAP_TESTER_NODE,
            EXECUTOR_NODE: EXECUTOR_NODE
        }
    )

    graph.add_edge(EXECUTOR_NODE, NMAP_TESTER_NODE)

    return graph


def create_msf_tools_team_graph(model_llm: Optional[Union[ChatOpenAI, ChatAnthropic, Callable]] = None):
    nodes_fabric = NodesFabric(model_llm=model_llm)

    gpt_4o_mini = utils.llm.create_llm('gpt-4o-mini')
    gpt_4o = utils.llm.create_llm('gpt-4o-2024-08-06')

    # NODES
    group_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_without_tools,
        model_llm=gpt_4o,
        sys_msg_path='planning_team/group_selection_agent#1.txt',
        node_func=create_ordinary_node,
        node_name=GROUP_SELECTION_NODE
    )
    module_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_tools,
        model_llm=gpt_4o_mini,
        sys_msg_path='planning_team/module_selection_agent#1.txt',
        node_func=create_ordinary_node,
        node_name=MODULE_SELECTION_NODE,
        tools=MODULE_SELECTION_TOOLS
    )

    executor_node = functools.partial(
        create_tool_node,
        tools=MODULE_SELECTION_TOOLS
    )

    graph = StateGraph(PlanningTeamState)

    graph.add_node(GROUP_SELECTION_NODE, group_node)
    graph.add_node(MODULE_SELECTION_NODE, module_node)
    graph.add_node(EXECUTOR_NODE, executor_node)

    graph.add_edge(START, GROUP_SELECTION_NODE)
    graph.add_edge(GROUP_SELECTION_NODE, MODULE_SELECTION_NODE)
    graph.add_edge(MODULE_SELECTION_NODE,EXECUTOR_NODE)
    graph.add_edge(EXECUTOR_NODE, END)


    return graph
