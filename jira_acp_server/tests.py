"""Tests for the Jira ACP server."""

import json
from unittest.mock import MagicMock, patch

import pytest

from jira_acp_server.jira_client import JiraClient


# ---------------------------------------------------------------------------
# JiraClient.format_story tests
# ---------------------------------------------------------------------------

SAMPLE_ISSUE = {
    "key": "PROJ-1",
    "fields": {
        "summary": "As a user, I can log in",
        "status": {"name": "In Progress"},
        "priority": {"name": "High"},
        "assignee": {"displayName": "Alice"},
        "description": {
            "content": [
                {"content": [{"type": "text", "text": "Implement login form."}]}
            ]
        },
    },
}


def test_format_story_all_fields():
    result = JiraClient.format_story(SAMPLE_ISSUE)
    assert "PROJ-1" in result
    assert "As a user, I can log in" in result
    assert "In Progress" in result
    assert "High" in result
    assert "Alice" in result
    assert "Implement login form." in result


def test_format_story_missing_optional_fields():
    minimal = {"key": "MIN-1", "fields": {"summary": "Minimal story"}}
    result = JiraClient.format_story(minimal)
    assert "MIN-1" in result
    assert "Minimal story" in result
    assert "Unassigned" in result


def test_format_story_string_description():
    issue = {
        "key": "STR-1",
        "fields": {
            "summary": "String desc",
            "description": "Plain text description",
        },
    }
    result = JiraClient.format_story(issue)
    assert "Plain text description" in result


# ---------------------------------------------------------------------------
# JiraClient HTTP method tests
# ---------------------------------------------------------------------------

def _make_mock_response(payload: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.raise_for_status = MagicMock()
    return mock


@patch("jira_acp_server.jira_client.requests.get")
def test_get_story(mock_get):
    mock_get.return_value = _make_mock_response(SAMPLE_ISSUE)
    client = JiraClient(base_url="https://example.atlassian.net", email="u@example.com", api_token="tok")
    result = client.get_story("PROJ-1")
    assert result["key"] == "PROJ-1"
    mock_get.assert_called_once()
    call_url = mock_get.call_args[0][0]
    assert "issue/PROJ-1" in call_url


@patch("jira_acp_server.jira_client.requests.get")
def test_search_stories(mock_get):
    payload = {"issues": [SAMPLE_ISSUE]}
    mock_get.return_value = _make_mock_response(payload)
    client = JiraClient(base_url="https://example.atlassian.net", email="u@example.com", api_token="tok")
    issues = client.search_stories("project = PROJ")
    assert len(issues) == 1
    assert issues[0]["key"] == "PROJ-1"


@patch("jira_acp_server.jira_client.requests.get")
def test_list_stories_uses_project_key(mock_get):
    payload = {"issues": [SAMPLE_ISSUE]}
    mock_get.return_value = _make_mock_response(payload)
    client = JiraClient(base_url="https://example.atlassian.net", email="u@example.com", api_token="tok")
    issues = client.list_stories(project_key="PROJ")
    assert len(issues) == 1
    params = mock_get.call_args[1]["params"]
    assert "PROJ" in params["jql"]


@patch("jira_acp_server.jira_client.requests.get")
def test_list_stories_empty(mock_get):
    mock_get.return_value = _make_mock_response({"issues": []})
    client = JiraClient(base_url="https://example.atlassian.net", email="u@example.com", api_token="tok")
    assert client.list_stories() == []


# ---------------------------------------------------------------------------
# ACP agent logic tests (run agent coroutine directly)
# ---------------------------------------------------------------------------

async def _collect_agent_output(command: str) -> str:
    """Helper: run the jira_stories agent and collect all MessagePart content."""
    from acp_sdk.models import Message, MessagePart as MP

    from jira_acp_server.server import jira_stories

    messages = [Message(parts=[MP(content=command)])]
    parts = []
    async for part in jira_stories(messages):
        parts.append(part.content or "")
    return "\n".join(parts)


def test_agent_help():
    output = pytest.importorskip("asyncio").run(_collect_agent_output("help"))
    assert "jira_stories" in output.lower() or "commands" in output.lower()


def test_agent_unknown_command():
    output = pytest.importorskip("asyncio").run(_collect_agent_output("frobnicate"))
    assert "unknown" in output.lower() or "help" in output.lower()


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_list_command(mock_get):
    mock_get.return_value = _make_mock_response({"issues": [SAMPLE_ISSUE]})
    import asyncio
    output = asyncio.run(_collect_agent_output("list PROJ"))
    assert "PROJ-1" in output


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_get_command(mock_get):
    mock_get.return_value = _make_mock_response(SAMPLE_ISSUE)
    import asyncio
    output = asyncio.run(_collect_agent_output("get PROJ-1"))
    assert "As a user, I can log in" in output


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_search_command(mock_get):
    mock_get.return_value = _make_mock_response({"issues": [SAMPLE_ISSUE]})
    import asyncio
    output = asyncio.run(_collect_agent_output("search project = PROJ AND issuetype = Story"))
    assert "PROJ-1" in output


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_get_missing_arg(mock_get):
    import asyncio
    output = asyncio.run(_collect_agent_output("get"))
    assert "usage" in output.lower() or "get" in output.lower()


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_search_missing_arg(mock_get):
    import asyncio
    output = asyncio.run(_collect_agent_output("search"))
    assert "usage" in output.lower() or "search" in output.lower()


@patch("jira_acp_server.jira_client.requests.get")
def test_agent_list_empty(mock_get):
    mock_get.return_value = _make_mock_response({"issues": []})
    import asyncio
    output = asyncio.run(_collect_agent_output("list"))
    assert "no stories" in output.lower()
