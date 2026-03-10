# Jira Stories ACP Server

An [Agent Communication Protocol (ACP)](https://agentcommunicationprotocol.dev/) server
that exposes Jira stories as an AI-accessible agent.

## Overview

The server registers a single agent called **`jira_stories`** that accepts natural-language
commands and returns Jira issue information using the Jira REST API.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

| Variable | Required | Description |
|---|---|---|
| `JIRA_BASE_URL` | ✅ | Base URL of your Jira instance, e.g. `https://mycompany.atlassian.net` |
| `JIRA_EMAIL` | ✅ | Jira user email for authentication |
| `JIRA_API_TOKEN` | ✅ | [Jira API token](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_PROJECT_KEY` | optional | Default project key used when listing stories |
| `ACP_PORT` | optional | Port the ACP server listens on (default: `8000`) |

```bash
export JIRA_BASE_URL="https://mycompany.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_KEY="PROJ"   # optional default project
```

## Running the server

```bash
python -m jira_acp_server.server
```

The server starts on `http://127.0.0.1:8000` by default.

## Agent commands

Once the server is running you can interact with the `jira_stories` agent via any
ACP-compatible client:

| Command | Description |
|---|---|
| `list [PROJECT_KEY]` | List Story-type issues, optionally filtered by project |
| `get ISSUE_KEY` | Fetch details for a single issue, e.g. `get PROJ-42` |
| `search JQL` | Search issues using a JQL expression |
| `help` | Show usage information |

### Example using the ACP Python SDK client

```python
import asyncio
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart

async def main():
    async with Client(base_url="http://localhost:8000") as client:
        # List stories in project PROJ
        result = await client.run_sync(
            agent="jira_stories",
            input=[Message(parts=[MessagePart(content="list PROJ")])]
        )
        for message in result.output:
            for part in message.parts:
                print(part.content)

asyncio.run(main())
```

## Running tests

```bash
python -m pytest jira_acp_server/tests.py -v
```
