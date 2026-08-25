# AI Docker Incident Troubleshooting Agent

A ReAct-style DevOps/SRE demo using OpenAI Function Calling and Docker. A user can report a service problem in natural language; the agent discovers the relevant container, checks state/exit code/restart count/health, reads logs, optionally checks HTTP availability, and gives evidence-based troubleshooting recommendations.

The agent is intentionally READ-ONLY: it does not restart, delete, or modify containers.

## Setup

Start Docker Desktop, then:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    export OPENAI_MODEL="gpt-5.6-luna"
    docker compose up -d
    docker ps

## Run

    python3 agent.py "Investigate why the orders service is unavailable."

## Test stopped container

    docker stop orders-nginx
    docker ps -a
    python3 agent.py "Investigate why the orders service is unavailable."

The agent should discover `orders-nginx` is exited, inspect it, read logs, and explain what the evidence supports without inventing a root cause.

## HTTP test

    docker compose up -d
    curl http://localhost:8081
    curl http://localhost:8082
    python3 agent.py "Check whether the orders service is reachable at http://localhost:8081."

## Tools

- `list_containers()` - discover running/stopped containers
- `inspect_container()` - state, exit code, restart count, health
- `get_container_logs()` - recent logs
- `check_http()` - local HTTP reachability

## Architecture

User -> OpenAI LLM -> Function Calling -> Python tools -> Docker/HTTP -> evidence -> LLM -> investigation report

## ReAct

REASON -> ACTION -> OBSERVATION -> REASON -> ACTION -> OBSERVATION -> FINAL REPORT

## Resume

Built an LLM-driven ReAct-based Docker Incident Troubleshooting Agent using OpenAI Function Calling to discover affected containers, analyze stopped/exited states, exit codes, restart behaviour, logs and HTTP availability, and provide evidence-based DevOps troubleshooting recommendations.
