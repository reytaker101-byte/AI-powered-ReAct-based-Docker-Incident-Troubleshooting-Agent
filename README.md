================================================================================
AI-POWERED ReAct-BASED DOCKER INCIDENT TROUBLESHOOTING AGENT
================================================================================

PURPOSE
-------
This project is a beginner-friendly DevOps/SRE AI Agent that investigates a
Docker-based service incident and can take a SAFE recovery action.

Example:

    User: "Check the orders service and investigate if anything is wrong."

The user does NOT need to know the Docker container name.

The Agent:

    1. Understands the user request
    2. Finds the relevant Docker container
    3. Checks container state
    4. Investigates logs
    5. If container is stopped/exited -> starts it
    6. Verifies that the container is running
    7. Gives an evidence-based final report

This demonstrates:

    LLM + Function Calling + ReAct loop + Docker tools + Automated remediation


================================================================================
1. HIGH-LEVEL USE CASE
================================================================================

                    USER
                      |
                      | "Check orders service"
                      v
                +-----------+
                |    LLM    |
                +-----------+
                      |
                      | selects tool
                      v
                +-----------+
                |  Docker   |
                |   Tools   |
                +-----------+
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       LIST       INSPECT       LOGS
    containers   container     evidence
          |           |           |
          +-----------+-----------+
                      |
                      v
                Is container
                   stopped?
                      |
                 +----+----+
                 |         |
                YES        NO
                 |         |
                 v         v
             START IT   INVESTIGATE
                 |
                 v
             INSPECT AGAIN
                 |
                 v
             running=true
                 |
                 v
              FINAL
              REPORT


IMPORTANT DIFFERENCE FROM THE PREVIOUS PROJECT:

Previous project:
    DETECT -> INVESTIGATE -> REPORT

Updated project:
    DETECT -> INVESTIGATE -> ACT -> VERIFY -> REPORT

So this is not only an AI troubleshooting/reporting agent.
It can also perform a controlled remediation action.


================================================================================
2. WHAT IS ReAct?
================================================================================

ReAct = Reason + Act

The agent repeatedly follows:

    REASON
       |
       v
    ACT -> call a tool
       |
       v
    OBSERVE -> receive real Docker output
       |
       v
    REASON again
       |
       v
    ACT again if required
       |
       v
    FINAL ANSWER

Example from our run:

    REASON
      |
      v
    list_containers()
      |
      v
    OBSERVE: orders-nginx = Exited
      |
      v
    REASON
      |
      v
    inspect_container("orders-nginx")
      |
      v
    OBSERVE: running=false
      |
      v
    REASON
      |
      v
    start_container("orders-nginx")
      |
      v
    OBSERVE: STARTED
      |
      v
    inspect_container("orders-nginx")
      |
      v
    OBSERVE: running=true
      |
      v
    FINAL RESPONSE


================================================================================
3. PROJECT FILES
================================================================================

Repository contains:

    README.md
        -> Project documentation

    agent.py
        -> Main AI Agent
        -> OpenAI API call
        -> ReAct loop
        -> Tool selection
        -> Tool execution
        -> Final investigation report

    tools.py
        -> Actual Docker business logic
        -> list containers
        -> inspect container
        -> read logs
        -> start stopped container

    docker-compose.yml
        -> Creates demo Docker services

    nginx/
        -> Demo HTML files for the services

    requirements.txt
        -> Python dependency:
           openai>=1.0.0


================================================================================
4. CLONE THE GITHUB PROJECT
================================================================================

COMMAND:

    git clone https://github.com/reytaker101-byte/AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent.git

OUTPUT:

    Cloning into 'AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent'...
    remote: Enumerating objects: 19, done.
    remote: Counting objects: 100% (19/19), done.
    remote: Compressing objects: 100% (18/18), done.
    remote: Total 19 (delta 4), reused 0 (delta 0), pack-reused 0
    Receiving objects: 100% (19/19), 15.84 KiB | 900.00 KiB/s, done.
    Resolving deltas: 100% (4/4), done.

GO INSIDE:

    cd AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent

CHECK FILES:

    ls

OUTPUT:

    README.md
    agent.py
    docker-compose.yml
    nginx
    requirements.txt
    tools.py


================================================================================
5. CHECK DOCKER
================================================================================

COMMAND:

    docker ps -a

Initially the old BuildKit container was present:

    CONTAINER ID   IMAGE                           STATUS
    8ccc835c9400   moby/buildkit:buildx-stable-1   Exited (137)

