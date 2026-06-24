#!/usr/bin/env python3
from __future__ import annotations
"""
engine.py — BugHunter Pro v4.0 (Combined Edition)
Standalone CLI. Works WITHOUT Claude Code or any AI subscription.

Providers (auto-detected, first available wins):
  FREE:  ollama, groq, deepseek
  PAID:  claude, openai, grok, gemini, mistral, together, cerebras, perplexity

13-Phase Recon Pipeline:
  1. Passive Subs   2. DNS + Permutations   3. HTTP Probing   4. Port Scanning
  5. Content Discovery  6. Parameter Discovery  7. JS Deep Recon
  8. GraphQL           9. API Fuzzing       10. Google Dorks   11. Vuln Scanning
  12. Cloud Assets    13. GitHub Secrets

Usage:
  ./engine.py setup                        one-time config wizard
  ./engine.py recon  <target>              recon (phases 1-7)
  ./engine.py deep   <target>              full deep recon (phases 1-13)
  ./engine.py hunt   <target>              full hunt pipeline
  ./engine.py js     <target>              JS deep recon only (phase 7)
  ./engine.py validate "<finding>"         7-Question Gate on a finding
  ./engine.py report [--findings-dir DIR]  write submission-ready report
  ./engine.py chain [--findings-dir DIR]   build exploit chain
  ./engine.py triage "<finding>"           fast triage (pass/kill/downgrade)
  ./engine.py chat                         interactive Q&A shell
  ./engine.py models                       list available models
  ./engine.py status                       show hunt status
  ./engine.py providers                    show all providers + API key status
  ./engine.py phase <N> <target>           run single phase (1-13)
"""

import argparse, json, os, re, subprocess, sys, textwrap, time, hashlib, shutil
import urllib.request, urllib.error, urllib.parse
from pathlib import Path
from datetime import datetime

HERE     = Path(__file__).resolve().parent
AGENTS   = HERE / "agents"
TOOLS    = HERE / "tools"
RECON    = HERE / "recon"
FINDINGS = HERE / "findings"
REPORTS  = HERE / "reports"
CONFIG   = Path.home() / ".bughunter-pro" / "config.json"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";     DIM    = "\033[2m"
NC     = "\033[0m";    MAGENTA= "\033[0;35m"

def ok(msg):   print(f"{GREEN}{BOLD}[+]{NC} {msg}")
def info(msg): print(f"{CYAN}{BOLD}[*]{NC} {msg}")
def warn(msg): print(f"{YELLOW}{BOLD}[!]{NC} {msg}")
def err(msg):  print(f"{RED}{BOLD}[-]{NC} {msg}")
def hit(msg):  print(f"{MAGENTA}{BOLD}[HIT]{NC} {msg}")

def header(title):
    width = max(len(title) + 4, 60)
    print(f"\n{BOLD}{'═' * width}{NC}")
    print(f"{BOLD}  {title}{NC}")
    print(f"{BOLD}{'═' * width}{NC}\n")

def load_config() -> dict:
    if CONFIG.exists():
        try: return json.loads(CONFIG.read_text())
        except Exception: pass
    return {}

def save_config(cfg: dict):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2))

COMMAND_ALIASES = {
    "setup": {"setup", "init"},
    "providers": {"providers", "p"},
    "models": {"models", "m"},
    "status": {"status", "s"},
    "chat": {"chat", "ask"},
    "recon": {"recon", "r"},
    "deep": {"deep", "full", "f"},
    "hunt": {"hunt", "h"},
    "js": {"js", "j"},
    "validate": {"validate", "v"},
    "triage": {"triage", "t"},
    "report": {"report", "rep"},
    "chain": {"chain", "c"},
    "phase": {"phase"},
}

def _print_quick_help():
    print(textwrap.dedent("""
    BugHunter Pro — fast commands

    bughunter-pro setup               Configure your AI provider
    bughunter-pro recon target.com    Recon (phases 1-7: subs, DNS, HTTP, ports, content, params, JS)
    bughunter-pro deep target.com     Full deep recon (all 13 phases)
    bughunter-pro js target.com       JS deep recon only
    bughunter-pro hunt target.com     Run full hunt pipeline with AI
    bughunter-pro validate "finding"  Run the 7-Question Gate
    bughunter-pro report              Write a submission-ready report
    bughunter-pro phase <N> <target>  Run single phase (1-13)

    Short: init=setup  r=recon  f=full/h=deep  j=js  v=validate  rep=report
    """).strip())

def _normalize_cli_argv(argv):
    if not argv: return argv
    if argv[0] in {"help", "-help"}: return ["--help", *argv[1:]]
    return ["--help" if item == "-help" else item for item in argv]

def load_agent_prompt(agent_name):
    md = AGENTS / f"{agent_name}.md"
    if not md.exists(): return ""
    text = md.read_text()
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1: text = text[end + 3:].lstrip()
    return text.strip()

