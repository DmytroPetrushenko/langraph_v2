from constants import *

planning_team_state_schema = {
    "title": "PlanningTeamState",
    "description": "A structured output representing the state of a planning team.",
    "type": "object",
    "properties": {
        MESSAGES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Messages exchanged within the team during the planning process."
        },
        SENDER_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of senders participating in the communication."
        },
        PLAN_FIELD: {
            "type": "string",
            "description": "A comprehensive security testing plan."
        },
        GROUPS_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of subgroups used in the security testing process."
        },
        MODULES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of modules selected for the security testing process."
        }
    },
    "required": [MESSAGES_FIELD, SENDER_FIELD, PLAN_FIELD, GROUPS_FIELD, MODULES_FIELD]
}


group_extraction_scheme = {
    "title": "module_extraction_scheme",
    "description": "A structured output representing selected Metasploit module groups and specific modules for the "
                   "state of a testing team.",
    "type": "object",
    "properties": {
        GROUPS_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "A list of selected Metasploit module groups that are relevant for the testing task."
        }
    },
    "required": [GROUPS_FIELD]
}

module_extraction_scheme = {
    "title": "module_extraction_scheme",
    "description": "A structured output representing selected Metasploit module groups and specific modules for the "
                   "state of a testing team.",
    "type": "object",
    "properties": {
        MODULES_FIELD: {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Extract here all metasploit modules from the messages."
        }
    },
    "required": [MODULES_FIELD]
}
plan_extraction_scheme = {
    "title": "plan_extraction_scheme",
    "description": "A field representing the final security testing plan.",
    "type": "object",
    "properties": {
        PLAN_FIELD: {
            "type": "string",
            "description": "The final security testing plan."
        }
    },
    "required": [PLAN_FIELD]
}

validator_feedback_scheme = {
    "title": "validator_feedback_schema",
    "description": "This schema defines the structure of feedback provided by the validator team after reviewing the "
                   "security testing plan.",
    "type": "object",
    "properties": {
        VALIDATOR_FIELD: {
            "type": "string",
            "description": (
                "The validator's feedback on the testing plan. This field contains either: "
                "1) A list of remarks for steps that need improvement, labeled as <Needs improvement>, "
                "with explanations for what can be improved in the context of automated testing; or "
                "2) The phrase 'The plan is good' if no issues were found."
            )
        }
    },
    "required": [VALIDATOR_FIELD]
}

result_extraction_scheme = {
    "title": "result_extraction_scheme",
    "description": "A scheme representing the structure for extracting the final security testing result.",
    "type": "object",
    "properties": {
        RESULT_FIELD: {
            "type": "string",
            "description": "The final result of the security testing process."
        }
    },
    "required": [RESULT_FIELD]
}

