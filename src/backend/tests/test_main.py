
import pytest
from fastapi.testclient import TestClient

from main import app, parse_github_url, categorize_commit, validate_release_notes


client = TestClient(app)


def test_parse_valid_github_url():
    owner, repo = parse_github_url(
        "https://github.com/example/project"
    )
    assert owner == "example"
    assert repo == "project"


def test_parse_github_url_with_git_extension():
    owner, repo = parse_github_url(
        "https://github.com/example/project.git"
    )
    assert owner == "example"
    assert repo == "project"


def test_reject_invalid_github_url():
    with pytest.raises(ValueError):
        parse_github_url("https://example.com/project")


def test_categorize_bug_fix():
    assert categorize_commit("Fix login error") == "Bug Fix"


def test_categorize_feature():
    assert categorize_commit("Add user registration") == "Feature"


def test_categorize_enhancement():
    assert categorize_commit("Improve dashboard layout") == "Enhancement"


def test_categorize_maintenance():
    assert categorize_commit("Update README documentation") == "Enhancement"


def test_validate_release_notes():
    notes = {
        "version": "v2.0.0",
        "overview": "Added a new feature.",
        "features": ["User registration"],
        "bug_fixes": [],
        "enhancements": [],
        "maintenance": [],
        "summary": "Added user registration."
    }

    result = validate_release_notes(notes)

    assert result["version"] == "v1.0.0"
    assert result["features"] == ["User registration"]


def test_reject_missing_release_note_field():
    notes = {
        "version": "v1.0.0",
        "overview": "Test overview",
        "features": [],
        "bug_fixes": [],
        "enhancements": [],
        "maintenance": []
    }

    with pytest.raises(ValueError):
        validate_release_notes(notes)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ReleaseNotesAI backend is running!"


def test_invalid_repository_returns_400():
    response = client.get(
        "/api/commits",
        params={"repo_url": "https://example.com/owner/repository"}
    )
    assert response.status_code == 400