def _import_brain():
    sys.path.insert(0, str(HERE))
    try:
        from brain import Brain, LLMClient
        return Brain, LLMClient
    except ImportError as e:
        err(f"Could not import brain.py: {e}")
        sys.exit(1)

def _get_client(provider=None):
    _, LLMClient = _import_brain()
    cfg = load_config()
    if not provider and not os.environ.get("BRAIN_PROVIDER"):
        provider = cfg.get("provider")
    if provider: os.environ["BRAIN_PROVIDER"] = provider
    return LLMClient(provider)

def _get_brain(provider=None):
    Brain, _ = _import_brain()
    cfg = load_config()
    if not provider and not os.environ.get("BRAIN_PROVIDER"):
        provider = cfg.get("provider")
    if provider: os.environ["BRAIN_PROVIDER"] = provider
    return Brain()

def _run_shell(cmd, cwd=None, timeout=3600):
    try:
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd or str(HERE),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        for line in proc.stdout:
            print(line, end="", flush=True)
            lines.append(line)
        proc.wait(timeout=timeout)
        return proc.returncode == 0, "".join(lines)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "timed out"
    except Exception as e:
        return False, str(e)

# ─── Commands ──────────────────────────────────────────────────

def cmd_setup(args):
    header("BugHunter Pro Setup")
    providers = {
        "1": ("ollama",   "Ollama (local, FREE)        — needs ollama running locally"),
        "2": ("groq",     "Groq (cloud, FREE tier)     — needs GROQ_API_KEY"),
        "3": ("deepseek", "DeepSeek (cloud, very cheap) — needs DEEPSEEK_API_KEY"),
        "4": ("claude",   "Claude (paid)               — needs ANTHROPIC_API_KEY"),
        "5": ("openai",   "OpenAI (paid)               — needs OPENAI_API_KEY"),
        "6": ("grok",     "Grok/xAI (paid)             — needs XAI_API_KEY"),
    }
    print("Choose your AI backend:\n")
    for k, (_, desc) in providers.items():
        print(f"  {k}) {desc}")
    print()
    choice = input("Enter number [1]: ").strip() or "1"
    provider = providers.get(choice, ("ollama", ""))[0]
    cfg = load_config()
    cfg["provider"] = provider
    if provider == "ollama":
        model = _pick_ollama_model()
        if model:
            cfg["ollama_model"] = model
            ok(f"Model set to: {model}")
    else:
        key_env = {"groq":"GROQ_API_KEY","deepseek":"DEEPSEEK_API_KEY",
                   "claude":"ANTHROPIC_API_KEY","openai":"OPENAI_API_KEY","grok":"XAI_API_KEY"}
        env_key = key_env.get(provider, "")
        current = os.environ.get(env_key, "")
        if not current:
            val = input(f"Enter your {env_key} [skip]: ").strip()
            if val: os.environ[env_key] = val
    save_config(cfg)
    ok(f"Provider set to: {provider}")
    ok("Config saved to ~/.bughunter-pro/config.json")

def _pick_ollama_model():
    try:
        import urllib.request, json
        req = urllib.request.Request("http://localhost:11434/api/tags")
        data = json.loads(urllib.request.urlopen(req, timeout=5).read())
        models = [m.get("name","") for m in data.get("models",[])]
        if not models:
            info("No Ollama models found. Pull one: ollama pull qwen3:4b")
            return input("Enter model name [qwen3:4b]: ").strip() or "qwen3:4b"
        if len(models) == 1:
            return models[0]
        print("\nAvailable models:")
        for i, m in enumerate(models, 1):
            print(f"  {i}) {m}")
        choice = input(f"Enter number [1]: ").strip() or "1"
        return models[int(choice)-1]
    except Exception as e:
        info(f"Could not reach Ollama: {e}")
        return input("Enter model name [qwen3:4b]: ").strip() or "qwen3:4b"

def cmd_providers(args):
    header("Available Providers")
    Brain, _ = _import_brain()
    client = _get_client()
    print(f"  Active provider: {client.provider} ({client.description})")
    print(f"\n  Provider priority: {', '.join(client.PROVIDER_PRIORITY)}")
    print(f"\n  Set provider: export BRAIN_PROVIDER=<name>")
    print(f"  Or run: bughunter-pro setup")

def cmd_models(args):
    header("Available Models")
    client = _get_client()
    try:
        import ollama
        models = ollama.Client().list()
        print("Local Ollama models:")
        for m in models.get("models", []):
            print(f"  {m.get('name', '?')}")
    except Exception:
        info("Ollama not available. Configure a cloud provider via 'bughunter-pro setup'")

def cmd_status(args):
    header("BugHunter Status")
    for d in [RECON, FINDINGS, REPORTS, TARGETS]:
        d.mkdir(exist_ok=True)
        count = len(list(d.iterdir())) if d.exists() else 0
        print(f"  {d.name}/: {count} files")
    cfg = load_config()
    provider = cfg.get("provider", "not configured")
    print(f"  AI Provider: {provider}")
    tools_exists = shutil.which("subfinder") is not None
    print(f"  Recon tools installed: {'Yes' if tools_exists else 'No — run ./install_tools.sh'}")
    print(f"\n  Config: {CONFIG}")

