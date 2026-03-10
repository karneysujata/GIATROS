"""Jira REST API client for fetching stories."""

import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    """Client for interacting with the Jira REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("JIRA_BASE_URL", "")).rstrip("/")
        self.email = email or os.environ.get("JIRA_EMAIL", "")
        self.api_token = api_token or os.environ.get("JIRA_API_TOKEN", "")
        self._auth = HTTPBasicAuth(self.email, self.api_token)
        self._headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self.base_url}/rest/api/3/{path}"
        response = requests.get(url, auth=self._auth, headers=self._headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_story(self, issue_key: str) -> dict:
        """Fetch a single Jira issue by its key (e.g. 'PROJ-123')."""
        return self._get(f"issue/{issue_key}")

    def list_stories(self, project_key: str | None = None, max_results: int = 50) -> list[dict]:
        """List stories (issue type 'Story') in a project."""
        project = project_key or os.environ.get("JIRA_PROJECT_KEY", "")
        jql = f"project = {project} AND issuetype = Story ORDER BY created DESC" if project else "issuetype = Story ORDER BY created DESC"
        return self.search_stories(jql, max_results=max_results)

    def search_stories(self, jql: str, max_results: int = 50) -> list[dict]:
        """Search Jira issues using a JQL query."""
        data = self._get(
            "search",
            params={"jql": jql, "maxResults": max_results, "fields": "summary,status,assignee,priority,description"},
        )
        return data.get("issues", [])

    @staticmethod
    def format_story(issue: dict) -> str:
        """Format a Jira issue dict as a human-readable string."""
        key = issue.get("key", "N/A")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "N/A")
        status = (fields.get("status") or {}).get("name", "N/A")
        priority = (fields.get("priority") or {}).get("name", "N/A")
        assignee_obj = fields.get("assignee") or {}
        assignee = assignee_obj.get("displayName", "Unassigned")
        description_obj = fields.get("description") or {}
        description = ""
        if isinstance(description_obj, dict):
            content = description_obj.get("content", [])
            texts = []
            for block in content:
                for item in block.get("content", []):
                    if item.get("type") == "text":
                        texts.append(item.get("text", ""))
            description = " ".join(texts).strip()
        elif isinstance(description_obj, str):
            description = description_obj.strip()

        lines = [
            f"Key: {key}",
            f"Summary: {summary}",
            f"Status: {status}",
            f"Priority: {priority}",
            f"Assignee: {assignee}",
        ]
        if description:
            lines.append(f"Description: {description}")
        return "\n".join(lines)
