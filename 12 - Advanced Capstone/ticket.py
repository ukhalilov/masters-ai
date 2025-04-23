# ticket.py

import requests

def create_github_issue(token, repo_owner, repo_name, title, body):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "title": title,
        "body": body
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()
