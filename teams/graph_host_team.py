from graph_entities.conditions import *
from utils.llm import *
from teams.graph_planning_team import *
from teams.graph_testing_team import *


def create_host_graph():
    model_llm = create_llm('gpt-4o-2024-08-06')
    nodes_fabric = NodesFabric(model_llm=model_llm)

    host_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_without_tools,
        sys_msg_path='host/host#1.txt',
        node_func=create_ordinary_node,
        node_name=HOST_NODE
    )

    chooser_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_without_tools,
        sys_msg_path='host/chooser#1.txt',
        node_func=create_chooser_node,
        node_name=CHOOSER_NODE,
        chooser_options=[FINAL_ANSWER, TESTER_AGENT, PLANNER_TEAM]
    )

    planner_node = nodes_fabric.create_team_node(
        graph_func=create_host_planner_graph,
        node_func=create_connector_sub_graph,
        name=PLANNER_TEAM,
        conditional_func=planner_team_conditions
    )

    tester_node = nodes_fabric.create_team_node(
        graph_func=create_host_testing_graph,
        node_func=create_connector_sub_graph,
        name=TESTER_TEAM,
    )

    graph = StateGraph(PlanningTeamState)

    graph.add_node(HOST_NODE, host_node)
    graph.add_node(PLANNER_NODE, planner_node)
    graph.add_node(CHOOSER_NODE, chooser_node)
    graph.add_node(TESTER_NODE, tester_node)

    graph.add_edge(START, HOST_NODE)
    graph.add_edge(HOST_NODE, CHOOSER_NODE)

    graph.add_conditional_edges(
        CHOOSER_NODE,
        router_chooser_node,
        {
            '__end__': END,
            CHOOSER_NODE: CHOOSER_NODE,
            PLANNER_NODE: PLANNER_NODE,
            TESTER_NODE: TESTER_NODE

        }
    )

    graph.add_edge(PLANNER_NODE, HOST_NODE)
    graph.add_edge(TESTER_NODE, HOST_NODE)

    return graph
