from tools.nmap_tools import *
from graph_entities.graphs import *
from graph_entities.nodes import *
from graph_entities.statets import *

MSF_TOOLS = [tool_based_on_metasploit]
NMAP_TOOLS = [tool_based_on_nmap]
ARGS_TOOLS = [get_msf_module_options]


def create_host_testing_graph(model_llm: ChatOpenAI):
    nodes_fabric = NodesFabric(model_llm=model_llm)

    header_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_without_tools,
        sys_msg_path='testing_team/header#1.txt',
        node_func=create_ordinary_node,
        node_name=HEADER_NODE
    )

    msf_tester_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_tools,
        sys_msg_path='testing_team/tester_msf#1.txt',
        node_func=create_ordinary_node,
        tools=MSF_TOOLS,
        node_name=MSF_TESTER_NODE
    )

    nmap_tester_node = nodes_fabric.create_team_node(
        graph_func=initializer_nmap_graph,
        node_func=create_connector_sub_graph,
        name=NMAP_TESTER_NODE,
        tools=NMAP_TOOLS
    )

    combine_tools = [*MSF_TOOLS, *ARGS_TOOLS, *NMAP_TOOLS]
    execution_node = functools.partial(
        create_tool_node,
        tools=combine_tools
    )

    args_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_tools,
        sys_msg_path='testing_team/args_msf#1.txt',
        node_func=create_ordinary_node,
        tools=ARGS_TOOLS,
        node_name=ARGS_NODE
    )

    extraction_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_constructed_output,
        sys_msg_path='planning_team/extraction_agent#1.txt',
        node_func=create_extraction_node,
        node_name=EXTRACTION_NODE,
        oai_schema=result_extraction_scheme
    )

    graph = StateGraph(PlanningTeamState)

    graph.add_node(HEADER_NODE, header_node)
    graph.add_node(MSF_TESTER_NODE, msf_tester_node)
    graph.add_node(EXTRACTION_NODE, extraction_node)
    graph.add_node(NMAP_TESTER_NODE, nmap_tester_node)
    graph.add_node(EXECUTOR_NODE, execution_node)
    graph.add_node(ARGS_NODE, args_node)

    graph.add_edge(START, HEADER_NODE)

    graph.add_conditional_edges(
        HEADER_NODE,
        router_header_node,
        {
            "__end__": EXTRACTION_NODE,
            "continue": HEADER_NODE,
            ARGS_NODE: ARGS_NODE,
            MSF_TESTER_NODE: MSF_TESTER_NODE,
            NMAP_TESTER_NODE: NMAP_TESTER_NODE
        }
    )

    graph.add_conditional_edges(
        ARGS_NODE,
        router_args_node,
        {
            HEADER_NODE: HEADER_NODE,
            EXECUTOR_NODE: EXECUTOR_NODE
        }
    )

    graph.add_edge(MSF_TESTER_NODE, EXECUTOR_NODE)
    graph.add_edge(NMAP_TESTER_NODE, HEADER_NODE)

    graph.add_conditional_edges(
        EXECUTOR_NODE,
        router_execution_node,
        {
            HEADER_NODE: HEADER_NODE,
            ARGS_NODE: ARGS_NODE
        }
    )

    graph.add_edge(EXTRACTION_NODE, END)

    return graph
