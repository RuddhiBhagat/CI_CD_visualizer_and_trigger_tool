import requests
from app.config import GITHUB_TOKEN

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_pipeline_runs(repo_full_name: str):
    url = f"https://api.github.com/repos/{repo_full_name}/actions/runs"
    response = requests.get(url, headers=headers)
    return response.json()
