import json
import subprocess
import urllib.request
import urllib.error

def _run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as exc:
        return {"exit_code": 1, "stdout": "", "stderr": str(exc)}

def list_containers():
    result = _run_command(["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"])
    if result["exit_code"] != 0:
        return json.dumps({"status":"ERROR","message":"Docker command failed.","details":result["stderr"]}, indent=2)
    containers=[]
    for line in result["stdout"].splitlines():
        parts=line.split("|",2)
        if len(parts)==3:
            containers.append({"name":parts[0],"status":parts[1],"image":parts[2]})
    return json.dumps({"status":"OK","containers":containers}, indent=2)

def inspect_container(container_name: str):
    result=_run_command(["docker","inspect",container_name])
    if result["exit_code"] != 0:
        return json.dumps({"status":"NOT_FOUND","container":container_name,"message":"Container was not found. Do not guess its state.","docker_error":result["stderr"]}, indent=2)
    try:
        data=json.loads(result["stdout"])[0]; state=data.get("State",{})
        return json.dumps({"status":"FOUND","container":data.get("Name","").lstrip("/"),"image":data.get("Config",{}).get("Image"),"state":state.get("Status"),"running":state.get("Running"),"exit_code":state.get("ExitCode"),"restart_count":data.get("RestartCount"),"health":state.get("Health",{}).get("Status","not_configured"),"started_at":state.get("StartedAt"),"finished_at":state.get("FinishedAt")}, indent=2)
    except (json.JSONDecodeError,IndexError) as exc:
        return json.dumps({"status":"ERROR","message":"Could not parse docker inspect output.","details":str(exc)}, indent=2)

def get_container_logs(container_name: str, tail: int=50):
    tail=max(1,min(tail,200))
    result=_run_command(["docker","logs","--tail",str(tail),container_name])
    if result["exit_code"] != 0:
        return json.dumps({"status":"ERROR","container":container_name,"message":"Could not read logs.","docker_error":result["stderr"]}, indent=2)
    return json.dumps({"status":"OK","container":container_name,"tail":tail,"logs":result["stdout"][-15000:]}, indent=2)

def check_http(url: str):
    try:
        req=urllib.request.Request(url,method="GET",headers={"User-Agent":"AI-Docker-Incident-Agent/1.0"})
        with urllib.request.urlopen(req,timeout=5) as response:
            body=response.read(500).decode("utf-8",errors="replace")
            return json.dumps({"status":"OK","url":url,"http_status":response.status,"reachable":True,"response_preview":body}, indent=2)
    except urllib.error.HTTPError as exc:
        return json.dumps({"status":"HTTP_ERROR","url":url,"http_status":exc.code,"reachable":True,"message":str(exc)}, indent=2)
    except Exception as exc:
        return json.dumps({"status":"UNREACHABLE","url":url,"reachable":False,"message":str(exc)}, indent=2)

AVAILABLE_FUNCTIONS={"list_containers":list_containers,"inspect_container":inspect_container,"get_container_logs":get_container_logs,"check_http":check_http}
