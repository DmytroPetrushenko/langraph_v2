from graph_entities.statets import PlanningTeamState
from constants import *


def planner_team_conditions(
        state: PlanningTeamState,
        name: str  # the name of the current sub-graph node
):
    income_list = state.results
    result = []

    if PLANNER_TEAM == name and income_list:
        result.append('The results of previous testing:\n')

        # Use enumerate to get both index and result
        for num, income in enumerate(income_list):
            result.append(f'{num + 1} result: {income};\n')

        # Return the combined string
        return ''.join(result)

    return ""
