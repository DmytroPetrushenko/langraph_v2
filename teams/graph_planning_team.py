from graph_entities.graphs import *
from graph_entities.nodes import *
from graph_entities.routers import *
from graph_entities.schemes import *
from graph_entities.statets import *
from tools.msf_tools import *
from tools.nmap_tools import *

TESTER_TOOLS = [tool_based_on_metasploit, tool_based_on_nmap]


def create_host_planner_graph(model_llm: Optional[Union[ChatOpenAI, ChatAnthropic, Callable]] = None):
    nodes_fabric = NodesFabric(model_llm=model_llm)

    gpt_4o_mini = utils.llm.create_llm('gpt-4o-mini')
    gpt_4o = utils.llm.create_llm('gpt-4o-2024-08-06')

    msf_tools_team = nodes_fabric.create_team_node(
        graph_func=create_msf_tools_team_graph,
        node_func=connector_to_tools_team_node,
        name=TOOLS_TEAM
    )

    planning_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_without_tools,
        model_llm=gpt_4o,
        sys_msg_path='planning_team/plan_composition_agent#2.txt',
        node_func=create_ordinary_node,
        node_name=PLAN_COMPOSITION_NODE,
        tools=TESTER_TOOLS
    )

    extraction_node = nodes_fabric.create_graph_node(
        agent_func=assistant_agent_with_constructed_output,
        model_llm=gpt_4o,
        sys_msg_path='planning_team/extraction_agent#1.txt',
        node_func=create_extraction_node,
        node_name=EXTRACTION_NODE,
        oai_schema=plan_extraction_scheme
    )

    graph = StateGraph(PlanningTeamState)

    graph.add_node(PLAN_COMPOSITION_NODE, planning_node)
    graph.add_node(EXTRACTION_NODE, extraction_node)
    graph.add_node(TOOLS_TEAM, msf_tools_team)

    graph.add_edge(START, PLAN_COMPOSITION_NODE)
    graph.add_conditional_edges(
        PLAN_COMPOSITION_NODE,
        router_planing_team,
        {
            EXTRACTION_NODE: EXTRACTION_NODE,
            TOOLS_TEAM: TOOLS_TEAM
        }
    )
    graph.add_edge(TOOLS_TEAM, PLAN_COMPOSITION_NODE)
    graph.add_edge(EXTRACTION_NODE, END)

    return graph
