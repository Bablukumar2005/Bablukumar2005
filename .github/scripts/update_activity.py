import os
import requests
import re
from datetime import datetime

USERNAME = "Bablukumar2005"
API_URL = f"https://api.github.com/users/{USERNAME}/events/public"

headers = {"Accept": "application/vnd.github.v3+json"}
if "GITHUB_TOKEN" in os.environ:
    headers["Authorization"] = f"token {os.environ['GITHUB_TOKEN']}"

try:
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    events = response.json()
except Exception as e:
    print(f"Error fetching data: {e}")
    exit(1)

activity_lines = []
MAX_LINES = 7

if isinstance(events, list):
    for event in events:
        if len(activity_lines) >= MAX_LINES:
            break
            
        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "unknown")
        repo_url = f"https://github.com/{repo_name}"
        repo_link = f"[{repo_name}]({repo_url})"
        
        if event_type == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            commit_count = len(commits)
            if commit_count > 0:
                activity_lines.append(f"- 🚀 Pushed **{commit_count}** commit(s) to **{repo_link}**")
        elif event_type == "WatchEvent":
            activity_lines.append(f"- ⭐ Starred **{repo_link}**")
        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "")
            issue = event.get("payload", {}).get("issue", {})
            issue_num = issue.get("number")
            issue_url = issue.get("html_url", "")
            activity_lines.append(f"- ❗ {action.capitalize()} issue [#{issue_num}]({issue_url}) in **{repo_link}**")
        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "")
            pr = event.get("payload", {}).get("pull_request", {})
            pr_num = pr.get("number")
            pr_url = pr.get("html_url", "")
            activity_lines.append(f"- 🔁 {action.capitalize()} PR [#{pr_num}]({pr_url}) in **{repo_link}**")
        elif event_type == "CreateEvent":
            ref_type = event.get("payload", {}).get("ref_type", "")
            if ref_type == "repository":
                activity_lines.append(f"- 📦 Created repository **{repo_link}**")
            elif ref_type == "branch":
                branch = event.get("payload", {}).get("ref", "")
                activity_lines.append(f"- 🌿 Created branch `{branch}` in **{repo_link}**")

activity_content = "\n".join(activity_lines) if activity_lines else "- No recent public activity found."

try:
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"(<!--START_SECTION:activity-->\n).*?(\n<!--END_SECTION:activity-->)"
    new_readme = re.sub(pattern, f"\\g<1>{activity_content}\\g<2>", readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
        
    print("README.md updated successfully.")
except Exception as e:
    print(f"Error updating README: {e}")
    exit(1)
