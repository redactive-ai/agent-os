# Agent OS 

The AgentOS is a sample implementation of the Open Agent Specification. It provides a framework for managing secure AI Agents that can perform various tasks autonomously and securely.

## Key Features

- Multi-tenant Agents: Supports multiple authorised users.
- Secure Agents: Handles highly sensitive content securely.
- Safe Agents: Performs actions autonomously while ensuring safety.
- Inter-agent Communication: Facilitates communication between agents across different authorisation and organisational boundaries.

## Open Agent Specification

At Redactive, we have extensive experience in developing, deploying, and maintaining generative AI applications. In this RFC, we define what a Generative AI Agent, or “Agent” is, how they can be defined safely and securely, and outline a formal standard to provide consistent expectations for agentic workflows. Agents that follow the OpenAgentSpec are able to:
- Be used by multiple authorized users (multi-tenant agents)
- Interact with highly sensitive content (secure agents)
- Autonomously perform actions safely (safe agents)
Communicate with other agents:
- with differing authorization boundaries
- across organisational boundaries

We believe that by taking an opinionated stance on what an Agent is, we can further goals to:
- Assist consumers and enterprises to onboard agents securely
- Establish best practises for platform providers to integrate with
- Build consistent expectations of how an agent should operate

The Open Agent Specification has been developed in an open fashion, including hosting requests for comments amongst industry leaders, and ensuring all future changes are versioned semantically as ideas evolve.

## Repo Structure

`├──`[`.devcontainer`](.devcontainer/) — Docker dev container configuration<br>
`├──`[`pyproject.toml`](pyproject.toml/) — Setuptools configuration<br>
`├──`[`src/redactive/agent_os`](src/redactive/agent_os/) — Example agent implementation<br>
`├──`[`src/redactive/cli`](src/redactive/cli/) — CLI for interacting with an agent/synapse<br>
`├──`[`src/redactive/utils`](src/redactive/utils/) — Libraries and tools<br>
`├──`[`.pre-commit-config.yaml`](.pre-commit-config.yaml) — Pre-commit hooks<br>


## Getting Started

### CLI

The CLI utilises the Google Secret Manager service which requires a login to Google Cloud and a valid project to store credentials. To setup a Google project for free visit [Google Cloud](https://cloud.google.com).

1. To authenticate the CLI, run the following:
`gcloud init && gcloud auth application-default login`
2. Run the agent_os using:
`python src/redactive/cli/main.py agent-os serve`

## Contribution Guide

This repository is configured to run formatting, testing, linting with pre-commit hooks. Read [`.pre-commit-config.yaml`](.pre-commit-config.yaml) for more details.

### PR Creation Flow

1. **Fork the Repository**: Click the "Fork" button on the repository's GitHub page.
2. **Clone Your Fork**: Clone the forked repository to your local machine.
3. **Create a New Branch**: Create and switch to a new branch for your changes.
4. **Make Changes**: Make your changes, then stage and commit them.
5. **Push the Changes**: Push your branch to your forked repository.
6. **Create a Pull Request**: On GitHub, open a pull request from your branch to the Redactive repository's main branch.
7. **Respond to Feedback**: Make any requested changes and push them to your branch.

### PR Review Flow

- Ensure quality checks pass.
- Ensure the build process passes.
- Reviewer reviews and responds to code changes.
- Reviewer merges approved code changes.
