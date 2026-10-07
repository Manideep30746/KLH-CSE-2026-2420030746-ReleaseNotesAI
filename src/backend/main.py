from fastapi import FastAPI, HTTPException
import httpx
import os
import asyncio
import json
from dotenv import load_dotenv
from urllib.parse import urlparse
from google import genai

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Primary Gemini model
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

# Fallback Gemini model
GEMINI_FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.7-flash"
)

# Number of retry attempts
GEMINI_MAX_RETRIES = 3


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="ReleaseNotesAI",
    description=(
        "AI-Powered Automated Release Notes "
        "and Changelog Generation"
    ),
    version="0.2.0"
)


# =========================================================
# GITHUB URL PARSER
# =========================================================

def parse_github_url(repo_url: str):

    parsed = urlparse(repo_url)

    if parsed.netloc.lower() != "github.com":
        raise ValueError(
            "Please provide a valid GitHub repository URL."
        )

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL."
        )

    owner = parts[0]
    repo = parts[1].replace(".git", "")

    return owner, repo


# =========================================================
# COMMIT CATEGORIZATION
# =========================================================

def categorize_commit(message: str):

    message_lower = message.lower()

    # -----------------------------
    # Bug Fix
    # -----------------------------

    if any(
        word in message_lower
        for word in [
            "fix",
            "bug",
            "error",
            "issue",
            "resolve",
            "patch"
        ]
    ):
        return "Bug Fix"

    # -----------------------------
    # Feature
    # -----------------------------

    if any(
        word in message_lower
        for word in [
            "add",
            "create",
            "implement",
            "introduce",
            "feature"
        ]
    ):
        return "Feature"

    # -----------------------------
    # Enhancement
    # -----------------------------

    if any(
        word in message_lower
        for word in [
            "update",
            "improve",
            "enhance",
            "refactor",
            "optimize"
        ]
    ):
        return "Enhancement"

    # -----------------------------
    # Maintenance
    # -----------------------------

    return "Maintenance"


# =========================================================
# FETCH COMMITS FROM GITHUB
# =========================================================

async def fetch_commits(repo_url: str):

    # -----------------------------
    # Parse repository URL
    # -----------------------------

    try:

        owner, repo = parse_github_url(
            repo_url
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # -----------------------------
    # GitHub API URL
    # -----------------------------

    github_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits"
    )

    # -----------------------------
    # Request Headers
    # -----------------------------

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ReleaseNotesAI"
    }

    # Add GitHub token if configured
    if GITHUB_TOKEN:

        headers["Authorization"] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    # -----------------------------
    # Request GitHub API
    # -----------------------------

    try:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                github_url,
                params={
                    "per_page": 20
                },
                headers=headers,
                timeout=10
            )

        # -------------------------
        # Repository not found
        # -------------------------

        if response.status_code == 404:

            raise HTTPException(
                status_code=404,
                detail="GitHub repository not found."
            )

        # -------------------------
        # Other GitHub errors
        # -------------------------

        if response.status_code != 200:

            try:

                github_message = response.json().get(
                    "message",
                    "GitHub API request failed"
                )

            except Exception:

                github_message = (
                    "GitHub API request failed"
                )

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

        # -------------------------
        # Convert response to JSON
        # -------------------------

        data = response.json()

        commits = []

        # -------------------------
        # Process each commit
        # -------------------------

        for item in data:

            message = (
                item["commit"]["message"]
                .split("\n")[0]
            )

            commits.append(
                {
                    "sha": item["sha"][:7],

                    "message": message,

                    "author": (
                        item["commit"]
                        ["author"]
                        ["name"]
                    ),

                    "date": (
                        item["commit"]
                        ["author"]
                        ["date"]
                    ),

                    "category": categorize_commit(
                        message
                    )
                }
            )

        # -------------------------
        # Return processed commits
        # -------------------------

        return {
            "repository": f"{owner}/{repo}",

            "total_commits": len(
                commits
            ),

            "commits": commits
        }

    # -----------------------------
    # Connection error
    # -----------------------------

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to connect to GitHub."
            )
        )


# =========================================================
# HOME ENDPOINT
# =========================================================

@app.get("/")
def home():

    return {
        "message": (
            "ReleaseNotesAI backend "
            "is running!"
        ),

        "version": "0.2.0",

        "ai_enabled": (
            gemini_client is not None
        )
    }


# =========================================================
# GET COMMITS ENDPOINT
# =========================================================

@app.get("/api/commits")
async def get_commits(
    repo_url: str
):

    return await fetch_commits(
        repo_url
    )


# =========================================================
# GENERATE AI RELEASE NOTES
# =========================================================

async def generate_release_notes(
    commits_data
):

    # -----------------------------
    # Check Gemini configuration
    # -----------------------------

    if gemini_client is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Gemini API key is not configured. "
                "Please add GEMINI_API_KEY "
                "to the .env file."
            )
        )

    # -----------------------------
    # Extract repository information
    # -----------------------------

    repository = commits_data[
        "repository"
    ]

    commits = commits_data[
        "commits"
    ]

    # -----------------------------
    # Convert commits to JSON
    # -----------------------------

    commits_json = json.dumps(
        commits,
        indent=2
    )

    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are an expert software release-note generator.

Your task is to generate professional,
concise, and human-readable release notes
from Git commit history.

