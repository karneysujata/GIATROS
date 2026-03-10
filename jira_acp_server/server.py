"""ACP server that exposes Jira stories as an AI agent.

The server registers a single agent named ``jira_stories`` that accepts
natural-language commands and returns Jira issue information.

Supported commands
------------------
- ``list [PROJECT_KEY]``        – list Story-type issues (optionally filtered by project)
- ``get ISSUE_KEY``             – fetch details of a single issue (e.g. ``get PROJ-42``)
- ``search JQL_QUERY``          – search issues with a JQL expression
- ``help``                      – show usage information

Environment variables
---------------------
JIRA_BASE_URL   Base URL of your Jira instance, e.g. https://mycompany.atlassian.net
JIRA_EMAIL      Jira user email for authentication
JIRA_API_TOKEN  Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens)
JIRA_PROJECT_KEY  Optional default project key used when listing stories
ACP_PORT        Port the ACP server listens on (default: 8000)
"""

import asyncio
import os
from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server

from .jira_client import JiraClient

HELP_TEXT = """\
Jira Stories ACP Agent
======================
Commands:
  list [PROJECT_KEY]   – List Story-type issues.  PROJECT_KEY overrides JIRA_PROJECT_KEY.
  get ISSUE_KEY        – Fetch details for a single issue (e.g. get PROJ-42).
  search JQL           – Search issues using a JQL query.
  help                 – Show this message.
"""

server = Server()


@server.agent(
    name="jira_stories",
    description="Fetches and exposes Jira stories via the Jira REST API.",
)
async def jira_stories(input: list[Message]) -> AsyncGenerator[MessagePart, None]:
    """ACP agent that exposes Jira stories."""
    command = ""
    for message in input:
        for part in message.parts:
            if part.content:
                command = part.content.strip()
                break
        if command:
            break

    client = JiraClient()

    try:
        if not command or command.lower() == "help":
            yield MessagePart(content=HELP_TEXT)
            return

        parts = command.split(None, 1)
        action = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if action == "list":
            project_key = arg or None
            issues = client.list_stories(project_key=project_key)
            if not issues:
                yield MessagePart(content="No stories found.")
                return
            noun = "story" if len(issues) == 1 else "stories"
            lines = [f"Found {len(issues)} {noun}:\n"]
            for issue in issues:
                lines.append(client.format_story(issue))
                lines.append("---")
            yield MessagePart(content="\n".join(lines))

        elif action == "get":
            if not arg:
                yield MessagePart(content="Usage: get ISSUE_KEY  (e.g. get PROJ-42)")
                return
            issue = client.get_story(arg.upper())
            yield MessagePart(content=client.format_story(issue))

        elif action == "search":
            if not arg:
                yield MessagePart(content="Usage: search JQL_QUERY  (e.g. search project = PROJ AND status = 'In Progress')")
                return
            issues = client.search_stories(arg)
            if not issues:
                yield MessagePart(content="No issues matched the query.")
                return
            lines = [f"Found {len(issues)} issue(s):\n"]
            for issue in issues:
                lines.append(client.format_story(issue))
                lines.append("---")
            yield MessagePart(content="\n".join(lines))

        else:
            yield MessagePart(content=f"Unknown command '{action}'. Send 'help' for usage.")

    except Exception as exc:  # noqa: BLE001
        yield MessagePart(content=f"Error: {exc}")


def main() -> None:
    """Entry point to start the ACP server."""
    port = int(os.environ.get("ACP_PORT", "8000"))
    asyncio.run(server.serve(port=port))


if __name__ == "__main__":
    main()
