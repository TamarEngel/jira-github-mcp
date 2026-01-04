"""
Development Workflow Prompts
"""

from typing import Optional
from mcp.types import TextContent


# def get_workflow_guidance(step: str = "start", issue_key: Optional[str] = None) -> str:
#     """Get workflow guidance for current step."""
    
#     workflows = {
#         "start": "Start workflow: Select Jira issue → Transition to IN PROGRESS → Create branch → Write code → Commit → PR → Review → Merge → Done",
        
#         "issue_selected": f"Issue selected. Options:\n- Transition: `jira_transition_issue(\"{issue_key}\", \"In Progress\")`\n- Create branch: `create_branch_for_issue(\"{issue_key}\")`",
        
#         "issue_selected_todo": f"Issue {issue_key} is in To Do. Next steps:\n- Transition: `jira_transition_issue(\"{issue_key}\", \"In Progress\")`\n- Then create branch: `create_branch_for_issue(\"{issue_key}\")`",
        
#         "issue_selected_in_progress": f"Issue {issue_key} is In Progress. Create branch: `create_branch_for_issue(\"{issue_key}\")`",
        
#         "status_in_progress": f"Good! Issue {issue_key} is In Progress. Next: Create branch: `create_branch_for_issue(\"{issue_key}\")`",
        
#         "branch_created": f"✅ Branch feature/{issue_key} created!\n**SWITCH TO IT NOW:** `git checkout feature/{issue_key}`\nThen write your code in that branch.",
        
#         "code_ready": f"Code ready. Commit and push: `git_commit_and_push(\"Your message\", \"{issue_key}\")`",
        
#         "committed_pushed": f"Changes on GitHub. Create PR: `create_pull_request(\"{issue_key}\", \"feature/{issue_key}\")`",
        
#         "pr_created": f"PR open. Transition issue: `jira_transition_issue(\"{issue_key}\", \"In Review\")`",
        
#         "status_in_review": f"Issue {issue_key} In Review. Waiting for approval.",
        
#         "pr_approved": f"PR approved. Ready to merge: `merge_pull_request(PR_NUMBER)`",
        
#         "merged": f"Merged to main. Mark done: `jira_transition_issue(\"{issue_key}\", \"Done\")`",
        
#         "status_done": f"Done! Issue {issue_key} complete."
#     }
    
#     return workflows.get(step, workflows["start"])

