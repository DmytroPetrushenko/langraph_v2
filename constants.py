# agents names
INITIALIZER = 'initializer'
EXECUTOR = 'executor_exp'
PENTEST = 'pentest'
TEAM_LEAD = 'team_lead'
TASK_SUPERVISOR = 'task_supervisor'
HELPER = 'helper_agent'
EXAMPLE = 'example'

# path to msf modules names
REPLACEMENT_PRELIMINARY_MODULES = 'msf_modules/preliminary_modules.txt'
REPLACEMENT_AUXILIARY_MODULES = 'msf_modules/auxiliary_modules.txt'

# placeholders
TEXT_INSIDE_BRACES_PATTERN = r'\{(.*?)\}'

# others
PREFIX_REPLACEMENT = 'REPLACEMENT_'
DEFAULT_MESSAGE = 'default_message.txt'

PASSWORD = 'PASSWORD'
HOST = 'HOST'
PORT = 'PORT'
SSL = 'SSL'
FALSE = 'false'

# msf_tools.py constant
EXECUTION_COMPLETION_PHRASES = [
    'execution completed',
    'OptionValidateError',
    '[-] Unknown command: run.',
    '[*] Exploit completed, but no session was created.',
    '[*] Using code \'400\' as not found for',
    '[-] Unknown command:'
]
TIMEOUT = 600  # 10 minutes

# importing_msfinfo_database.py
DELETE_UNTIL = '#     Name'

# some flag
MOCK: bool = False
MOCK_MSF_TOOLS: bool = False

# database
TABLE_NAME: str | None = None

# file path
MESSAGE_FOLDER = 'messages'

# end key
FINAL_ANSWER = "FINAL ANSWER"

HOST_NAMES_LIST = ['RHOSTS', 'rhosts']

# host team
PLANNER_AGENT = 'Planner Team'
TESTER_AGENT = 'Tester Team'
HOST_NODE = 'host_node'
HOST_AGENT = 'host_agent'
CHOOSER_NODE = 'chooser_node'
PLANNER_TEAM = 'planner_team'
PLANNER_NODE = 'planner_node'
TESTER_TEAM = 'tester_team'
TESTER_NODE = 'tester_node'

# testing team
MSF_TESTER_AGENT = 'MSF Tester Agent'
NMAP_TESTER_AGENT = 'Nmap Tester Agent'
HEADER_AGENT = 'Header Agent'
ARGS_AGENT = 'Args Agent'

ARGS_NODE = 'args_node'
HEADER_NODE = 'header_node'
MSF_TESTER_NODE = 'msf_tester_node'
NMAP_TESTER_NODE = 'nmap_tester_node'

# planning distributed team
TOOLS_AGENT = 'TOOLS_TEAM'
GROUP_SELECTION_TEAM = 'group_selection_team'
TOOLS_TEAM = 'tools_team'
MODULE_SELECTION_TEAM = 'module_selection_team'
PLAN_COMPOSITION_TEAM = 'plan_composition_team'
VALIDATOR_TEAM = 'validator_team'

GROUP_SELECTION_NODE = 'group_selection_node'
MODULE_SELECTION_NODE = 'module_selection_node'
EXECUTOR_NODE = 'executor_node'

PLAN_COMPOSITION_NODE = 'plan_composition_node'
PLAN_EXTRACTION_NODE = 'plan_extraction_node'

PLAN_VALIDATOR_NODE = 'plan_validator_node'
EXTRACTION_NODE = 'extraction_node'

MODULE_EXTRACTION_NODE = 'module_extraction_node'

PROCESS_EVALUATION_NODE = 'process_evaluation_node'

names_mutation_dict = {
    GROUP_SELECTION_NODE: 'MODULE GROUP SELECTION AGENT',
    MODULE_SELECTION_NODE: 'MODULE SELECTION AGENT',
    PLAN_VALIDATOR_NODE: 'MODULE ORGANIZER AGENT',
    PLAN_COMPOSITION_NODE: 'PLAN COMPOSITION AGENT',
    EXECUTOR_NODE: 'TASK EXECUTION AGENT',
    PLAN_EXTRACTION_NODE: 'PLAN EXTRACTION AGENT'
}

GROUP_SELECTION_MSG_PATH = 'planning_team/module_group_selection_agent#1.txt'
MODULE_SELECTION_MSG_PATH = 'planning_team/module_selection_agent#1.txt'
EXTRACTION_MSG_PATH = 'planning_team/extraction_agent#1.txt'
PLAN_VALIDATOR_MSG_PATH = 'planning_team/plan_validator_agent#1.txt'
PLAN_COMPOSITION_MSG_PATH = 'planning_team/plan_composition_agent#1.txt'
MODULE_ORGANIZER_MSG_PATH = 'planning_team/plan_validator_agent#1.txt'
PROCESS_EVALUATION_MSG_PATH = 'planning_team/process_evaluation_agent#1.txt'




# Field names as constants
MESSAGES_FIELD = "messages"
SENDER_FIELD = "sender"
PLAN_FIELD = "plan"
RESULT_FIELD = "result"
GROUPS_FIELD = "sub_groups"
MODULES_FIELD = "modules"
VALIDATOR_FIELD = "validator_feedback"
CHOOSER_FIELD = "chooser_decision"
# for PlanningTeamState
TASK_FINISHED = 'The task was finished!'

PLAN_SAVED_MESSAGE = f'{TASK_FINISHED} The current plan was saved in "{PLAN_FIELD}" field in a state.'
MODULES_SAVED_MESSAGE = f'{TASK_FINISHED} The relevant modules were saved in "{MODULES_FIELD}" field in a state.'
GROUPS_SAVED_MESSAGE = f'{TASK_FINISHED} The relevant sub-groups were saved in "{GROUPS_FIELD}" field in a state.'
VALIDATOR_SAVED_MESSAGE = f'{TASK_FINISHED} The relevant feedback was saved in "{VALIDATOR_FIELD}" field in a state.'