It was removed:

    docker rm 8cc

OUTPUT:

    8cc


================================================================================
6. CREATE PYTHON VIRTUAL ENVIRONMENT
================================================================================

A virtual environment keeps project Python packages isolated.

COMMAND:

    python3 -m venv .venv

ACTIVATE:

    source .venv/bin/activate

OUTPUT:

    (.venv) admin@NewLearning#


IMPORTANT:

When the .venv did not exist initially, this happened:

    source .venv/bin/activate
    source: no such file or directory: .venv/bin/activate

So we created it first:

    python3 -m venv .venv

and then activated it.


================================================================================
7. INSTALL OPENAI SDK
================================================================================

COMMAND:

    python3 -m pip install -r requirements.txt

requirements.txt:

    openai>=1.0.0

Installed version in this run:

    openai 3.3.1

VERIFY:

    python3 -c "import openai; print('OpenAI SDK:', openai.__version__)"

OUTPUT:

    OpenAI SDK: 3.3.1


================================================================================
8. OPENAI CONFIGURATION
================================================================================

The Agent uses the OpenAI API to make the LLM decision.

Environment variables:

    OPENAI_API_KEY
        -> Secret API credential

    OPENAI_MODEL
        -> Model used by the Agent

COMMAND:

    export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

COMMAND:

    export OPENAI_MODEL="gpt-5.6-luna"

VERIFY MODEL:

    echo $OPENAI_MODEL

OUTPUT:

    gpt-5.6-luna


IMPORTANT SECURITY NOTE:

Never commit the real OPENAI_API_KEY into GitHub.

Do NOT put it in:

    README.md
    agent.py
    tools.py
    .env committed to GitHub

Use an environment variable or secret manager.


================================================================================
9. DOCKER DEMO ENVIRONMENT
================================================================================

The project uses Docker Compose to create two demo services:

    orders-nginx
    payments-nginx

Start them:

    docker compose up -d

OUTPUT:

    [+] Running 2/2
     ✔ Container payments-nginx  Started
     ✔ Container orders-nginx    Started


CHECK:

    docker ps -a

OUTPUT:

    CONTAINER ID   IMAGE          STATUS        PORTS
    faaa38463f3e   nginx:alpine   Up 7 seconds  0.0.0.0:8081->80/tcp
    01035e2583cf   nginx:alpine   Up 7 seconds  0.0.0.0:8082->80/tcp

CONTAINER MAPPING:

    orders-nginx
        Docker port 80
        |
        v
        Mac localhost:8081

    payments-nginx
        Docker port 80
        |
        v
        Mac localhost:8082


================================================================================
10. VERIFY THE SERVICES MANUALLY
================================================================================

ORDERS:

    curl http://localhost:8081

OUTPUT:

    <!doctype html><html><body><h1>Orders Service</h1><p>Status: OK</p></body></html>


PAYMENTS:

    curl http://localhost:8082

OUTPUT:

    <!doctype html><html><body><h1>Payments Service</h1><p>Status: OK</p></body></html>


This proves that the demo services are reachable before creating the incident.


================================================================================
11. CREATE THE INCIDENT
================================================================================

We intentionally stop the Orders container.

COMMAND:

    docker stop orders-nginx

OUTPUT:

    orders-nginx

Now check:

    docker ps -a

OUTPUT:

    CONTAINER ID   IMAGE          STATUS
    faaa38463f3e   nginx:alpine   Exited (0) 15 seconds ago
    01035e2583cf   nginx:alpine   Up 2 minutes

IMPORTANT:

    Exited (0)

does NOT necessarily mean application failure/crash.

Exit code 0 means the container process exited successfully.

For this demo, the important fact is:

    orders-nginx
        |
        v
    Exited
        |
        v
    running = false
        |
        v
    Service unavailable


================================================================================
12. CORE TOOL: list_containers()
================================================================================

Purpose:

Find what Docker containers currently exist and their state.

Conceptually:

    list_containers()
          |
          v
    docker ps -a
          |
          v
    container names + status + image


During the Agent run:

    [Tool Action] list_containers({})

Output:

    {
      "status": "OK",
      "containers": [
        {
          "name": "orders-nginx",
          "status": "Exited (0) 3 minutes ago",
          "image": "nginx:alpine"
        },
        {
          "name": "payments-nginx",
          "status": "Up 5 minutes",
          "image": "nginx:alpine"
        }
      ]
    }

The LLM now has real Docker evidence.

