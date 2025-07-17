from fastapi import APIRouter
import os
import requests

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@router.get("/repos")
def get_user_repos():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Get authenticated user
    user_resp = requests.get("https://api.github.com/user", headers=headers)
    user_resp.raise_for_status()
    username = user_resp.json()["login"]

    # Get their repos
    repo_resp = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers)
    repo_resp.raise_for_status()
    return repo_resp.json()
