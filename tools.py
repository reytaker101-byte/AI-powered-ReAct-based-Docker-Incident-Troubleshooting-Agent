import json
import subprocess
import urllib.request


def _run_docker(args):
    """
    Execute a Docker CLI command safely and return
    exit code, stdout and stderr.
    """
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=15,
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except Exception as exc:
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": str(exc),
        }


# ============================================================
# TOOL 1: LIST CONTAINERS
# ============================================================

def list_containers():
    """
    List all Docker containers, including running and stopped ones.
    """

    result = _run_docker(
        [
            "ps",
            "-a",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Image}}",
        ]
    )

    if result["exit_code"] != 0:
        return json.dumps(
            {
                "status": "ERROR",
                "message": "Docker command failed",
                "details": result["stderr"],
            },
            indent=2,
        )

    containers = []

    for line in result["stdout"].splitlines():

        parts = line.split("|", 2)

        if len(parts) == 3:

            containers.append(
                {
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2],
                }
            )

    return json.dumps(
        {
            "status": "OK",
            "containers": containers,
        },
        indent=2,
    )


# ============================================================
# TOOL 2: INSPECT CONTAINER
# ============================================================

def inspect_container(container_name: str):
    """
    Inspect a Docker container and return its state,
    health, exit code and restart count.
    """

    result = _run_docker(
        [
            "inspect",
            container_name,
        ]
    )

    if result["exit_code"] != 0:

        return json.dumps(
            {
                "status": "NOT_FOUND",
                "container": container_name,
                "message": "Container was not found. Do not guess its state.",
                "docker_error": result["stderr"],
            },
            indent=2,
        )

    try:

        data = json.loads(result["stdout"])[0]

        state = data.get("State", {})

        return json.dumps(
            {
                "status": "FOUND",
                "container": data.get("Name", "").lstrip("/"),
                "image": data.get("Config", {}).get("Image"),
                "state": state.get("Status"),
                "running": state.get("Running"),
                "exit_code": state.get("ExitCode"),
                "restart_count": data.get("RestartCount"),
                "health": state.get(
                    "Health",
                    {}
                ).get(
                    "Status",
                    "not_configured",
                ),
                "started_at": state.get("StartedAt"),
                "finished_at": state.get("FinishedAt"),
            },
            indent=2,
        )

    except (json.JSONDecodeError, IndexError) as exc:

        return json.dumps(
            {
                "status": "ERROR",
                "message": "Could not parse Docker inspect output",
                "details": str(exc),
            },
            indent=2,
        )


# ============================================================
# TOOL 3: GET CONTAINER LOGS
# ============================================================

def get_container_logs(
    container_name: str,
    tail: int = 50,
):
    """
    Read recent logs from a Docker container.
    """

    result = _run_docker(
        [
            "logs",
            "--tail",
            str(tail),
            container_name,
        ]
    )

    if result["exit_code"] != 0:

        return json.dumps(
            {
                "status": "ERROR",
                "container": container_name,
                "message": "Could not read logs.",
                "docker_error": result["stderr"],
            },
            indent=2,
        )

    return json.dumps(
        {
            "status": "OK",
            "container": container_name,
            "tail": tail,
            "logs": result["stdout"][-12000:],
        },
        indent=2,
    )


# ============================================================
# TOOL 4: START CONTAINER
# ============================================================

def start_container(container_name: str):
    """
    Start a Docker container only when it is stopped/exited.

    This tool first checks the container state.
    It will NOT start an already-running container.
    """

    print(
        f"-> TOOL: Checking whether {container_name} can be started..."
    )

    # --------------------------------------------------------
    # First inspect the container
    # --------------------------------------------------------

    inspect_result = _run_docker(
        [
            "inspect",
            container_name,
        ]
    )

    if inspect_result["exit_code"] != 0:

        return json.dumps(
            {
                "status": "NOT_FOUND",
                "container": container_name,
                "message": "Container does not exist. Nothing was started.",
            },
            indent=2,
        )

    try:

        data = json.loads(inspect_result["stdout"])[0]

        state = data.get("State", {})

        current_state = state.get("Status")
        running = state.get("Running")

    except Exception as exc:

        return json.dumps(
            {
                "status": "ERROR",
                "message": "Could not determine container state.",
                "details": str(exc),
            },
            indent=2,
        )

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if running:

        return json.dumps(
            {
                "status": "ALREADY_RUNNING",
                "container": container_name,
                "state": current_state,
                "message": "Container is already running. No start action taken.",
            },
            indent=2,
        )

    # --------------------------------------------------------
    # Only start stopped/exited containers
    # --------------------------------------------------------

    if current_state not in [
        "exited",
        "created",
    ]:

        return json.dumps(
            {
                "status": "NOT_STARTED",
                "container": container_name,
                "state": current_state,
                "message": (
                    "Container is not in a safe stopped state for "
                    "automatic start. No action taken."
                ),
            },
            indent=2,
        )

    print(
        f"-> TOOL: Starting stopped container {container_name}..."
    )

    result = _run_docker(
        [
            "start",
            container_name,
        ]
    )

    if result["exit_code"] != 0:

        return json.dumps(
            {
                "status": "START_FAILED",
                "container": container_name,
                "message": "Docker failed to start the container.",
                "docker_error": result["stderr"],
            },
            indent=2,
        )

    return json.dumps(
        {
            "status": "STARTED",
            "container": container_name,
            "previous_state": current_state,
            "message": "Container start command completed successfully.",
        },
        indent=2,
    )


# ============================================================
# TOOL 5: CHECK HTTP
# ============================================================

def check_http(url: str):
    """
    Check whether an HTTP endpoint is responding.
    """

    print(
        f"-> TOOL: Checking HTTP endpoint {url}..."
    )

    try:

        request = urllib.request.Request(
            url,
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:

            body = response.read(
                500
            ).decode(
                "utf-8",
                errors="replace",
            )

            return json.dumps(
                {
                    "status": "OK",
                    "url": url,
                    "http_status": response.status,
                    "response": body,
                },
                indent=2,
            )

    except Exception as exc:

        return json.dumps(
            {
                "status": "FAILED",
                "url": url,
                "message": "HTTP endpoint is not responding successfully.",
                "error": str(exc),
            },
            indent=2,
        )


# ============================================================
# AVAILABLE FUNCTIONS
# ============================================================

AVAILABLE_FUNCTIONS = {

    "list_containers":
        list_containers,

    "inspect_container":
        inspect_container,

    "get_container_logs":
        get_container_logs,

    "start_container":
        start_container,

    "check_http":
        check_http,
}
