from fastapi import FastAPI, HTTPException
import httpx
import os
from dotenv import load_dotenv
from urllib.parse import urlparse


# Load environment variables from .env
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


app = FastAPI(
    title="ReleaseNotesAI",
    description="AI-Powered Automated Release Notes and Changelog Generation",
    version="0.1.0"
)


def parse_github_url(repo_url: str):
    """Extract owner and repository name from a GitHub URL."""

    parsed = urlparse(repo_url)

    if parsed.netloc.lower() != "github.com":
        raise ValueError("Please provide a valid GitHub repository URL.")

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")

    owner = parts[0]
    repo = parts[1].replace(".git", "")

    return owner, repo


def categorize_commit(message: str):
    """Basic rule-based commit categorization."""

    message_lower = message.lower()

    # Bug fixes
    if any(word in message_lower for word in [
        "fix", "bug", "error", "issue", "resolve", "patch"
    ]):
        return "Bug Fix"

    # New features
    if any(word in message_lower for word in [
        "add", "create", "implement", "introduce", "feature"
    ]):
        return "Feature"

    # Improvements
    if any(word in message_lower for word in [
        "update", "improve", "enhance", "refactor", "optimize"
    ]):
        return "Enhancement"

    # Everything else
    return "Maintenance"


@app.get("/")
def home():
    """Check whether the backend is running."""

    return {
        "message": "ReleaseNotesAI backend is running!",
        "version": "0.1.0"
    }


@app.get("/api/commits")
async def get_commits(repo_url: str):
    """Fetch recent commits from a GitHub repository."""

    # Step 1: Parse GitHub repository URL
    try:
        owner, repo = parse_github_url(repo_url)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # GitHub API endpoint
    github_url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    # Step 2: Prepare GitHub API headers
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ReleaseNotesAI"
    }

    # Add authentication token if available
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    # Step 3: Request commits from GitHub
    try:
        async with httpx.AsyncClient() as client:

            response = await client.get(
                github_url,
                params={"per_page": 20},
                headers=headers,
                timeout=10
            )

        # Repository not found
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="GitHub repository not found."
            )

        # Any other GitHub API error
        if response.status_code != 200:

            try:
                github_message = response.json().get(
                    "message",
                    "GitHub API request failed"
                )
            except Exception:
                github_message = "GitHub API request failed"

            remaining = response.headers.get(
                "x-ratelimit-remaining"
            )

            reset = response.headers.get(
                "x-ratelimit-reset"
            )

            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "github_message": github_message,
                    "rate_limit_remaining": remaining,
                    "rate_limit_reset": reset
                }
            )

        # Step 4: Convert GitHub response to JSON
        data = response.json()

        commits = []

        # Step 5: Process each commit
        for item in data:

            message = item["commit"]["message"].split("\n")[0]

            commits.append({
                "sha": item["sha"][:7],
                "message": message,
                "author": item["commit"]["author"]["name"],
                "date": item["commit"]["author"]["date"],
                "category": categorize_commit(message)
            })

        # Step 6: Return processed commits
        return {
            "repository": f"{owner}/{repo}",
            "total_commits": len(commits),
            "commits": commits
        }

    # GitHub connection error
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to GitHub."
        )