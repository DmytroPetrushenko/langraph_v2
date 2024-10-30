from graph_entities.graphs import *
from teams.graph_planning_team import create_host_planner_graph
from tools import *


def launch_workflow(task: str):
    graph = create_host_planner_graph()

    input_message = {
        MESSAGES_FIELD: [
            AIMessage(
                content=task
            )
        ],
        SENDER_FIELD: [PLANNER_TEAM],
    }

    event = execute_graph(
        graph=graph,
        full_task_message=input_message
    )

    output = {
        MESSAGES_FIELD: AIMessage(content=""),
        SENDER_FIELD: [PLANNER_TEAM],
        PLAN_FIELD: event.get(PLAN_FIELD)
    }

    print(output)