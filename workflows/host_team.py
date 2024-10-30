from langchain_core.messages import HumanMessage

from graph_entities.graph_executors import execute_graph
from teams.graph_host_team import create_host_graph


def launcher_host_team(task: str):
    input_dict = {
        'messages': [HumanMessage(content=task)],
        'sender': ['Human']
    }

    graph = create_host_graph()

    execute_graph(
        graph=graph,
        full_task_message=input_dict,
        thread_id=1
    )