It does NOT guess:

    "Maybe orders-nginx is down."

It has actual evidence:

    orders-nginx = Exited


================================================================================
13. CORE TOOL: inspect_container()
================================================================================

Purpose:

Get detailed state information about a specific container.

The Agent called:

    inspect_container("orders-nginx")

Output:

    {
      "status": "FOUND",
      "container": "orders-nginx",
      "image": "nginx:alpine",
      "state": "exited",
      "running": false,
      "exit_code": 0,
      "restart_count": 0,
      "health": "not_configured",
      "started_at": "2026-08-26T07:03:58.602542716Z",
      "finished_at": "2026-08-26T07:05:52.018974338Z"
    }

Most important fields:

    state = exited
        -> container is stopped

    running = false
        -> container is NOT running

    exit_code = 0
        -> process exited cleanly

    restart_count = 0
        -> Docker has not restarted it

    health = not_configured
        -> no Docker health check exists


================================================================================
14. WHY DOES THE AGENT INSPECT BEFORE ACTING?
================================================================================

The Agent should not blindly execute:

    docker start orders-nginx

Instead:

    FIND
      ↓
    INSPECT
      ↓
    CONFIRM stopped
      ↓
    ACT

This is safer because the Agent first collects evidence.

In our run:

    list_containers()
          ↓
    orders-nginx = Exited
          ↓
    inspect_container()
          ↓
    running = false
          ↓
    start_container()


================================================================================
15. CORE ACTION TOOL: start_container()
================================================================================

This is the major change from the earlier version of the project.

Purpose:

Start a Docker container when the Agent determines that it is stopped.

Agent action:

    [Tool Action] start_container(
        {"container_name":"orders-nginx"}
    )

Tool output:

    -> TOOL: Checking whether orders-nginx can be started...
    -> TOOL: Starting stopped container orders-nginx...

    {
      "status": "STARTED",
      "container": "orders-nginx",
      "previous_state": "exited",
      "message": "Container start command completed successfully."
    }

This is the:

    ACT

part of the ReAct architecture.


================================================================================
16. WHY VERIFICATION IS IMPORTANT
================================================================================

The Agent does NOT simply assume:

    start command succeeded
        =
    service is healthy

It performs another inspection.

Agent:

    [Tool Action] inspect_container(
        {"container_name":"orders-nginx"}
    )

Output:

    {
      "status": "FOUND",
      "container": "orders-nginx",
      "image": "nginx:alpine",
      "state": "running",
      "running": true,
      "exit_code": 0,
      "restart_count": 0,
      "health": "not_configured"
    }

This proves:

    Before:
        running = false

    Action:
        start_container()

    After:
        running = true


================================================================================
17. LOG INVESTIGATION
================================================================================

The Agent also collected logs:

    [Tool Action] get_container_logs(
        {"container_name":"orders-nginx","tail":50}
    )

Relevant output:

    /docker-entrypoint.sh:
    Configuration complete; ready for start up

    192.168.65.1 - - [26/Aug/2026:07:04:23 +0000]
    "GET / HTTP/1.1" 200 82

This tells us:

    Nginx configuration completed successfully.

And:

    GET /
    HTTP 200

means the web endpoint previously responded successfully.

The Agent therefore does NOT invent a root cause.


================================================================================
18. COMPLETE AGENT RUN
================================================================================

COMMAND:

    python3 agent.py "Check the orders service and investigate if anything is wrong."


OUTPUT:

    === AI DOCKER INCIDENT TROUBLESHOOTING AGENT ===
    Model: gpt-5.6-luna
    Incident: Check the orders service and investigate if anything is wrong.

    [Agent Step 1] Thinking / selecting evidence...

    [Tool Action] list_containers({})

    [Observation] {
      "status": "OK",
      "containers": [
        {
          "name": "orders-nginx",
          "status": "Exited (0) 3 minutes ago",
          "image": "nginx:alpine"
        },
        {
          "name": "payments-nginx",
          "status": "Up 5 minutes",
          "image": "nginx:alpine"
        }
      ]
    }

    [Agent Step 2] Thinking / selecting evidence...

    [Tool Action] inspect_container(
        {"container_name":"orders-nginx"}
    )

    [Observation] {
      "status": "FOUND",
      "container": "orders-nginx",
      "image": "nginx:alpine",
      "state": "exited",
      "running": false,
      "exit_code": 0,
      "restart_count": 0,
      "health": "not_configured"
    }

    [Agent Step 3] Thinking / selecting evidence...

    [Tool Action] start_container(
        {"container_name":"orders-nginx"}
    )

    -> TOOL: Checking whether orders-nginx can be started...
    -> TOOL: Starting stopped container orders-nginx...

    [Observation] {
      "status": "STARTED",
      "container": "orders-nginx",
      "previous_state": "exited",
      "message": "Container start command completed successfully."
    }

    [Agent Step 4] Thinking / selecting evidence...

    [Tool Action] inspect_container(
        {"container_name":"orders-nginx"}
    )

    [Observation] {
      "status": "FOUND",
      "container": "orders-nginx",
      "image": "nginx:alpine",
      "state": "running",
      "running": true,
      "exit_code": 0,
      "restart_count": 0,
      "health": "not_configured"
    }

    [Tool Action] get_container_logs(
        {"container_name":"orders-nginx","tail":50}
    )

    [Observation] {
      "status": "OK",
      "container": "orders-nginx",
      "tail": 50,
      "logs": "... Configuration complete; ready for start up ..."
    }


