#!/usr/bin/env python3
from __future__ import annotations
"""
agent.py — LangGraph-style ReAct hunting agent with 13-phase pipeline support.

Architecture:
  ReAct loop: Observe → Think → Act → Observe → loop
  13-phase toolset integrated from BugHunter Pro v4.0

Usage:
  python3 agent.py --target example.com
  python3 agent.py --target example.com --phase 7       # Single phase
  python3 agent.py --target example.com --deep           # All 13 phases
  python3 agent.py --target example.com --langgraph      # Force LangGraph
"""

import argparse, json, os, sys, time, traceback
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
    from langchain_core.tools import tool as lc_tool
    try: from langchain_ollama import ChatOllama
    except: from langchain_community.chat_models import ChatOllama
    _LANGGRAPH_OK = True
except ImportError:
    _LANGGRAPH_OK = False

try:
    import ollama
    _OLLAMA_OK = True
except ImportError:
    _ollama_lib = None
    _OLLAMA_OK = False

HERE = Path(__file__).resolve().parent.parent

# ── Tool definitions (JSON Schema for Ollama native tool calling) ──

def build_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "run_passive_subs",
                "description": "Phase 1: Enumerate passive subdomains (subfinder, assetfinder, amass, crt.sh, gau, waybackurls)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_dns_resolve",
                "description": "Phase 2: DNS resolution + permutations (puredns, altdns, gotator, CNAME takeover check)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_http_probe",
                "description": "Phase 3: HTTP probing + tech fingerprinting + screenshots (httpx, wafw00f, gowitness)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_port_scan",
                "description": "Phase 4: Port scanning + dangerous service detection (naabu, nmap)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_content_discovery",
                "description": "Phase 5: Content discovery + sensitive file probing (katana, gau, feroxbuster, kiterunner)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_param_discovery",
                "description": "Phase 6: Parameter discovery for SSRF, redirect, XSS, IDOR",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_js_recon",
                "description": "Phase 7: JS deep recon — download JS, source maps, extract endpoints, scan secrets (70+ patterns + entropy)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_graphql_scan",
                "description": "Phase 8: GraphQL detection + introspection probing",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_api_fuzz",
                "description": "Phase 9: API path discovery + fuzzing + HTTP method testing",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_google_dorks",
                "description": "Phase 10: Generate Google dorks + GitHub dorks for manual searching",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_vuln_scan",
                "description": "Phase 11: Vulnerability scanning (nuclei CVEs, panels, default creds, CORS, CRLF, open redirect, 403 bypass, dalfox XSS)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_cloud_scan",
                "description": "Phase 12: Cloud asset discovery (S3 buckets, Firebase, GCP storage, Azure blobs)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_github_scan",
                "description": "Phase 13: GitHub secret scanning (TruffleHog, gitleaks)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_ai_js_analysis",
                "description": "AI-powered JS secret analysis using LLM (catches what regex misses)",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_recon",
                "description": "Run full recon (phases 1-7): subdomain enum + DNS + HTTP + ports + content + params + JS",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"},"quick":{"type":"boolean","description":"Quick mode (phases 1-5)"}},"required":["target"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_deep_recon",
                "description": "Run ALL 13 phases: full recon + GraphQL + API fuzz + dorks + vulns + cloud + GitHub",
                "parameters": {"type":"object","properties":{"target":{"type":"string","description":"Target domain"}},"required":["target"]},
            },
        },
    ]

TOOLS = build_tools()
MAX_OBS_CHARS = 3000; MAX_CTX_CHARS = 18000; MAX_FINDINGS_LOG = 200; MEMORY_REFRESH_N = 5

GREEN="\033[0;32m"; CYAN="\033[0;36m"; YELLOW="\033[1;33m"; RED="\033[0;31m"
MAGENTA="\033[0;35m"; BOLD="\033[1m"; DIM="\033[2m"; NC="\033[0m"

def ok(msg): print(f"{GREEN}{BOLD}[+]{NC} {msg}")
def info(msg): print(f"{CYAN}{BOLD}[*]{NC} {msg}")
def warn(msg): print(f"{YELLOW}{BOLD}[!]{NC} {msg}")

