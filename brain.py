#!/usr/bin/env python3
from __future__ import annotations
"""
Brain — Multi-Provider LLM Reasoning Layer for Bug Bounty & VAPT
Supports: Ollama (local), Claude, OpenAI, Grok, Groq, DeepSeek,
          Gemini, Kimi, Mistral, Together AI, Cerebras, Perplexity

Integrates batch JS secret scanning from BugHunter Pro v4.0.
"""

import argparse, json, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# ── Multi-provider LLM client ──────────────────────────────────

class LLMClient:
    PROVIDER_PRIORITY = [
        "ollama", "groq", "deepseek", "cerebras",
        "gemini", "kimi", "mistral", "together",
        "perplexity", "claude", "openai", "grok",
    ]
    DEFAULT_MODELS = {
        "claude":"claude-sonnet-4-6","openai":"gpt-4o","grok":"grok-2-latest",
        "groq":"llama-3.3-70b-versatile","deepseek":"deepseek-chat",
        "gemini":"gemini-2.0-flash","kimi":"moonshot-v1-128k",
        "mistral":"mistral-large-latest","together":"meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "cerebras":"llama3.3-70b","perplexity":"sonar-pro","ollama":None,
    }
    PROVIDER_KEY_ENV = {
        "claude":"ANTHROPIC_API_KEY","openai":"OPENAI_API_KEY","grok":"XAI_API_KEY",
        "groq":"GROQ_API_KEY","deepseek":"DEEPSEEK_API_KEY","gemini":"GEMINI_API_KEY",
        "kimi":"MOONSHOT_API_KEY","mistral":"MISTRAL_API_KEY","together":"TOGETHER_API_KEY",
        "cerebras":"CEREBRAS_API_KEY","perplexity":"PERPLEXITY_API_KEY",
    }

    def __init__(self, provider=None):
        self.provider = (provider or os.environ.get("BRAIN_PROVIDER","")).lower()
        self.model = None
        if not self.provider:
            cfg_path = Path.home() / ".bughunter-pro" / "config.json"
            if cfg_path.exists():
                try:
                    cfg = json.loads(cfg_path.read_text())
                    self.provider = cfg.get("provider", "").lower()
                    self.model = cfg.get("ollama_model") or None
                except: pass
        self.available = False; self.description = ""
        if not self.provider: self.provider = self._auto_detect()
        else: self._init_provider(self.provider)

    def _auto_detect(self):
        key_providers = [p for p,env in self.PROVIDER_KEY_ENV.items() if os.environ.get(env)]
        rest = [p for p in self.PROVIDER_PRIORITY if p not in key_providers]
        for p in key_providers + rest:
            try:
                self._init_provider(p)
                if self.available: return p
            except: pass
        return "ollama"

    def _init_provider(self, provider):
        self.available = False
        if provider == "ollama":
            try:
                req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
                urllib.request.urlopen(req, timeout=5)
                self.available = True
                self.description = f"Ollama @ {OLLAMA_HOST}"
            except: pass
        elif provider == "claude":
            key = os.environ.get("ANTHROPIC_API_KEY","")
            if not key: return
            try:
                import anthropic
                anthropic.Anthropic(api_key=key)
                self.available = True
                self.description = "Claude API"
            except: self.available = True; self.description = "Claude API (HTTP)"
        elif provider == "openai":
            if os.environ.get("OPENAI_API_KEY"):
                self.available = True; self.description = "OpenAI API"
        elif provider == "groq":
            if os.environ.get("GROQ_API_KEY"):
                self.available = True; self.description = "Groq API"
        elif provider == "deepseek":
            if os.environ.get("DEEPSEEK_API_KEY"):
                self.available = True; self.description = "DeepSeek API"

    def chat(self, model=None, system=None, user="", max_tokens=2000, temperature=0.1, timeout=120):
        if not self.available:
            return "No AI provider available. Run 'bughunter-pro setup' to configure one."
        if self.provider == "ollama":
            return self._chat_ollama(model, system, user, max_tokens, temperature, timeout)
        elif self.provider == "claude":
            return self._chat_claude(model, system, user, max_tokens, temperature, timeout)
        else:
            return self._chat_openai(model, system, user, max_tokens, temperature, timeout)

    def _chat_ollama(self, model, system, user, max_tokens, temperature, timeout):
        model = model or self.model or os.environ.get("OLLAMA_MODEL", "qwen3:4b")
        messages = []
        if system: messages.append({"role":"system","content":system})
        messages.append({"role":"user","content":user})
        payload = json.dumps({"model":model,"messages":messages,"stream":False,
            "options":{"num_predict":max_tokens,"temperature":temperature}}).encode()
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/chat", data=payload,
            headers={"Content-Type":"application/json"})
        try:
            resp = json.loads(urllib.request.urlopen(req, timeout=timeout or 120).read())
            return resp.get("message",{}).get("content","")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                avail = self._list_ollama_models()
                return f"Model '{model}' not found. Available: {avail or 'none — run: ollama pull qwen3:4b'}"
            raise

    def _list_ollama_models(self):
        try:
            req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
            data = json.loads(urllib.request.urlopen(req, timeout=5).read())
            return ", ".join(m.get("name","?") for m in data.get("models",[]))
        except: return ""

    def _chat_claude(self, model, system, user, max_tokens, temperature, timeout):
        model = model or "claude-sonnet-4-6"
        key = os.environ.get("ANTHROPIC_API_KEY","")
        payload = json.dumps({"model":model,"max_tokens":max_tokens,"temperature":temperature,
            "system":system,"messages":[{"role":"user","content":user}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
            headers={"Content-Type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01"})
        data = json.loads(urllib.request.urlopen(req,timeout=timeout).read().decode())
        return "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")

    def _chat_openai(self, model, system, user, max_tokens, temperature, timeout):
        model = model or "gpt-4o-mini"
        key = os.environ.get("OPENAI_API_KEY","")
        payload = json.dumps({"model":model,"messages":[{"role":"system","content":system or ""},
            {"role":"user","content":user}],"max_tokens":max_tokens,"temperature":temperature}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=payload,
            headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"})
        data = json.loads(urllib.request.urlopen(req,timeout=timeout).read().decode())
        return data.get("choices",[{}])[0].get("message",{}).get("content","")


# ── Core Brain ──────────────────────────────────────────────────

class Brain:
    """AI analysis layer for bug bounty findings."""

    SYSTEM = "You are a professional bug bounty hunter and security researcher. Analyze the provided data and give actionable insights."

    def __init__(self, provider=None):
        self.client = LLMClient(provider)
        self.provider = self.client.provider

    def analyze_recon(self, recon_dir):
        """Analyze recon data and suggest attack vectors."""
        data = self._gather_recon_data(recon_dir)
        prompt = f"""Analyze this recon data for {recon_dir} and identify:
1. Most promising attack vectors
2. Low-hanging fruit vulnerabilities
3. Priorities for manual testing

Data:
{json.dumps(data, indent=2)[:8000]}"""
        return self.client.chat(system=self.SYSTEM, user=prompt, timeout=600)

    def analyze_js(self, js_content, filename=""):
        """Analyze a JavaScript file for hardcoded secrets (batch-style)."""
        system = """You are a JavaScript security analyst. Find hardcoded secrets,
API keys, tokens, passwords, connection strings, internal URLs, and credentials.
Return ONLY a JSON array. Each item: {"type":"...","value":"...","confidence":"high|medium","file":"..."}
If nothing found, return []."""
        user = f"FILE: {filename}\n```javascript\n{js_content[:16000]}\n```"
        raw = self.client.chat(model=None, system=system, user=user, temperature=0.1, max_tokens=2048)
        return self._parse_json_array(raw)

    def analyze_js_batch(self, files_dir, max_files=50):
        """Batch JS analysis: scan multiple JS files for secrets (from BugHunter Pro v4.0)."""
        path = Path(files_dir)
        if not path.exists(): return []
        js_files = sorted(path.rglob("*.js"))[:max_files]
        if not js_files: return []
        all_findings = []
        system = """You are a JS security analyst. Find hardcoded secrets, API keys,
tokens, passwords, connection strings, internal URLs. Return ONLY JSON array.
Each: {"type":"...","value":"...","confidence":"high|medium","file":"..."}
Ignore libraries, placeholders, test data. Return [] if nothing found."""
        for i, jsf in enumerate(js_files, 1):
            try:
                content = jsf.read_text(errors="ignore")
                if not content.strip() or len(content) > 50000: continue
                label = jsf.name
                print(f"  [{i}/{len(js_files)}] {label}")
                chunk = content[:16000]
                user = f"FILE: {label}\n```javascript\n{chunk}\n```"
                raw = self.client.chat(system=system, user=user, temperature=0.1, max_tokens=2048, timeout=300)
                findings = self._parse_json_array(raw)
                for f in findings:
                    f["file"] = label
                    all_findings.append(f)
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(0.3)
        return all_findings

    def _parse_json_array(self, text):
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?","",text).strip()
            text = re.sub(r"```$","",text).strip()
        try: return json.loads(text) if isinstance(json.loads(text),list) else []
        except:
            m = re.search(r"\[[\s\S]*\]", text)
            if m:
                try: return json.loads(m.group(0)) if isinstance(json.loads(m.group(0)),list) else []
                except: return []
            return []

    def analyze_finding(self, finding_text):
        """Contextual analysis of a potential finding."""
        prompt = f"""Analyze this potential bug bounty finding:
{finding_text}

Provide:
1. Vulnerability type and CWE
2. Impact assessment (critical/high/medium/low/info)
3. Steps to verify
4. Remediation advice"""
        return self.client.chat(system=self.SYSTEM, user=prompt)

    def triage_finding(self, finding_text):
        """Fast triage: pass/kill/downgrade with reason."""
        prompt = f"""Triage this finding for a bug bounty report:
{finding_text}

Respond with: PASS (high chance of payout) | KILL (not exploitable) | DOWNGRADE
Include 1-2 sentence reason."""
        return self.client.chat(system=self.SYSTEM, user=prompt, max_tokens=200)

    def build_chain(self, findings_dir):
        """Build exploit chain from multiple findings."""
        findings_path = Path(findings_dir) if findings_dir else None
        data = ""
        if findings_path and findings_path.exists():
            for f in findings_path.rglob("*.json"):
                try: data += f.read_text()[:2000] + "\n"
                except: pass
        prompt = f"""Given these findings, build an exploit chain (A->B->C):
{data[:6000] if data else 'No structured findings available.'}

Show the step-by-step exploitation path from least to most impactful."""
        return self.client.chat(system=self.SYSTEM, user=prompt)

    def chat(self, message):
        """Free-form Q&A."""
        return self.client.chat(system=self.SYSTEM, user=message)

    def _gather_recon_data(self, recon_dir):
        data = {}
        base = Path(recon_dir)
        if not base.exists(): return data
        for pattern, key in [("subdomains/*.txt","subdomains"),
            ("web/live_urls.txt","live_urls"),("endpoints/all_urls.txt","urls"),
            ("secrets/*.json","secrets"),("vulns/*.txt","vulns")]:
            files = list(base.glob(pattern))
            if files:
                lines = set()
                for f in files[:3]:
                    try: lines.update(f.read_text().splitlines()[:50])
                    except: pass
                data[key] = list(lines)[:50]
        return data


# ── CLI ─────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="BugHunter Brain — AI Analysis Layer")
    ap.add_argument("--phase", choices=["recon","scan","js","batch-js","triage","chain","report","chat","full","plan","exploit","list-models","autopilot"])
    ap.add_argument("--recon-dir", help="Path to recon output directory")
    ap.add_argument("--findings-dir", help="Path to findings directory")
    ap.add_argument("--js-file", help="Path to JavaScript file for analysis")
    ap.add_argument("--js-dir", help="Path to JS directory for batch analysis")
    ap.add_argument("--finding", help="Finding description for triage/analysis")
    ap.add_argument("--url", help="Target URL context")
    ap.add_argument("--provider", help="Force specific AI provider")
    ap.add_argument("--model", help="Model override")
    ap.add_argument("--list-models", action="store_true", help="List available Ollama models")
    args = ap.parse_args()

    brain = Brain(args.provider)
    info(f"Using provider: {brain.client.description}")

    if args.list_models or args.phase == "list-models":
        try:
            req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
            data = json.loads(urllib.request.urlopen(req, timeout=5).read())
            for m in data.get("models",[]):
                print(f"  {m.get('name','?')}")
        except: info("Ollama not available")
        return 0

    if args.phase == "recon" and args.recon_dir:
        result = brain.analyze_recon(args.recon_dir)
        print(result)

    elif args.phase == "js" and args.js_file:
        content = Path(args.js_file).read_text(errors="ignore")
        result = brain.analyze_js(content, Path(args.js_file).name)
        print(json.dumps(result, indent=2))

    elif args.phase == "batch-js" and args.js_dir:
        result = brain.analyze_js_batch(args.js_dir)
        print(json.dumps(result, indent=2))
        info(f"Total findings: {len(result)}")

    elif args.phase == "triage" and args.finding:
        result = brain.triage_finding(args.finding)
        print(result)

    elif args.phase == "chain":
        result = brain.build_chain(args.findings_dir)
        print(result)

    elif args.phase == "chat":
        print("BugHunter Brain chat. Type 'exit' to quit.")
        while True:
            try:
                q = input("> ").strip()
                if q.lower() in ("exit","quit"): break
                if not q: continue
                print(brain.chat(q))
            except (EOFError, KeyboardInterrupt): break

    else:
        ap.print_help()
    return 0

def info(msg): print(f"\033[0;36m[*]\033[0m {msg}")

if __name__ == "__main__":
    raise SystemExit(main())