================================================================================
19. FINAL AI RESPONSE
================================================================================

    === FINAL INVESTIGATION ===

    Incident:
    The orders service container was stopped and unavailable.

    Evidence:
    - Container identified: orders-nginx
    - Initial state: exited
    - Running: false
    - Exit code: 0
    - Restart count: 0
    - Logs showed normal Nginx startup and configuration messages.
    - No health check was configured.

    Action Taken:
    - Started the stopped orders-nginx container.

    Verification:
    - Post-start inspection confirms:
      State: running
      Running: true

    Likely Cause:
    Undetermined. The container exited cleanly with code 0, but the
    available evidence does not explain why.

    Final Status:
    Resolved at the container level; application-level health remains
    unverified.

    Next Steps:
    - Configure or provide an HTTP health endpoint.
    - Investigate why the container stopped if unexpected shutdowns recur.


================================================================================
20. FINAL DOCKER VERIFICATION
================================================================================

After the Agent completed the remediation:

COMMAND:

    docker ps

OUTPUT:

    CONTAINER ID   IMAGE          STATUS        PORTS
    faaa38463f3e   nginx:alpine   Up 35 seconds 0.0.0.0:8081->80/tcp   orders-nginx
    01035e2583cf   nginx:alpine   Up 6 minutes  0.0.0.0:8082->80/tcp   payments-nginx

This is the final physical proof from Docker:

    orders-nginx = UP


================================================================================
21. WHAT ACTUALLY HAPPENED?
================================================================================

Before incident:

    orders-nginx
         |
         v
       RUNNING
         |
         v
    localhost:8081
         |
         v
       HTTP 200


We intentionally created an incident:

    docker stop orders-nginx
         |
         v
    orders-nginx
         |
         v
       EXITED
         |
         v
    running = false


Then the AI Agent handled it:

    User reports problem
           |
           v
    LLM selects list_containers
           |
           v
    Finds orders-nginx
           |
           v
    inspect_container
           |
           v
    Confirms running=false
           |
           v
    start_container
           |
           v
    orders-nginx STARTED
           |
           v
    inspect_container again
           |
           v
    running=true
           |
           v
    read logs
           |
           v
    Final evidence-based report


================================================================================
22. WHAT IS THE BENEFIT?
================================================================================

Traditional approach:

    User reports:
        "Orders service is down."

    Engineer:
        docker ps -a
        docker inspect orders-nginx
        docker logs orders-nginx
        docker start orders-nginx
        docker inspect orders-nginx

    Multiple manual steps.


AI Agent approach:

    User:
        "Check the orders service."

                 |
                 v

             AI Agent
                 |
          +------+------+------+
          |      |      |      |
         FIND  CHECK  START  VERIFY
          |      |      |      |
          +------+------+------+
                 |
                 v
          Investigation report


The AI does not replace Docker.

The AI is the decision-making/orchestration layer.

Docker remains the system that actually performs the operation.


================================================================================
23. IMPORTANT TERMINOLOGY
================================================================================

LLM
---
Large Language Model.

In this project:

    LLM = brain that understands the user request and decides which
          tool should be used.

Agent
-----
An LLM + tools + instructions + execution loop.

Here:

    Agent = OpenAI LLM + Docker tools + ReAct loop


Function Calling
----------------
Mechanism through which the LLM requests a specific function/tool.

Example:

    LLM
     |
     v
    start_container(
        container_name="orders-nginx"
    )


Tool
----
A Python function that allows the Agent to interact with the real system.

