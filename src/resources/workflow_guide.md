# Workflow Guide

## 10-Step Development Workflow

1. Select Issue (Jira) → 2. Transition to IN PROGRESS → 3. Create Branch (feature/ISSUE-KEY) → 4. Write Code → 5. Commit & Push → 6. Create PR → 7. Transition to IN REVIEW → 8. Wait for Approval → 9. Merge to Main → 10. Mark as DONE

---

## Available Tools

**Jira:** `jira_get_issue()` | `jira_search_issues()` | `jira_get_my_issues()` | `jira_transition_issue()`

**GitHub:** `create_branch_for_issue()` | `create_pull_request()` | `git_commit_and_push()` | `merge_pull_request()`

---

## Jira Statuses & Actions

| Status | Next Action |
|--------|------------|
| **To Do** | Transition to IN PROGRESS |
| **In Progress** | Create branch & write code |
| **In Review** | Wait for approval |
| **Done** | Archive issue |

---

## Branch Naming

`feature/ISSUE-KEY` (e.g., feature/KAN-1) | `bugfix/ISSUE-KEY` | `hotfix/ISSUE-KEY`

---

## Key Tips

Always transition status in Jira | Use meaningful commits | Review before PR | Wait for approval | Mark DONE when complete
