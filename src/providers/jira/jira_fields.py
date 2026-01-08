"""
Jira Fields Configuration
Defines default fields for list and detailed issue views.
"""

LIST_DEFAULT_FIELDS = [
    "summary",
    "status",
    "priority",
    "updated",
    "assignee",
    "duedate",
]

ISSUE_DEFAULT_FIELDS = [
    "summary",
    "description",
    "issuetype",
    "status",
    "priority",
    "assignee",
    "reporter",
    "duedate",
    "created",
    "updated",
    "subtasks"
]

FIELDS_PRESETS = {
    "list": LIST_DEFAULT_FIELDS,
    "issue": ISSUE_DEFAULT_FIELDS,
}