def cmd_recon(args):
    header(f"Recon: {args.target}")
    print(f"  Mode: {'standard' if not args.deep else 'deep'} | AI: {'yes' if not args.no_ai else 'no'}")
    from tools.hunt import print_tool_status
    print_tool_status()
    _run_shell(f'python3 -u "{TOOLS / "hunt.py"}" --target {args.target} {"--deep" if args.deep else ""} {"--quick" if args.quick else ""} {"--no-ai" if args.no_ai else ""}')

def cmd_js(args):
    header(f"JS Deep Recon: {args.target}")
    _run_shell(f'python3 "{TOOLS / "hunt.py"}" --target {args.target} --phase js {"--no-ai" if args.no_ai else ""}')

def cmd_phase(args):
    header(f"Phase {args.phase_num}: {args.target}")
    _run_shell(f'python3 "{TOOLS / "hunt.py"}" --target {args.target} --phase {args.phase_num}')

def cmd_hunt(args):
    header(f"Hunt: {args.target}")
    agent_prompt = load_agent_prompt("autopilot")
    Brain, _ = _import_brain()
    brain = _get_brain()
    info("Starting autonomous hunt pipeline...")
    _run_shell(f'python3 "{TOOLS / "hunt.py"}" --target {args.target} --deep {"--no-ai" if args.no_ai else ""}')

def cmd_validate(args):
    header("Validation Gate")
    _run_shell(f'python3 "{TOOLS / "validate.py"}" "{args.finding}"')

def cmd_triage(args):
    header("Triage")
    Brain, _ = _import_brain()
    brain = _get_brain()
    result = brain.triage_finding(args.finding)
    print(result)

def cmd_report(args):
    header("Report Generation")
    _run_shell(f'python3 "{TOOLS / "validate.py"}" --report {"--findings-dir " + args.findings_dir if args.findings_dir else ""}')

def cmd_chain(args):
    header("Exploit Chain Builder")
    Brain, _ = _import_brain()
    brain = _get_brain()
    result = brain.build_chain(args.findings_dir)
    print(result)

def cmd_chat(args):
    header("Interactive Chat")
    Brain, _ = _import_brain()
    brain = _get_brain()
    print("BugHunter AI Chat. Type 'exit' to quit.\n")
    while True:
        try:
            q = input(f"{CYAN}> {NC}").strip()
            if q.lower() in ("exit", "quit"): break
            if not q: continue
            resp = brain.chat(q)
            print(f"{GREEN}{resp}{NC}\n")
        except (KeyboardInterrupt, EOFError):
            break

COMMANDS = {
    "setup":    cmd_setup,
    "providers": cmd_providers,
    "models":   cmd_models,
    "status":   cmd_status,
    "recon":    cmd_recon,
    "deep":     cmd_recon,
    "hunt":     cmd_hunt,
    "js":       cmd_js,
    "validate": cmd_validate,
    "triage":   cmd_triage,
    "report":   cmd_report,
    "chain":    cmd_chain,
    "chat":     cmd_chat,
    "phase":    cmd_phase,
}

def main():
    argv = _normalize_cli_argv(sys.argv[1:])
    if not argv or argv[0] in ("--help", "-h"):
        _print_quick_help()
        parser.print_help()
        return 0
    parser = argparse.ArgumentParser(
        description="BugHunter Pro — AI-powered bug bounty toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", help="Command: recon|hunt|deep|js|validate|report|setup|chat|phase|...")
    parser.add_argument("target", nargs="?", help="Target domain")
    parser.add_argument("finding", nargs="?", help="Finding description for validation")
    parser.add_argument("phase_num", nargs="?", type=int, help="Phase number (1-13)")
    parser.add_argument("--deep", action="store_true", help="Run full deep recon")
    parser.add_argument("--quick", action="store_true", help="Quick scan mode")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI analysis")
    parser.add_argument("--findings-dir", help="Path to findings directory")
    parser.add_argument("--provider", help="AI provider override")

    args, extra = parser.parse_known_args(argv if argv[0] not in ("--help", "-h") else [])
    cmd = args.command.lower() if args.command else ""

    # Normalize alias
    for canonical, aliases in COMMAND_ALIASES.items():
        if cmd in aliases:
            cmd = canonical
            break

    if cmd == "phase":
        if args.phase_num:
            cmd_phase(args)
        elif extra and extra[0].isdigit():
            args.phase_num = int(extra[0])
            args.target = extra[1] if len(extra) > 1 else None
            cmd_phase(args)
        else:
            err("Usage: bughunter-pro phase <N> <target> (N = 1-13)")
        return 0

    handler = COMMANDS.get(cmd)
    if not handler:
        _print_quick_help()
        return 1
    if cmd == "deep":
        args.deep = True
    handler(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