Repository:
{repository}

Commit history:
{commits_json}

Instructions:

1. Analyze the commit messages carefully.

2. Do not invent features, fixes, or changes
   that are not supported by the commit messages.

3. Group related changes logically.

4. Use these categories when appropriate:

   - Features
   - Bug Fixes
   - Enhancements
   - Maintenance

5. Ignore meaningless repetition.

6. Keep the release notes concise but informative.

7. Mention important technical changes clearly.

8. Do not mention that an AI generated
   the release notes.

9. Use Markdown formatting.

10. If a category has no meaningful changes,
    do not include that category.

Return the release notes using this structure:

# Release Notes

## Overview

A short 2-3 sentence summary of the changes.

## Features

- Important new features.

## Bug Fixes

- Important bug fixes.

## Enhancements

- Improvements and refactoring.

## Maintenance

- Maintenance and configuration changes.

## Summary

A short concluding summary.

Only include sections that have
relevant information.
"""

    # =====================================================
    # MODELS TO TRY
    # =====================================================

    models_to_try = [
        GEMINI_MODEL,
        GEMINI_FALLBACK_MODEL
    ]

    last_error = None

    # =====================================================
    # TRY PRIMARY + FALLBACK MODELS
    # =====================================================

    for model in models_to_try:

        # Avoid trying the same model twice
        if (
            model != GEMINI_MODEL
            and model == GEMINI_FALLBACK_MODEL
            and GEMINI_FALLBACK_MODEL == GEMINI_MODEL
        ):
            continue

        # -----------------------------------------------
        # Retry temporary errors
        # -----------------------------------------------

        for attempt in range(
            1,
            GEMINI_MAX_RETRIES + 1
        ):

            try:

                print(
                    "\n"
                    "===================================="
                )

                print(
                    "Gemini Request"
                )

                print(
                    f"Model: {model}"
                )

                print(
                    f"Attempt: "
                    f"{attempt}/"
                    f"{GEMINI_MAX_RETRIES}"
                )

                print(
                    "===================================="
                )

                # ---------------------------------------
                # Gemini SDK call
                # ---------------------------------------

                response = await asyncio.to_thread(
                    gemini_client
                    .models
                    .generate_content,

                    model=model,

                    contents=prompt
                )

                # ---------------------------------------
                # Get generated text
                # ---------------------------------------

                generated_text = (
                    response.text
                )

                # ---------------------------------------
                # Successful response
                # ---------------------------------------

                if generated_text:

                    print(
                        "\n"
                        "Gemini generation "
                        "successful!"
                    )

                    print(
                        f"Model used: {model}"
                    )

                    return generated_text

                # Empty response
                last_error = (
                    "Gemini returned "
                    "an empty response."
                )

                print(
                    last_error
                )

            except Exception as error:

                last_error = str(error)

                print(
                    "\nGemini error:"
                )

                print(
                    last_error
                )

                error_text = (
                    str(error)
                    .lower()
                )

                # ---------------------------------------
                # Detect temporary errors
                # ---------------------------------------

                temporary_error = any(
                    keyword in error_text
                    for keyword in [
                        "503",
                        "unavailable",
                        "overloaded",
                        "high demand",
                        "429",
                        "resource exhausted"
                    ]
                )

                # ---------------------------------------
                # Temporary error → retry
                # ---------------------------------------

                if temporary_error:

                    if (
                        attempt
                        < GEMINI_MAX_RETRIES
                    ):

                        # Exponential backoff:
                        #
                        # attempt 1 → 2 seconds
                        # attempt 2 → 4 seconds

                        wait_time = (
                            2 ** attempt
                        )

                        print(
                            "\n"
                            "Gemini is temporarily "
                            "unavailable."
                        )

                        print(
                            f"Retrying in "
                            f"{wait_time} seconds..."
                        )

                        await asyncio.sleep(
                            wait_time
                        )

                    continue

                # ---------------------------------------
                # Permanent error
                # ---------------------------------------

                print(
                    "\n"
                    "Non-temporary Gemini "
                    "error detected."
                )

                print(
                    "Moving to fallback model..."
                )

                break

    # =====================================================
    # ALL ATTEMPTS FAILED
    # =====================================================

    raise HTTPException(
        status_code=502,
        detail={
            "message": (
                "Gemini AI request failed "
                "after retries."
            ),

            "primary_model": (
                GEMINI_MODEL
            ),

            "fallback_model": (
                GEMINI_FALLBACK_MODEL
            ),

            "error": last_error
        }
    )


# =========================================================
# RELEASE NOTES ENDPOINT
# =========================================================

@app.get("/api/release-notes")
async def get_release_notes(
    repo_url: str
):

    # ---------------------------------------------
    # Step 1: Fetch GitHub commits
    # ---------------------------------------------

    commits_data = await fetch_commits(
        repo_url
    )

    # ---------------------------------------------
    # Step 2: Generate release notes
    # ---------------------------------------------

    release_notes = (
        await generate_release_notes(
            commits_data
        )
    )

    # ---------------------------------------------
    # Step 3: Return final result
    # ---------------------------------------------

    return {
        "repository": (
            commits_data[
                "repository"
            ]
        ),

        "commits_analyzed": (
            commits_data[
                "total_commits"
            ]
        ),

        "model": GEMINI_MODEL,

        "release_notes": release_notes
    }