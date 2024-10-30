import re

from constants import *
from graph_entities.statets import PlanningTeamState

FINAL_ANSWER_PATTERN = re.compile(FINAL_ANSWER)
ARGS_AGENT_PATTERN = re.compile(f'\\*\\*{ARGS_AGENT}\\*\\*')
NMAP_TESTER_AGENT_PATTERN = re.compile(f'\\*\\*{NMAP_TESTER_AGENT}\\*\\*')
MSF_TESTER_AGENT_PATTERN = re.compile(f'\\*\\*{MSF_TESTER_AGENT}\\*\\*')
PLANNER_TEAM_PATTERN = re.compile(f'{PLANNER_AGENT}')
TESTER_TEAM_PATTERN = re.compile(f'{TESTER_AGENT}')
CHOOSER_NODE_PATTERN = re.compile(f'{CHOOSER_NODE}')



def router_planing_team(state: PlanningTeamState):
    last_message = state.messages[-1]

    if re.findall(r'Tools Agent', last_message.content):
        return TOOLS_TEAM

    return EXTRACTION_NODE


def router_header_node(state: PlanningTeamState):
    last_message = state.messages[-1]

    if re.findall(FINAL_ANSWER_PATTERN, last_message.content):
        return "__end__"

    if re.findall(NMAP_TESTER_AGENT_PATTERN, last_message.content):
        return NMAP_TESTER_NODE

    if re.findall(MSF_TESTER_AGENT_PATTERN, last_message.content):
        return MSF_TESTER_NODE

    if re.findall(ARGS_AGENT_PATTERN, last_message.content):
        return ARGS_NODE

    return "continue"


def router_args_node(state: PlanningTeamState):
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return EXECUTOR_NODE

    return HEADER_NODE


def router_execution_node(state: PlanningTeamState):
    sender = state.sender[-2]

    if sender is ARGS_NODE:
        return ARGS_NODE

    return HEADER_NODE


def router_nmap_node(state: PlanningTeamState):
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return EXECUTOR_NODE

    if re.findall(FINAL_ANSWER_PATTERN, last_message.content):
        return "__end__"

    return 'continue'


def router_chooser_node(state: PlanningTeamState):
    last_message = state.messages[-1]

    if re.findall(FINAL_ANSWER_PATTERN, last_message.content):
        return "__end__"

    if re.search(PLANNER_TEAM_PATTERN, last_message.content):
        return PLANNER_NODE

    if re.findall(TESTER_TEAM_PATTERN, last_message.content):
        return TESTER_NODE

    if re.findall(CHOOSER_NODE_PATTERN, last_message.content):
        return CHOOSER_NODE

    raise ValueError(f"Nothing was chosen! -> {last_message.content}")