def get_workflow_guidance(step: str = "start", issue_key: Optional[str] = None) -> str:
    """
    Safe workflow guidance:
    - Only git checkout CLI is allowed (no add/commit/push CLI ever)
    - No automatic next-step pushing
    - Ask user every step
    - Suggest tools only after user chooses
    """
    ik = issue_key or "<ISSUE_KEY>"

    workflows = {
        "start": (
            "Start\n"
            "Choose what you want to do now:\n"
            "1) Enter/select a Jira issue key (e.g., KAN-18)\n"
            "2) List my assigned issues (if you have such a tool)\n\n"
            "What do you choose? (1/2)"
        ),

        "issue_selected": (
            f"Selected issue: {ik}\n\n"
            "Before suggesting actions, we must check the current state.\n"
            "What do you want to check now?\n"
            "1) Jira issue status\n"
            "2) Whether a branch already exists for this issue\n"
            "3) Whether an open PR already exists for this issue\n\n"
            "Reply 1/2/3."
        ),

        "issue_status_todo": (
            f"Issue {ik} is in To Do.\n\n"
            "What do you want to do now?\n"
            "1) Move the issue to In Progress\n"
            "2) Check whether a branch already exists\n"
            "3) Create a new branch (without changing status)\n"
            "4) Stop here\n\n"
            "Reply 1/2/3/4."
        ),

        "issue_status_in_progress": (
            f"Issue {ik} is already In Progress.\n"
            "I will not suggest a status transition.\n\n"
            "What do you want to do now?\n"
            "1) Check whether a branch already exists\n"
            "2) Create a new branch\n"
            "3) Start/continue coding (no tools, just guidance)\n"
            "4) Check whether an open PR exists\n"
            "5) Stop here\n\n"
            "Reply 1/2/3/4/5."
        ),

        "issue_status_in_review": (
            f"Issue {ik} is in In Review.\n\n"
            "What do you want to do?\n"
            "1) Check the open PR and its status\n"
            "2) Check whether the PR is ready to merge to main\n"
            "3) Move back to In Progress (only if changes are needed)\n"
            "4) Stop here\n\n"
            "Reply 1/2/3/4."
        ),

        "issue_status_done": (
            f"Issue {ik} is already Done.\n\n"
            "What do you want to do?\n"
            "1) Show details only\n"
            "2) Choose another issue\n"
            "3) Stop here\n\n"
            "Reply 1/2/3."
        ),

        "branch_exists": (
            f"A branch already exists for {ik}.\n\n"
            "What do you want to do?\n"
            "1) Continue working on the existing branch\n"
            "2) Check whether an open PR exists\n"
            "3) Stop here\n\n"
            "Reply 1/2/3."
        ),

        "branch_not_exists": (
            f"No branch found for {ik}.\n\n"
            "Do you want to create a new branch?\n"
            "1) Yes — I will suggest the tool create_branch_for_issue\n"
            "2) No — stop here\n\n"
            "Reply 1/2."
        ),

        "branch_created": (
            f"Branch created: feature/{ik}\n\n"
            "CLI exception (allowed because there is no tool for it):\n"
            f"`git checkout feature/{ik}`\n\n"
            "Question: did you switch to that branch successfully?\n"
            "1) Yes\n"
            "2) No\n\n"
            "Reply 1/2."
        ),

        "coding": (
            "Coding phase\n\n"
            "When you're ready to push changes, tell me: 'code is ready'.\n"
            "Reminder: I will never suggest or run git add/commit/push via CLI."
        ),

        "code_ready": (
            f"You said the code is ready for {ik}.\n\n"
            "Important: I must NOT suggest or run CLI git add/commit/push.\n"
            "We can only do it via the tool git_commit_and_push(...) and ONLY after your explicit 'Yes'.\n\n"
            "Do you want to run Commit + Push now using the tool?\n"
            "1) Yes — I will suggest: git_commit_and_push(\"message\", \"{ik}\")\n"
            "2) No — stop here\n\n"
            "Reply 1/2."
        ),

        "after_push": (
            f"Push completed for {ik}.\n\n"
            "Before creating a PR, we must check whether an open PR already exists.\n"
            "What do you want to do?\n"
            "1) Check for an existing open PR\n"
            "2) Create a new PR (only if you're sure none exists)\n"
            "3) Stop here\n\n"
            "Reply 1/2/3."
        ),

        "pr_exists": (
            f"An open PR already exists for {ik}.\n\n"
            "What do you want to do?\n"
            "1) Show PR details only\n"
            "2) Update the PR (usually requires another commit/push — only if you want)\n"
            "3) Stop here\n\n"
            "Reply 1/2/3."
        ),

        "pr_not_exists": (
            f"No open PR found for {ik}.\n\n"
            "Do you want to create a PR?\n"
            "1) Yes — I will suggest the tool create_pull_request\n"
            "2) No — stop here\n\n"
            "Reply 1/2."
        ),

        "pr_created": (
            f"PR created for {ik}.\n\n"
            "I will NOT suggest merge automatically.\n"
            "What do you want to do now?\n"
            "1) Move the issue to In Review\n"
            "2) Keep the issue status as-is\n"
            "3) Stop here\n\n"
            "Reply 1/2/3."
        ),

        "merge_question": (
            f"Merge discussion for {ik}.\n\n"
            "I will never merge without explicit confirmation.\n"
            "Do you want to merge now?\n"
            "1) Yes — I will suggest merge_pull_request\n"
            "2) No — keep the PR open\n\n"
            "Reply 1/2."
        ),
    }

    return workflows.get(step, workflows["start"])


def register(mcp) -> None:
    """Register workflow prompts with FastMCP"""
    
    @mcp.prompt(name="dev_workflow_guide")
    def workflow_guide(step: str = "start", issue_key: str = None) -> list[TextContent]:
        """Smart workflow guidance for development."""
        guidance = get_workflow_guidance(step, issue_key)
        
        system_msg = """You are a smart development assistant helping a developer with their workflow.
You are an MCP workflow assistant for Jira + GitHub. Your job is to guide the user step-by-step with strict control.

NON-NEGOTIABLE RULES:
1) Never execute actions without explicit user confirmation. Always ask first and wait for the user's answer.
2) CLI exception: You MAY suggest only this manual command because there is no tool for it:
   - git checkout <branch>
3) You MUST NOT suggest or run CLI for:
   - git add / git commit / git push
   Instead, you MUST use ONLY the tool: git_commit_and_push(...)
   And ONLY after the user explicitly says "Yes".
4) Before suggesting any action, you must check the current state (via tools when possible):
   - Before creating a branch: check Jira status AND whether a branch already exists
   - Before creating a PR: check whether an open PR already exists
   - Before merge: ask the user if they want to merge (never assume)
5) Do not “rush” the workflow. Each step must end with:
   - Findings / current state
   - 2-5 numbered options
   - A single question asking the user to choose
   - STOP and wait (do not call tools before the user chooses)
6) If uncertain, stop and ask.

Response format you should follow:
- What you found / what was checked
- Options (numbered)
- One question for the users choice
- No tool execution before the users reply

"""
        
        return [
            TextContent(type="text", text=system_msg, anotations={"role": "system"}),
            TextContent(type="text", text=guidance)
        ]
