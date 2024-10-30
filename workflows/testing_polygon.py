from graph_entities.graphs import *
from tools import *


def launch_workflow():
    graph = create_msf_tools_team_graph()

    all_groups = get_msf_sub_groups_list()
    main_task = 'Please investigate this host: 10.10.11.23'

    input_message = {
        MESSAGES_FIELD: [
            AIMessage(
                content=f'Please prepare the list of metasploit modules of the relevant groups to this task, that '
                        f'I can create a pentesting plan according this task: {main_task}!\n'
                        f'All metasploit group: {all_groups}.'
            )
        ],
        SENDER_FIELD: [TOOLS_TEAM],
    }

    event = execute_graph(
                graph=graph,
                full_task_message=input_message
    )

    modules = extract_results(event)

    output = {
        MESSAGES_FIELD: AIMessage(content=f'The task was done! The modules were added in "{MODULES_FIELD}" field!'),
        MODULES_FIELD: modules
    }
    print(output)


def extract_results(event: Dict):
    messages = event.get(MESSAGES_FIELD)
    result = []
    for message in messages[::-1]:
        if not isinstance(message, ToolMessage):
            return result

        result += message.content.replace("['", "").replace("']", "").split("', '")
