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

admin@NewLearning# git clone https://github.com/reytaker101-byte/AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent.git
Cloning into 'AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent'...
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 10 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (10/10), 5.20 KiB | 2.60 MiB/s, done.
admin@NewLearning#cd AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent 
admin@NewLearning#pwd
/Users/dollyd/Desktop/AI-powered-ReAct-based-Docker-Incident-Troubleshooting-Agent
admin@NewLearning#ls
README.md               agent.py                docker-compose.yml      nginx                   requirements.txt        tools.py
admin@NewLearning#python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install -r requirements.txt
Collecting openai>=1.0.0 (from -r requirements.txt (line 1))
  Using cached openai-3.3.1-py3-none-any.whl.metadata (41 kB)
Collecting anyio<5,>=4.10.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
Collecting httpx2<3,>=2.7.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached httpx2-2.12.0-py3-none-any.whl.metadata (9.5 kB)
Collecting jiter<1,>=0.16.0 (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached jiter-0.16.0-cp314-cp314-macosx_11_0_arm64.whl.metadata (5.2 kB)
Collecting pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13 (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached pydantic-2.13.4-py3-none-any.whl.metadata (109 kB)
Collecting sniffio (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting typing-extensions<5,>=4.14 (from openai>=1.0.0->-r requirements.txt (line 1))
  Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting idna>=2.8 (from anyio<5,>=4.10.0->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached idna-3.19-py3-none-any.whl.metadata (9.2 kB)
Collecting httpcore2==2.12.0 (from httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached httpcore2-2.12.0-py3-none-any.whl.metadata (25 kB)
Collecting truststore>=0.10 (from httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached truststore-0.10.4-py3-none-any.whl.metadata (4.4 kB)
Collecting h11>=0.16 (from httpcore2==2.12.0->httpx2<3,>=2.7.0->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting annotated-types>=0.6.0 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.4 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached pydantic_core-2.46.4-cp314-cp314-macosx_11_0_arm64.whl.metadata (6.6 kB)
Collecting typing-inspection>=0.4.2 (from pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,<3,>=1.10.13->openai>=1.0.0->-r requirements.txt (line 1))
  Using cached typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
Using cached openai-3.3.1-py3-none-any.whl (1.7 MB)
Using cached anyio-4.14.2-py3-none-any.whl (125 kB)
Using cached httpx2-2.12.0-py3-none-any.whl (95 kB)
Using cached httpcore2-2.12.0-py3-none-any.whl (83 kB)
Using cached jiter-0.16.0-cp314-cp314-macosx_11_0_arm64.whl (308 kB)
Using cached pydantic-2.13.4-py3-none-any.whl (472 kB)
Using cached pydantic_core-2.46.4-cp314-cp314-macosx_11_0_arm64.whl (2.0 MB)
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Using cached annotated_types-0.8.0-py3-none-any.whl (13 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Using cached idna-3.19-py3-none-any.whl (68 kB)
Using cached truststore-0.10.4-py3-none-any.whl (18 kB)
Using cached typing_inspection-0.4.4-py3-none-any.whl (14 kB)
Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
Installing collected packages: typing-extensions, truststore, sniffio, jiter, idna, h11, annotated-types, typing-inspection, pydantic-core, httpcore2, anyio, pydantic, httpx2, openai
Successfully installed annotated-types-0.8.0 anyio-4.14.2 h11-0.16.0 httpcore2-2.12.0 httpx2-2.12.0 idna-3.19 jiter-0.16.0 openai-3.3.1 pydantic-2.13.4 pydantic-core-2.46.4 sniffio-1.3.1 truststore-0.10.4 typing-extensions-4.16.0 typing-inspection-0.4.4

[notice] A new release of pip is available: 25.2 -> 26.2.1
[notice] To update, run: pip install --upgrade pip
(.venv) admin@NewLearning#python3 -c "import openai; print('OpenAI SDK:', openai.__version__)"
OpenAI SDK: 3.3.1
(.venv) admin@NewLearning#export OPENAI_API_KEY="YOUR_REAL_OPENAI_API_KEY"
(.venv) admin@NewLearning#export OPENAI_API_KEY="sk-xxxxxxxxxx"
(.venv) admin@NewLearning#python3 -c "import os; print('API key configured:', bool(os.getenv('OPENAI_API_KEY')))"
API key configured: True
(.venv) admin@NewLearning#export OPENAI_MODEL="gpt-5.6-luna"
(.venv) admin@NewLearning#echo $OPENAI_MODEL
gpt-5.6-luna
(.venv) admin@NewLearning#docker compose up -d
[+] Running 2/3
 ✔ Network ai-powered-react-based-docker-incident-troubleshooting-agent_default  Crea...                                                                                0.1s 
 ✘ Container orders-nginx                                                        Error response from daemon: Conflict. The container name "...                          0.1s 
 ⠋ Container payments-nginx                                                      Creating                                                                               0.1s 
Error response from daemon: Conflict. The container name "/orders-nginx" is already in use by container "72b0e07cb0818d6aa622beff8db1b90b855ed3d03969a4c5819b4a6b3885784a". You have to remove (or rename) that container to be able to reuse that name.
(.venv) admin@NewLearning#docker ps -a
CONTAINER ID   IMAGE                           COMMAND                  CREATED        STATUS                      PORTS     NAMES
c38aaf66b518   nginx:alpine                    "/docker-entrypoint.…"   4 days ago     Exited (0) 4 days ago                 payments-nginx
72b0e07cb081   nginx:alpine                    "/docker-entrypoint.…"   4 days ago     Exited (0) 4 days ago                 orders-nginx
8ccc835c9400   moby/buildkit:buildx-stable-1   "/usr/bin/buildkitd-…"   4 months ago   Exited (137) 4 months ago             buildx_buildkit_serene_euler0
(.venv) admin@NewLearning#docker rm c38aa
c38aa
(.venv) admin@NewLearning#docker rm 71b0 
Error response from daemon: No such container: 71b0
(.venv) admin@NewLearning#docker rm 72b0
72b0
(.venv) admin@NewLearning#docker compose up -d
[+] Running 2/2
 ✔ Container orders-nginx    Started                                                                                                                                    0.8s 
 ✔ Container payments-nginx  Started                                                                                                            
 
 admin@NewLearning#curl http://localhost:8081
<!doctype html><html><body><h1>Orders Service</h1><p>Status: OK</p></body></html>

(.venv) admin@NewLearning#python3 agent.py "Check the orders service and investigate if anything is wrong."

=== AI DOCKER INCIDENT TROUBLESHOOTING AGENT ===
Model: gpt-5.6-luna
Incident: Check the orders service and investigate if anything is wrong.

[Agent Step 1] Thinking / selecting evidence...
[Tool Action] list_containers({})
[Observation] {
  "status": "OK",
  "containers": [
    {
      "name": "payments-nginx",
      "status": "Up 4 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "orders-nginx",
      "status": "Up 4 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "buildx_buildkit_serene_euler0",
      "status": "Exited (137) 4 months ago",
      "image": "moby/buildkit:buildx-stable-1"
    }
  ]
}
[Agent Step 2] Thinking / selecting evidence...
[Tool Action] inspect_container({"container_name":"orders-nginx"})
[Observation] {
  "status": "FOUND",
  "container": "orders-nginx",
  "image": "nginx:alpine",
  "state": "running",
  "running": true,
  "exit_code": 0,
  "restart_count": 0,
  "health": "not_configured",
  "started_at": "2026-08-26T05:24:08.306947012Z",
  "finished_at": "0001-01-01T00:00:00Z"
}
[Agent Step 3] Thinking / selecting evidence...
[Tool Action] get_container_logs({"container_name":"orders-nginx","tail":100})
[Observation] {
  "status": "OK",
  "container": "orders-nginx",
  "tail": 100,
  "logs": "/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration\n/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh\n10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf\n10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf\n/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh\n/docker-entrypoint.sh: Configuration complete; ready for start up\n192.168.65.1 - - [26/Aug/2026:05:27:21 +0000] \"GET / HTTP/1.1\" 200 82 \"-\" \"curl/8.7.1\" \"-\""
}
[Agent Step 4] Thinking / selecting evidence...

=== FINAL INVESTIGATION ===
## Incident
No active fault detected in the `orders-nginx` service.

## Evidence
- Container `orders-nginx` is **running**.
- Exit code: `0`.
- Restart count: `0`.
- Docker health status: **not configured**.
- Logs show Nginx completed configuration successfully and was “ready for start up.”
- A recent `GET /` request returned HTTP **200**.

## Likely cause
No evidence of an incident or service failure. The service appears operational. Health monitoring is not configured, so Docker is not independently reporting application health.

## Recommended next steps
- No restart or remediation is currently indicated.
- If stronger monitoring is required, configure a Docker health check for the orders service.
- If users are reporting problems despite the successful root request, provide the affected endpoint, timestamp, and error so it can be investigated further.
(.venv) admin@NewLearning#

<img width="2388" height="1690" alt="image" src="https://github.com/user-attachments/assets/39cb09f2-16ab-4a14-92b6-c3e0976de7f7" />

#Stop orders container
(.venv) admin@NewLearning#python3 agent.py "Check the orders service and investigate if anything is wrong."

=== AI DOCKER INCIDENT TROUBLESHOOTING AGENT ===
Model: gpt-5.6-luna
Incident: Check the orders service and investigate if anything is wrong.

[Agent Step 1] Thinking / selecting evidence...
[Tool Action] list_containers({})
[Observation] {
  "status": "OK",
  "containers": [
    {
      "name": "payments-nginx",
      "status": "Up 4 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "orders-nginx",
      "status": "Up 4 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "buildx_buildkit_serene_euler0",
      "status": "Exited (137) 4 months ago",
      "image": "moby/buildkit:buildx-stable-1"
    }
  ]
}
[Agent Step 2] Thinking / selecting evidence...
[Tool Action] inspect_container({"container_name":"orders-nginx"})
[Observation] {
  "status": "FOUND",
  "container": "orders-nginx",
  "image": "nginx:alpine",
  "state": "running",
  "running": true,
  "exit_code": 0,
  "restart_count": 0,
  "health": "not_configured",
  "started_at": "2026-08-26T05:24:08.306947012Z",
  "finished_at": "0001-01-01T00:00:00Z"
}
[Agent Step 3] Thinking / selecting evidence...
[Tool Action] get_container_logs({"container_name":"orders-nginx","tail":100})
[Observation] {
  "status": "OK",
  "container": "orders-nginx",
  "tail": 100,
  "logs": "/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration\n/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh\n10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf\n10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf\n/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh\n/docker-entrypoint.sh: Configuration complete; ready for start up\n192.168.65.1 - - [26/Aug/2026:05:27:21 +0000] \"GET / HTTP/1.1\" 200 82 \"-\" \"curl/8.7.1\" \"-\""
}
[Agent Step 4] Thinking / selecting evidence...

=== FINAL INVESTIGATION ===
## Incident
No active fault detected in the `orders-nginx` service.

## Evidence
- Container `orders-nginx` is **running**.
- Exit code: `0`.
- Restart count: `0`.
- Docker health status: **not configured**.
- Logs show Nginx completed configuration successfully and was “ready for start up.”
- A recent `GET /` request returned HTTP **200**.

## Likely cause
No evidence of an incident or service failure. The service appears operational. Health monitoring is not configured, so Docker is not independently reporting application health.

## Recommended next steps
- No restart or remediation is currently indicated.
- If stronger monitoring is required, configure a Docker health check for the orders service.
- If users are reporting problems despite the successful root request, provide the affected endpoint, timestamp, and error so it can be investigated further.
(.venv) admin@NewLearning#docker stop orders-nginx
orders-nginx
(.venv) admin@NewLearning#python3 agent.py "Check the orders service and investigate if anything is wrong."

=== AI DOCKER INCIDENT TROUBLESHOOTING AGENT ===
Model: gpt-5.6-luna
Incident: Check the orders service and investigate if anything is wrong.

[Agent Step 1] Thinking / selecting evidence...
[Tool Action] list_containers({})
[Observation] {
  "status": "OK",
  "containers": [
    {
      "name": "payments-nginx",
      "status": "Up 6 minutes",
      "image": "nginx:alpine"
    },
    {
      "name": "orders-nginx",
      "status": "Exited (0) 25 seconds ago",
      "image": "nginx:alpine"
    },
    {
      "name": "buildx_buildkit_serene_euler0",
      "status": "Exited (137) 4 months ago",
      "image": "moby/buildkit:buildx-stable-1"
    }
  ]
}
[Agent Step 2] Thinking / selecting evidence...
[Tool Action] inspect_container({"container_name":"orders-nginx"})
[Observation] {
  "status": "FOUND",
  "container": "orders-nginx",
  "image": "nginx:alpine",
  "state": "exited",
  "running": false,
  "exit_code": 0,
  "restart_count": 0,
  "health": "not_configured",
  "started_at": "2026-08-26T05:24:08.306947012Z",
  "finished_at": "2026-08-26T05:30:37.347598387Z"
}
[Agent Step 3] Thinking / selecting evidence...
[Tool Action] get_container_logs({"container_name":"orders-nginx","tail":100})
[Observation] {
  "status": "OK",
  "container": "orders-nginx",
  "tail": 100,
  "logs": "/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration\n/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh\n10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf\n10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf\n/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh\n/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh\n/docker-entrypoint.sh: Configuration complete; ready for start up\n192.168.65.1 - - [26/Aug/2026:05:27:21 +0000] \"GET / HTTP/1.1\" 200 82 \"-\" \"curl/8.7.1\" \"-\""
}
[Agent Step 4] Thinking / selecting evidence...

=== FINAL INVESTIGATION ===
## Incident
The `orders-nginx` service is currently stopped and unavailable.

## Evidence
- Container status: `Exited (0)` approximately 25 seconds ago.
- Running: `false`
- Exit code: `0`
- Restart count: `0`
- Health check: `not_configured`
- Logs show normal Nginx startup and configuration completion.
- A prior `GET /` request returned HTTP `200`.

## Likely cause
The container terminated cleanly rather than crashing. The available evidence does not identify why it stopped; no error appears in the recent logs.

## Recommended next steps
- Check the deployment/orchestrator configuration and container lifecycle events to determine what requested the stop.
- Configure a health check and restart policy if the service is expected to remain continuously available.
- Verify the service after it is started again.
(.venv) admin@NewLearning#

## Resume

Built an LLM-driven ReAct-based Docker Incident Troubleshooting Agent using OpenAI Function Calling to discover affected containers, analyze stopped/exited states, exit codes, restart behaviour, logs and HTTP availability, and provide evidence-based DevOps troubleshooting recommendations.
