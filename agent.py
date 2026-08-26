import json
import os
import sys

from openai import OpenAI

from tools import AVAILABLE_FUNCTIONS


# ============================================================
# MODEL
# ============================================================

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)


# ============================================================
# OPENAI TOOLS
# ============================================================

TOOLS = [

    # --------------------------------------------------------
    # TOOL 1: LIST CONTAINERS
    # --------------------------------------------------------

    {
        "type": "function",
        "name": "list_containers",

        "description":
            "List all Docker containers including running "
            "and stopped containers.",

        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },

        "strict": True,
    },


    # --------------------------------------------------------
    # TOOL 2: INSPECT CONTAINER
    # --------------------------------------------------------

    {
        "type": "function",
        "name": "inspect_container",

        "description":
            "Inspect a Docker container to determine "
            "whether it is running, exited or stopped. "
            "Also return exit code, restart count and health status.",

        "parameters": {

            "type": "object",

            "properties": {

                "container_name": {
                    "type": "string",
                    "description":
                        "Exact Docker container name.",
                },

            },

            "required": [
                "container_name"
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },


    # --------------------------------------------------------
    # TOOL 3: LOGS
    # --------------------------------------------------------

    {
        "type": "function",
        "name": "get_container_logs",

        "description":
            "Read recent Docker logs from a container "
            "to investigate errors or failures.",

        "parameters": {

            "type": "object",

            "properties": {

                "container_name": {
                    "type": "string",
                    "description":
                        "Exact Docker container name.",
                },

                "tail": {
                    "type": "integer",
                    "description":
                        "Number of recent log lines to read.",
                },

            },

            "required": [
                "container_name",
                "tail",
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },


    # --------------------------------------------------------
    # TOOL 4: START CONTAINER
    # --------------------------------------------------------

    {
        "type": "function",
        "name": "start_container",

        "description":
            "Start a Docker container only when evidence "
            "confirms that it is stopped or exited. "
            "Do not use this tool for an already-running container.",

        "parameters": {

            "type": "object",

            "properties": {

                "container_name": {
                    "type": "string",
                    "description":
                        "Exact Docker container name.",
                },

            },

            "required": [
                "container_name"
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },


    # --------------------------------------------------------
    # TOOL 5: HTTP CHECK
    # --------------------------------------------------------

    {
        "type": "function",
        "name": "check_http",

        "description":
            "Check whether an HTTP endpoint is responding "
            "successfully after a container is started.",

        "parameters": {

            "type": "object",

            "properties": {

                "url": {
                    "type": "string",
                    "description":
                        "HTTP URL to check.",
                },

            },

            "required": [
                "url"
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are an AI DevOps Incident Troubleshooting Agent.

Your job is to investigate Docker-based microservice incidents
using real Docker evidence and take a limited safe remediation
action when appropriate.

IMPORTANT:

Never invent container names, statuses, logs, errors or causes.

Use a ReAct-style investigation:

1. REASON
2. ACTION -> call a Docker tool
3. OBSERVE the tool result
4. REASON again
5. Take the next appropriate action
6. VERIFY the result
7. Give the final incident summary


============================================================
INVESTIGATION FLOW
============================================================

When the user asks to investigate a service:

STEP 1:
Call list_containers() if the affected container is not known.

STEP 2:
Identify the relevant container from the available evidence.

STEP 3:
Call inspect_container().

STEP 4:
If the container is running:

    - Read logs if useful.
    - Determine whether there is an actual problem.
    - Do NOT restart a healthy container.

STEP 5:
If the container state is "exited" or "created"
and running=false:

    - Treat this as a service availability incident.
    - Call start_container().

STEP 6:
After starting the container:

    - Call inspect_container() again.
    - Confirm running=true.

STEP 7:
If an HTTP endpoint is available for the service:

    - Call check_http().
    - Verify that the service returns a successful HTTP response.

STEP 8:
Only after verification say that the service has been restored.

============================================================
IMPORTANT SAFETY RULES
============================================================

- Never start an already-running container.
- Never restart a healthy container.
- Never claim a container was started unless the tool confirms it.
- Never claim the service is healthy without verification.
- If start_container fails, report the failure.
- If HTTP verification fails, report that the container started
  but service verification failed.
- If the container does not exist, say "Not found".
- Do not guess a root cause.
- Separate FACTS from INFERENCE.

============================================================
FINAL RESPONSE FORMAT
============================================================

Incident:
<what happened>

Evidence:
<facts returned by Docker/tools>

Action Taken:
<what the agent actually did>

Verification:
<post-action verification>

Likely Cause:
<only if evidence supports it>

Final Status:
<Resolved / Still Investigating / Escalation Required>

Next Steps:
<recommended actions if required>

"""


# ============================================================
# AGENT
# ============================================================

def run_agent(user_prompt: str):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Export it before running the agent."
        )


    client = OpenAI(
        api_key=api_key
    )


    conversation = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]


    print(
        "\n=== AI DOCKER INCIDENT TROUBLESHOOTING AGENT ==="
    )

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Incident: {user_prompt}\n"
    )


    # Maximum number of ReAct iterations
    for step in range(1, 8):

        print(
            f"[Agent Step {step}] "
            "Thinking / selecting evidence..."
        )


        response = client.responses.create(

            model=MODEL,

            instructions=SYSTEM_PROMPT,

            input=conversation,

            tools=TOOLS,
        )


        # Preserve model output for next iteration
        conversation.extend(
            response.output
        )


        # Find tool calls
        function_calls = [

            item

            for item in response.output

            if item.type == "function_call"
        ]


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        if not function_calls:

            print(
                "\n=== FINAL INVESTIGATION ==="
            )

            print(
                response.output_text
            )

            return response.output_text


        # ----------------------------------------------------
        # EXECUTE TOOL CALLS
        # ----------------------------------------------------

        for call in function_calls:

            print(
                f"[Tool Action] "
                f"{call.name}({call.arguments})"
            )


            try:

                args = json.loads(
                    call.arguments
                )


                function_to_call = (
                    AVAILABLE_FUNCTIONS.get(
                        call.name
                    )
                )


                if not function_to_call:

                    result = json.dumps(
                        {
                            "status": "ERROR",
                            "message":
                                f"Unknown tool: {call.name}",
                        }
                    )

                else:

                    result = function_to_call(
                        **args
                    )


            except Exception as exc:

                result = json.dumps(
                    {
                        "status": "ERROR",
                        "message":
                            "Tool execution failed",
                        "details":
                            str(exc),
                    }
                )


            print(
                f"[Observation] "
                f"{result[:1500]}"
            )


            if len(result) > 1500:

                print(
                    "[Observation] "
                    "...truncated on screen."
                )


            # Send tool result back to LLM
            conversation.append(
                {
                    "type":
                        "function_call_output",

                    "call_id":
                        call.call_id,

                    "output":
                        result,
                }
            )


    raise RuntimeError(
        "Agent stopped after maximum investigation steps."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    prompt = " ".join(
        sys.argv[1:]
    ).strip()


    if not prompt:

        prompt = (
            "Check the orders service and "
            "investigate if anything is wrong."
        )


    run_agent(
        prompt
    )