Examples:

    list_containers()
    inspect_container()
    get_container_logs()
    start_container()


Observation
-----------
The real output returned by the tool.

Example:

    running = false

The LLM uses this information for its next decision.


Remediation
-----------
An action taken to fix/recover an incident.

Here:

    start_container("orders-nginx")


Verification
------------
Checking whether the remediation actually worked.

Here:

    inspect_container()
        |
        v
    running = true


Evidence
--------
Actual information obtained from Docker.

Examples:

    state = exited
    running = false
    exit_code = 0
    logs = normal Nginx startup


Inference
---------
A conclusion made from evidence.

Example:

    "The container stopped cleanly."

But:

    "Someone manually stopped it."

would NOT be claimed unless evidence proves it.


================================================================================
24. SAFETY PRINCIPLE
================================================================================

The Agent should not blindly modify infrastructure.

Current remediation is intentionally limited:

    ALLOWED:
        start stopped container

    NOT automatically doing:
        delete container
        remove image
        modify configuration
        change network
        change certificates
        deploy code
        restart everything
        destroy infrastructure

The Agent should collect evidence first and then take the permitted action.


================================================================================
25. CURRENT PROJECT LIMITATION
================================================================================

The current final output itself says:

    "application-level health remains unverified."

Why?

Because container state:

    running = true

does NOT automatically mean:

    application = healthy


For example:

    Container RUNNING
          |
          X
          |
    Application could still return HTTP 500


For this demo we manually know:

    orders-nginx -> localhost:8081

and earlier:

    curl http://localhost:8081

returned:

    <!doctype html><html><body><h1>Orders Service</h1>
    <p>Status: OK</p></body></html>

So a stronger future version would add:

    HTTP health-check tool
          |
          v
    curl localhost:8081
          |
          v
    HTTP 200?
          |
       +--+--+
       |     |
      YES    NO
       |     |
    Healthy  Investigate


================================================================================
26. COMPLETE ARCHITECTURE
================================================================================

                         USER
                          |
                          | Natural language
                          v
                  +----------------+
                  |   OPENAI LLM   |
                  +----------------+
                          |
                          | Function Calling
                          v
                  +----------------+
                  |   ReAct Agent  |
                  +----------------+
                          |
             +------------+-------------+
             |            |             |
             v            v             v
       list_containers  inspect       logs
             |         container        |
             |            |             |
             +------------+-------------+
                          |
                          v
                   Docker Desktop
                          |
                          v
                    orders-nginx
                          |
                   state = exited
                          |
                          v
                  start_container()
                          |
                          v
                    orders-nginx
                          |
                    state = running
                          |
                          v
                    verify again
                          |
                          v
                    FINAL REPORT


================================================================================
27. ONE-MINUTE EXPLANATION FOR INTERVIEW/SESSION
================================================================================

"I built an AI-powered ReAct-based Docker Incident Troubleshooting Agent
using OpenAI Function Calling.

The user can report an issue in natural language, such as 'Check the
orders service'. The LLM does not directly execute Docker commands.
Instead, it selects from predefined Python tools.

First, the agent discovers the relevant container and inspects its state.
If the container is stopped or exited, the agent invokes a controlled
start_container tool. After the action, it performs another inspection
to verify that the container is actually running. It also collects recent
logs and produces an evidence-based incident summary.

So the important ReAct flow is:

    Reason -> Tool Action -> Observation -> Reason -> Action -> Verify -> Report

The project demonstrates LLMs, function calling, tool execution, Docker
automation, incident investigation and automated remediation."


================================================================================
28. RESUME BULLET
================================================================================

Built an AI-powered ReAct-based Docker Incident Troubleshooting Agent
using OpenAI Function Calling that autonomously discovers affected
containers, investigates container state and logs, performs controlled
service recovery for stopped containers, and verifies post-remediation
state.


================================================================================
29. FINAL MEMORY TRICK
================================================================================

Traditional:

    HUMAN
      |
      v
    CHECK
      |
      v
    FIX
      |
      v
    VERIFY


Our AI Agent:

    USER
      |
      v
    LLM
      |
      v
    REASON
      |
      v
    TOOL
      |
      v
    OBSERVE
      |
      v
    REASON
      |
      v
    ACT
      |
      v
    VERIFY
      |
      v
    REPORT


ONE LINE:

    "LLM decides WHAT to investigate/do,
     Python tools actually DO it,
     Docker provides the REAL evidence,
     and the Agent verifies the result."
================================================================================
