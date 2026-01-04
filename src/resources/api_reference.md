# API Reference

## Jira Tools

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `jira_get_issue` | `issue_key` (required), `fields`, `raw` | Get issue details by key |
| `jira_search_issues` | `jql` (required), `max_results=10`,`next_page_token `,`fields`, `raw` | Search using JQL: `assignee=currentUser()`, `status="To Do"`, `duedate>=-7d` |
| `jira_get_my_issues` | `status`, `issue_type`, `max_results=50`,`fields`, `raw` | Get your assigned issues |
| `jira_transition_issue` | `issue_key` (required), `to_status` (required), `comment`, `raw` | Change issue status to: "To Do", "In Progress", "In Review", "Done" |

---

## GitHub Tools

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `create_branch_for_issue` | `issue_key` (required), `branch_name` | Create branch: feature/ISSUE-KEY |
| `create_pull_request` | `issue_key`, `branch_name` (required), `title`, `description` | Create PR linking to Jira issue |
| `git_commit_and_push` | `message` (required), `local_path`, `branch_name` | Stage, commit, push all changes |
| `merge_pull_request` | `pr_number` (required), `merge_method="squash"`, `check_status=true` | Merge PR after CI check |

---

## Return Format (All Tools)

**Success:**
```json
{ "success": true, "data": {...} }
```

**Error:**
```json
{ "success": false, "error": "Description" }
```

---

## Workflow Prompts

**dev_workflow_guide(step, issue_key):**
- Steps: `start`, `issue_selected_todo`, `status_in_progress`, `branch_created`, `code_ready`, `committed_pushed`, `pr_created`, `status_in_review`, `pr_approved`, `merged`, `status_done`
- Provides contextual guidance for each workflow step
