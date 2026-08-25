import json
import os
import sys
from openai import OpenAI
from tools import AVAILABLE_FUNCTIONS

MODEL=os.getenv("OPENAI_MODEL","gpt-5.6-luna")
TOOLS=[
 {"type":"function","name":"list_containers","description":"List all Docker containers, including running and stopped containers. Use this first when the affected container is unknown.","parameters":{"type":"object","properties":{},"required":[],"additionalProperties":False},"strict":True},
 {"type":"function","name":"inspect_container","description":"Inspect a Docker container and return state, running flag, exit code, restart count and health status.","parameters":{"type":"object","properties":{"container_name":{"type":"string","description":"Exact Docker container name."}},"required":["container_name"],"additionalProperties":False},"strict":True},
 {"type":"function","name":"get_container_logs","description":"Read recent Docker logs from a container as evidence for troubleshooting.","parameters":{"type":"object","properties":{"container_name":{"type":"string","description":"Exact Docker container name."},"tail":{"type":"integer","description":"Number of recent log lines to inspect."}},"required":["container_name","tail"],"additionalProperties":False},"strict":True},
 {"type":"function","name":"check_http","description":"Check whether a local HTTP endpoint is reachable. Use when a container is running but service availability is uncertain.","parameters":{"type":"object","properties":{"url":{"type":"string","description":"HTTP URL to check, for example http://localhost:8081."}},"required":["url"],"additionalProperties":False},"strict":True},
]
SYSTEM_PROMPT="""You are a DevOps Container Incident Troubleshooting Agent. Investigate Docker incidents using ONLY evidence returned by tools. Never invent container names, states, errors, logs, or root causes. Use a ReAct-style loop: reason about missing evidence, select a read-only tool, observe, repeat when needed, then produce a concise report. If the affected container is unknown, call list_containers first. Inspect before diagnosing. If exited/stopped/inactive, inspect exit code, restart count and logs. If running but availability is uncertain, use check_http when a URL/port is available. Distinguish FACTS from INFERENCE. If evidence is insufficient, say so. Do not restart, delete, modify, or recreate containers. Final response must contain Incident, Evidence, Likely cause, Recommended next steps."""

def run_agent(user_prompt:str):
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key: raise RuntimeError("OPENAI_API_KEY is not set. Export it before running the agent.")
    client=OpenAI(api_key=api_key); conversation=[{"role":"user","content":user_prompt}]
    print("\n=== AI DOCKER INCIDENT TROUBLESHOOTING AGENT ==="); print(f"Model: {MODEL}"); print(f"Incident: {user_prompt}\n")
    for step in range(1,8):
        print(f"[Agent Step {step}] Thinking / selecting evidence...")
        response=client.responses.create(model=MODEL,instructions=SYSTEM_PROMPT,input=conversation,tools=TOOLS)
        conversation.extend(response.output)
        calls=[item for item in response.output if item.type=="function_call"]
        if not calls:
            print("\n=== FINAL INVESTIGATION ==="); print(response.output_text); return response.output_text
        for call in calls:
            print(f"[Tool Action] {call.name}({call.arguments})")
            try:
                args=json.loads(call.arguments); fn=AVAILABLE_FUNCTIONS.get(call.name)
                result=json.dumps({"error":f"Unknown tool: {call.name}"}) if not fn else fn(**args)
            except Exception as exc:
                result=json.dumps({"error":"Tool execution failed","details":str(exc)})
            print(f"[Observation] {result[:1200]}")
            if len(result)>1200: print("[Observation] ...truncated on screen; full result was sent to the model.")
            conversation.append({"type":"function_call_output","call_id":call.call_id,"output":result})
    raise RuntimeError("Agent stopped after 7 investigation steps. Try a narrower incident prompt.")

if __name__=="__main__":
    prompt=" ".join(sys.argv[1:]).strip() or "Investigate why the orders service is unavailable. Find the affected Docker container, collect evidence, and recommend troubleshooting steps. Do not restart anything."
    run_agent(prompt)