class HuntingAgent:
    """ReAct-style autonomous hunting agent with 13-phase toolset."""

    def __init__(self, target, cookie=None, deep=False, no_brain=False):
        self.target = target
        self.cookie = cookie
        self.deep = deep
        self.no_brain = no_brain
        self.working_memory = ""
        self.findings_log = []
        self.observation_buf = []
        self.step = 0
        self.session_file = HERE / "hunt_sessions" / f"{target.replace('.','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        (HERE / "hunt_sessions").mkdir(exist_ok=True)

    def _call_tool(self, tool_name, args):
        info(f"Agent executing: {tool_name}({json.dumps(args)})")
        try:
            if tool_name == "run_passive_subs":
                from tools.hunt import phase_passive_subs
                return phase_passive_subs(args.get("target"), None)
            elif tool_name == "run_dns_resolve":
                from tools.hunt import phase_dns
                return phase_dns(args.get("target"), None)
            elif tool_name == "run_http_probe":
                from tools.hunt import phase_http
                return phase_http(args.get("target"), None)
            elif tool_name == "run_port_scan":
                from tools.hunt import phase_ports
                return phase_ports(args.get("target"), None)
            elif tool_name == "run_content_discovery":
                from tools.hunt import phase_content
                return phase_content(args.get("target"), None, self.cookie)
            elif tool_name == "run_param_discovery":
                from tools.hunt import phase_params
                return phase_params(args.get("target"), None)
            elif tool_name == "run_js_recon":
                from tools.hunt import phase_js
                return phase_js(args.get("target"), None)
            elif tool_name == "run_graphql_scan":
                from tools.hunt import phase_graphql
                return phase_graphql(args.get("target"), None)
            elif tool_name == "run_api_fuzz":
                from tools.hunt import phase_api_fuzz
                return phase_api_fuzz(args.get("target"), None)
            elif tool_name == "run_google_dorks":
                from tools.hunt import phase_dorks
                return phase_dorks(args.get("target"), None)
            elif tool_name == "run_vuln_scan":
                from tools.hunt import phase_vulns
                return phase_vulns(args.get("target"), None)
            elif tool_name == "run_cloud_scan":
                from tools.hunt import phase_cloud
                return phase_cloud(args.get("target"), None)
            elif tool_name == "run_github_scan":
                from tools.hunt import phase_github
                return phase_github(args.get("target"), None)
            else:
                return f"Tool {tool_name} not implemented"
        except Exception as e:
            return f"Tool error: {e}"

    def run(self):
        """Main ReAct loop."""
        ok(f"Agent starting on {self.target} (deep={'yes' if self.deep else 'no'})")

        if self.deep:
            phases = [("run_passive_subs",{"target":self.target}),
                     ("run_dns_resolve",{"target":self.target}),
                     ("run_http_probe",{"target":self.target}),
                     ("run_port_scan",{"target":self.target}),
                     ("run_content_discovery",{"target":self.target}),
                     ("run_param_discovery",{"target":self.target}),
                     ("run_js_recon",{"target":self.target}),
                     ("run_graphql_scan",{"target":self.target}),
                     ("run_api_fuzz",{"target":self.target}),
                     ("run_google_dorks",{"target":self.target}),
                     ("run_vuln_scan",{"target":self.target}),
                     ("run_cloud_scan",{"target":self.target}),
                     ("run_github_scan",{"target":self.target})]
        else:
            phases = [("run_passive_subs",{"target":self.target}),
                     ("run_dns_resolve",{"target":self.target}),
                     ("run_http_probe",{"target":self.target}),
                     ("run_port_scan",{"target":self.target}),
                     ("run_content_discovery",{"target":self.target}),
                     ("run_param_discovery",{"target":self.target}),
                     ("run_js_recon",{"target":self.target})]

        for tool_name, tool_args in phases:
            self.step += 1
            info(f"\n{'='*60}\nStep {self.step}: {tool_name}\n{'='*60}")
            result = self._call_tool(tool_name, tool_args)
            self.findings_log.append({"tool":tool_name,"result":str(result)[:200],"timestamp":datetime.now().isoformat()})
            ok(f"{tool_name} complete")

        self._save_session()
        ok(f"Agent finished. {len(self.findings_log)} phases completed.")
        return self.findings_log

    def _save_session(self):
        self.session_file.write_text(json.dumps({
            "target":self.target,"timestamp":datetime.now().isoformat(),
            "steps":self.step,"log":self.findings_log}, indent=2))

def main():
    ap = argparse.ArgumentParser(description="BugHunter Agent — Autonomous 13-Phase Hunting")
    ap.add_argument("--target", required=True, help="Target domain")
    ap.add_argument("--cookie", help="Session cookie")
    ap.add_argument("--deep", action="store_true", help="Run all 13 phases")
    ap.add_argument("--no-brain", action="store_true", help="Skip AI analysis")
    ap.add_argument("--phase", type=int, help="Single phase to run (1-13)")
    ap.add_argument("--langgraph", action="store_true", help="Use LangGraph backend")
    args = ap.parse_args()

    agent = HuntingAgent(args.target, args.cookie, args.deep, args.no_brain)

    if args.phase:
        phase_tools = {1:"run_passive_subs",2:"run_dns_resolve",3:"run_http_probe",
            4:"run_port_scan",5:"run_content_discovery",6:"run_param_discovery",
            7:"run_js_recon",8:"run_graphql_scan",9:"run_api_fuzz",
            10:"run_google_dorks",11:"run_vuln_scan",12:"run_cloud_scan",13:"run_github_scan"}
        tool_name = phase_tools.get(args.phase)
        if tool_name:
            result = agent._call_tool(tool_name, {"target":args.target})
            print(f"Result: {result[:500]}")
        return 0

    agent.run()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
