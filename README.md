# 🎯 BugHunter Pro v2.0

Real command-line recon + bug-finding tool.  
Based on HackerOne/Bugcrowd top report methodology.

---

## Quick Start

```bash
# 1. Install all tools (one time)
chmod +x install.sh && bash install.sh

# 2. Run full recon
python3 bughunter.py example.com

# 3. Run with authenticated session
python3 bughunter.py example.com --cookie "session=YOUR_COOKIE"

# 4. Run single phase only
python3 bughunter.py example.com --phase js
python3 bughunter.py example.com --phase dorks
python3 bughunter.py example.com --phase vulns

# 5. Check which tools are installed
python3 bughunter.py --check-tools

# 6. Show install instructions
python3 bughunter.py --install
```

---

## What It Does (11 Phases)

| Phase | What |
|-------|------|
| 1. Passive Subs | subfinder, assetfinder, amass, crt.sh, gau, waybackurls |
| 2. DNS | puredns resolve + bruteforce, altdns permutations |
| 3. HTTP | httpx tech-detect, screenshots, WAF detection |
| 4. Ports | naabu + nmap on critical ports (9200, 6379, 27017...) |
| 5. Content | katana crawl (auth+unauth), feroxbuster, kiterunner |
| 6. Params | arjun, SSRF/redirect/SQLi param extraction |
| 7. JS Deep | Download all JS, source maps, LinkFinder, JSluice, 25 secret patterns |
| 8. Dorks | 80+ Google dorks + GitHub dorks generated for target |
| 9. Vulns | nuclei (CVEs, panels, default creds, misconfig, CORS), subzy, 403 bypass |
| 10. Cloud | S3 buckets, Firebase, GCP storage |
| 11. GitHub | TruffleHog org scan, gitleaks |

---

## Output Structure

```
hunt_example.com_20260308_120000/
├── subdomains/
│   └── all_passive.txt        ← All discovered subdomains
├── dns/
│   └── resolved.txt           ← Live subdomains
├── web/
│   ├── live_urls.txt          ← Live HTTP/S hosts
│   └── 403_hosts.txt          ← 403 bypass candidates
├── ips/
│   └── open_ports.txt         ← Open ports
├── endpoints/
│   ├── all_urls.txt           ← All URLs
│   └── js_extracted_endpoints.txt
├── params/
│   ├── ssrf_prone.txt         ← SSRF param URLs
│   ├── redirect_prone.txt     ← Open redirect URLs
│   └── injection_prone.txt    ← SQLi/XSS URLs
├── js/
│   ├── files/                 ← Downloaded JS
│   ├── maps/                  ← Source maps
│   └── source_maps_found.txt
├── secrets/                   ← AWS keys, JWTs, etc.
├── vulns/                     ← nuclei, subzy results
├── dorks/
│   ├── google_dorks.txt
│   └── github_dorks.txt
└── HUNT_REPORT_example.com.md ← Final report
```

---

## Requirements

- Python 3.8+
- Linux (Kali, Parrot, Ubuntu 22.04)
- Go 1.20+ (for tool installation)
- Internet connection

---

## Phase Examples

```bash
# JS only (fastest for secret hunting)
python3 bughunter.py example.com --phase js

# Just generate dorks
python3 bughunter.py example.com --phase dorks

# Vuln scan only (if you already have live_urls.txt)
python3 bughunter.py example.com --phase vulns

# Full run with auth cookie
python3 bughunter.py example.com --cookie "auth=eyJhb..."
```

---

## AI-Powered JS Secret Scanning

Uses an LLM to find hardcoded credentials, API keys, tokens, passwords, and other secrets in JavaScript files. Supports **OpenAI/GPT**, **Anthropic Claude**, **DeepSeek**, **Ollama** (local), or any OpenAI-compatible API. Catches what regex misses: obfuscated credentials, split variables, base64-encoded values, and unusual formats.

### Flags

| Flag | Description |
|------|-------------|
| `--ai-secrets` | Run AI scan **after** the regex-based scan (both run) |
| `--ai-secrets-only` | Skip regex completely; **only** use AI for secret detection |
| `--ai-provider` | `openai` (default), `claude`, or `ollama` |
| `--ai-model` | Override model (e.g. `gpt-4o`, `claude-sonnet-4`, `deepseek-chat`, `llama3`) |
| `--ai-api-key` | API key (defaults to `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or provider-specific env) |
| `--ai-api-base` | Custom API base URL |

### How It Works

1. Every downloaded JS file plus every extracted source-map source is sent to the LLM
2. The AI identifies credentials, API keys, tokens, passwords, private keys, connection strings, and any other secret-like values
3. Results are saved to:
   - `secrets/js_ai_findings.json` (full JSON with file, type, value, line, confidence)
   - `secrets/js_ai_findings.txt` (human-readable summary)

### Examples

```bash
# ── OpenAI / GPT ──
export OPENAI_API_KEY="sk-..."
python3 bughunter.py example.com --phase js --ai-secrets

# AI only — skip regex
python3 bughunter.py example.com --phase js --ai-secrets-only

# ── Anthropic Claude ──
export ANTHROPIC_API_KEY="sk-ant-..."
python3 bughunter.py example.com --phase js --ai-secrets --ai-provider claude

# Use a specific Claude model
python3 bughunter.py example.com --phase js --ai-secrets --ai-provider claude --ai-model claude-sonnet-4-20250514

# ── DeepSeek (OpenAI-compatible via --ai-api-base) ──
export OPENAI_API_KEY="sk-..."
python3 bughunter.py example.com --phase js --ai-secrets --ai-api-base https://api.deepseek.com/v1

# ── Ollama (local, no API key needed) ──
python3 bughunter.py example.com --phase js --ai-secrets-only --ai-provider ollama

# Custom model via Ollama
python3 bughunter.py example.com --phase js --ai-secrets-only --ai-provider ollama --ai-model llama3

# ── Full recon with AI ──
python3 bughunter.py example.com --ai-secrets-only --ai-provider ollama
```

### Providers

| Provider | `--ai-provider` | API Key | Default Model | Notes |
|----------|-----------------|---------|---------------|-------|
| OpenAI / GPT | `openai` | `OPENAI_API_KEY` env or `--ai-api-key` | `gpt-4o-mini` | Works with any OpenAI-compatible API (DeepSeek, local proxies, etc.) |
| Anthropic Claude | `claude` | `ANTHROPIC_API_KEY` env or `--ai-api-key` | `claude-sonnet-4-20250514` | Uses Anthropic Messages API |
| DeepSeek | `openai` | `OPENAI_API_KEY` or `--ai-api-key` | — | Set `--ai-api-base https://api.deepseek.com/v1` |
| Ollama | `ollama` | None (local) | `llama3` | Set `OLLAMA_HOST` env to change from `http://localhost:11434` |
