# BugHunter Pro — Combined Edition

**AI-Powered Bug Bounty Hunting Toolkit — Recon to Report, All in Your Terminal**

BugHunter Pro automates the entire bug bounty workflow: subdomain enumeration, DNS resolution, HTTP probing, port scanning, content discovery, parameter analysis, JavaScript deep recon (with 70+ secret patterns + AI), GraphQL detection, API fuzzing, Google dork generation, vulnerability scanning, cloud asset discovery, GitHub secret scanning, finding validation, and report generation.

**No subscription required.** Works 100% free with Ollama (local AI), or with Groq/DeepSeek/Claude/OpenAI.

Combines the **13-phase recon pipeline** from BugHunter Pro v4.0 with the **modular agent architecture, multi-AI provider support, validation gate, and Web3 modules** from Claude Bug Bounty.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start (5-Minute Demo)](#quick-start-5-minute-demo)
- [All Commands](#all-commands)
- [The 13-Phase Recon Pipeline (Detailed)](#the-13-phase-recon-pipeline-detailed)
- [AI Features (How AI is Used)](#ai-features-how-ai-is-used)
- [Validation Gate](#validation-gate)
- [Autonomous Agent](#autonomous-agent)
- [Multi-AI Provider System](#multi-ai-provider-system)
- [Supported Tools](#supported-tools)
- [Output Structure](#output-structure)
- [Example Workflow](#example-workflow)
- [Project Architecture](#project-architecture)
- [Credits](#credits)

---

## Installation

### Prerequisites

- **Python 3.9+** installed
- **Linux** (Kali/Parrot/Ubuntu recommended — some tools may not work on Windows)
- **Go 1.20+** (for installing Go-based recon tools)
- **Internet connection**

### Step 1: Get the Project

```bash
git clone <your-repo-url>
cd bughunter-pro
```

### Step 2: Install as System Command (Optional)

```bash
chmod +x install.sh
./install.sh --standalone
```

This creates the `bughunter-pro` command so you can run it from anywhere.

### Step 3: Install External Recon Tools (For Full 13-Phase Pipeline)

```bash
chmod +x install_tools.sh
./install_tools.sh
```

This installs: `subfinder`, `httpx`, `nuclei`, `katana`, `gau`, `waybackurls`, `ffuf`, `amass`, `puredns`, `dnsx`, `naabu`, `jsluice`, `trufflehog`, and more.

> **Note:** The tool runs even without these — it simply skips phases that require missing tools and reports what's missing.

### Step 4: Configure AI Provider

```bash
bughunter-pro setup
```

You'll be prompted to choose an AI provider:

| # | Provider | Cost | Needs |
|---|----------|------|-------|
| 1 | **Ollama** | Free (local, offline) | `ollama pull qwen2.5:14b` |
| 2 | **Groq** | Free tier (cloud) | `GROQ_API_KEY` |
| 3 | **DeepSeek** | Very cheap (cloud) | `DEEPSEEK_API_KEY` |
| 4 | **Claude** | Paid (cloud) | `ANTHROPIC_API_KEY` |
| 5 | **OpenAI** | Paid (cloud) | `OPENAI_API_KEY` |
| 6 | **Grok/xAI** | Paid (cloud) | `XAI_API_KEY` |

**For zero-cost setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:14b

# Then run setup
bughunter-pro setup   # Choose option 1 (Ollama)
```

---

## Quick Start (5-Minute Demo)

```bash
# 1. Configure AI
bughunter-pro setup

# 2. Quick recon on a target
bughunter-pro recon example.com

# 3. Validate a finding
bughunter-pro validate "Open S3 bucket at s3.amazonaws.com/bucket-name"

# 4. Generate report
bughunter-pro report
```

---

## All Commands

### Core Workflow Commands

| Command | Description |
|---------|-------------|
| `bughunter-pro recon <target>` | Run phases 1-7 (subs, DNS, HTTP, ports, content, params, JS) |
| `bughunter-pro deep <target>` | Run ALL 13 phases (full deep recon) |
| `bughunter-pro hunt <target>` | Full autonomous hunt with AI |
| `bughunter-pro js <target>` | JS deep recon only (phase 7) |
| `bughunter-pro validate "<finding>"` | Run the 7-Question Validation Gate on a finding |
| `bughunter-pro triage "<finding>"` | Auto-triage a finding (PASS/KILL/DOWNGRADE) |
| `bughunter-pro report` | Generate a submission-ready HackerOne/Bugcrowd report |
| `bughunter-pro chain` | Build A→B→C exploit chains from findings |

### Single-Phase Commands

| Command | Description |
|---------|-------------|
| `bughunter-pro phase 1 <target>` | Passive subdomain enumeration |
| `bughunter-pro phase 2 <target>` | DNS resolution + permutations |
| `bughunter-pro phase 3 <target>` | HTTP probing + screenshots |
| `bughunter-pro phase 4 <target>` | Port scanning |
| `bughunter-pro phase 5 <target>` | Content discovery + sensitive files |
| `bughunter-pro phase 6 <target>` | Parameter discovery (SSRF, XSS, IDOR) |
| `bughunter-pro phase 7 <target>` | JS deep recon (secrets, source maps, endpoints) |
| `bughunter-pro phase 8 <target>` | GraphQL detection + introspection |
| `bughunter-pro phase 9 <target>` | API fuzzing |
| `bughunter-pro phase 10 <target>` | Google dork generation |
| `bughunter-pro phase 11 <target>` | Vulnerability scanning |
| `bughunter-pro phase 12 <target>` | Cloud asset discovery |
| `bughunter-pro phase 13 <target>` | GitHub secret scanning |

You can also use phase names: `bughunter-pro phase vulns <target>` or `bughunter-pro phase js <target>`.

### Configuration Commands

| Command | Description |
|---------|-------------|
| `bughunter-pro setup` | Interactive AI provider setup wizard |
| `bughunter-pro providers` | List all available AI providers and their status |
| `bughunter-pro models` | List available local Ollama models |
| `bughunter-pro status` | Show pipeline status and output directory info |
| `bughunter-pro chat` | Interactive AI chat — ask questions about your target |

### Aliases

| Shortcut | Full Command |
|----------|-------------|
| `bughunter-pro r <target>` | `bughunter-pro recon <target>` |
| `bughunter-pro f <target>` | `bughunter-pro deep <target>` |
| `bughunter-pro h <target>` | `bughunter-pro hunt <target>` |
| `bughunter-pro j <target>` | `bughunter-pro js <target>` |
| `bughunter-pro v "<finding>"` | `bughunter-pro validate "<finding>"` |
| `bughunter-pro rep` | `bughunter-pro report` |
| `bughunter-pro s` | `bughunter-pro status` |

---

## The 13-Phase Recon Pipeline (Detailed)

### Phase 1: Passive Subdomain Enumeration

**Goal:** Discover all subdomains of your target without sending a single packet to the target.

**Tools used:** `subfinder`, `assetfinder`, `amass`, `crt.sh`, `gau`, `waybackurls`, `github-subdomains`

**What it produces:**
- `subdomains/all_passive.txt` — All unique subdomains discovered
- Individual tool outputs in `subdomains/`

**Example output:**
```
admin.example.com
dev-api.example.com
mail.example.com
staging.example.com
vpn.example.com
```

### Phase 2: DNS Resolution + Permutations

**Goal:** Find which subdomains are live, discover missing ones via permutations, and detect CNAME takeover opportunities.

**Tools used:** `puredns`, `altdns`, `gotator`, `dnsx`

**What it produces:**
- `dns/resolved.txt` — DNS-confirmed live subdomains with IPs
- `dns/dns_details.txt` — A, AAAA, CNAME, MX records
- `vulns/cname_takeovers.txt` — Dangling CNAME takeover candidates

**Dangerous services flagged automatically:**
- Port 9200/9300 → Elasticsearch (likely no-auth)
- Port 6379 → Redis (likely no-auth)
- Port 27017 → MongoDB (likely no-auth)
- Port 5601 → Kibana dashboard

### Phase 3: HTTP Probing + Tech Fingerprinting

**Goal:** Find which hosts are actually serving web content, identify their technology stack, and take screenshots.

**Tools used:** `httpx`, `wafw00f`, `gowitness`, `aquatone`

**What it produces:**
- `web/live_urls.txt` — Live HTTP/HTTPS URLs
- `web/httpx_full.txt` — Full tech detection (status codes, titles, web servers, IPs, CDN)
- `web/403_hosts.txt` — 403 Forbidden hosts (bypass candidates)
- `screenshots/` — Visual screenshots of each live host

**Example output:**
```
https://admin.example.com [403] [nginx] [Apache/2.4.41]
https://example.com [200] [WordPress 6.4] [PHP 8.1] [Cloudflare]
https://dev.example.com [401] [Node.js/Express]
```

### Phase 4: Port Scanning

**Goal:** Discover open ports beyond 80/443, especially dangerous services exposed to the internet.

**Tools used:** `naabu`, `nmap`

**What it produces:**
- `ips/all_ips.txt` — All resolved IPs
- `ips/open_ports.txt` — Open ports on critical services
- `ips/nmap_services/` — Detailed nmap service detection

**Dangerous services flagged automatically:**
- Elasticsearch (9200) — often no authentication
- Redis (6379) — often no authentication
- MongoDB (27017) — often no authentication
- Kibana (5601) — exposed dashboards
- WebLogic (7001) — CVE-2020-14882

### Phase 5: Content Discovery + Sensitive File Probing

**Goal:** Crawl all discovered hosts to find every URL, API endpoint, and exposed sensitive file.

**Tools used:** `katana`, `gau`, `waybackurls`, `hakrawler`, `feroxbuster`, `kiterunner`

**Sensitive files probed (80+ paths):**
```
/.git/HEAD            /.env               /wp-config.php.bak
/actuator/env         /graphql            /swagger.json
/backup.zip           /phpinfo.php        /admin
/Dockerfile           /sitemap.xml        /crossdomain.xml
```

**What it produces:**
- `endpoints/all_urls.txt` — All discovered URLs
- `vulns/sensitive_files.txt` — Exposed sensitive files with confirmation

### Phase 6: Parameter Discovery

**Goal:** Find URLs with parameters that indicate specific vulnerability classes.

**What it discovers:**
- **SSRF-prone parameters:** `url=`, `redirect=`, `proxy=`, `fetch=`, `load=`
- **Open redirect parameters:** `return=`, `next=`, `goto=`, `dest=`
- **XSS-prone parameters:** `q=`, `search=`, `query=`, `callback=`, `jsonp=`
- **IDOR-prone parameters:** `id=`, `uid=`, `account=`, `order_id=`
- **Injection-prone parameters:** `cmd=`, `exec=`, `select=`, `order=`

**Tools used:** `unfurl`, `arjun` (for hidden parameter discovery)

### Phase 7: JavaScript Deep Recon (The Crown Jewel)

**Goal:** Extract every possible piece of information from JavaScript files.

**This is the most powerful phase. Here's what it does in sequence:**

1. **JS URL Discovery** — Finds all JS file URLs from crawls, historical data, HTML pages, and framework manifests (Next.js, webpack, Vite)
2. **JS Downloading** — Downloads all discovered JS files (multi-threaded, up to 3000 files)
3. **Recursive JS Crawling** — Finds JS imports inside downloaded JS files (depth 3)
4. **Source Map Detection** — Checks every JS file and URL for `.map` files (exposes unminified source code)
5. **Source Map Extraction** — Downloads source maps, extracts original source files, analyzes them
6. **JSluice Analysis** — AST-level URL and secret extraction
7. **Advanced Static Analysis:**
   - Endpoint extraction from strings, API calls
   - API call cataloging (fetch, axios, etc.)
   - GraphQL operation detection
   - Client-side route discovery
   - Storage key discovery (localStorage, sessionStorage, cookies)
   - Dangerous sink detection (eval, innerHTML, postMessage)
   - Interesting config values (auth, API, tenant endpoints)
8. **Regex Secret Scanning (70+ patterns):** See the full list below
9. **Entropy-Based Secret Detection** — Catches high-entropy strings near credential-like keywords
10. **Credential Pair Detection** — Finds username + password pairs in the same context

**Full list of 70+ secret patterns checked:**

| Category | Patterns |
|----------|----------|
| **AWS** | Access Key (AKIA/ASIA), Secret Key, Session Token, Account ID, ARN |
| **GCP/Firebase** | Google API Key (AIza), OAuth ID/Secret, Firebase URL, Service Account |
| **Stripe** | Secret Key (sk_live), Restricted Key, Publishable Key |
| **GitHub** | Classic Token, Fine-Grained PAT, GitLab Token |
| **Slack** | Bot/User/App Token, Webhook URL |
| **Discord** | Webhook URL, Bot Token |
| **Twilio** | SID, Auth Token |
| **SendGrid/Mailgun/Mailchimp** | API Keys |
| **Auth** | JWT Tokens, Bearer Tokens, Private Keys, Basic Auth URLs, OAuth Client Secrets |
| **Azure** | Connection Strings, Account Keys |
| **DigitalOcean** | Personal Access Token, Spaces Keys |
| **Databases** | MongoDB, PostgreSQL, MySQL, Redis Connection URIs |
| **AI/ML** | OpenAI Keys (sk-), Anthropic Keys (sk-ant-), HuggingFace Tokens |
| **SaaS** | Shopify, Supabase, Algolia, Mapbox, NPM, Cloudinary, Sentry, Datadog, Vercel, Clerk |
| **Generic** | API Keys, Passwords, Usernames, Encryption Keys, Internal URLs, Feature Flags, Hardcoded Credentials, Debug Statements |

### Phase 8: GraphQL Detection & Introspection

**Goal:** Find GraphQL endpoints and check if introspection is enabled.

**Probes 15+ common GraphQL paths** on every live host and sends an introspection query. If introspection is enabled, the full schema is dumped and analyzed for sensitive types (User, Admin, Token, Payment, Credential).

### Phase 9: API Fuzzing

**Goal:** Discover hidden API endpoints and test HTTP method abuse.

**What it does:**
- Probes 20+ common API base paths (`/api`, `/api/v1`, `/rest`, `/swagger.json`)
- Runs `ffuf` API endpoint fuzzing with wordlists
- Tests HTTP method abuse (PUT, DELETE, PATCH, OPTIONS) on discovered APIs

### Phase 10: Google Dork Generation

**Goal:** Generate 100+ Google dorks and GitHub dorks for manual searching.

**Categories:**
- Sensitive files (env, log, sql, zip, pem, key)
- Admin panels (jenkins, grafana, kibana, jira)
- API & docs (swagger, graphql, postman)
- Open redirect & SSRF params
- Cloud infrastructure (S3, Firebase, GCP)
- Source code leaks (GitHub, GitLab, Pastebin)
- Error & debug info
- SQL injection prone params

### Phase 11: Vulnerability Scanning

**Goal:** Automatically find vulnerabilities using multiple techniques.

**What it runs:**
- **nuclei** — CVEs (high/critical), exposed panels, default credentials, misconfigurations, exposed files, CORS, tech detection
- **subzy** — Subdomain takeover detection
- **403 Bypass Testing** — Path manipulation headers (X-Original-URL, X-Forwarded-For)
- **CORS Testing** — Checks for permissive CORS policies with null origin and arbitrary origins
- **CRLF Injection** — Tests 5 different CRLF payloads on all live hosts
- **Open Redirect Validation** — Tests parameter-bearing URLs with external redirect canary
- **Host Header Injection** — Tests Host header manipulation
- **dalfox** — Reflected XSS scanning on parameter URLs
- **sqlmap** — SQL injection testing on top injection-prone URLs

### Phase 12: Cloud Asset Discovery

**Goal:** Find exposed cloud storage assets.

**What it checks:**
- **AWS S3 Buckets** — 20+ bucket name permutations, direct HTTP + aws cli
- **Firebase Realtime Databases** — Database name permutations
- **GCP Storage Buckets** — 10+ bucket permutations
- **Azure Blob Storage** — Account + container permutations across multiple account names
- **DigitalOcean Spaces** — 5 regions × 8 bucket names

### Phase 13: GitHub Secret Scanning

**Goal:** Find secrets in the target's GitHub organization.

**Tools used:** `trufflehog`, `gitleaks`

**What it produces:**
- `secrets/trufflehog_github.txt` — Verified secrets from TruffleHog
- GitHub dorks for manual searching

---

## AI Features (How AI is Used)

BugHunter Pro uses AI in 4 distinct ways:

### 1. AI-Powered JS Secret Scanning

**What it does:** After the regex-based secret scan (70+ patterns), the AI scans every JS file again — but using an LLM instead of patterns.

**Why this matters:** Regex only catches known patterns. The AI catches:

- **Obfuscated credentials** — `var a = "pass"; var b = "word";` → AI sees them as one credential
- **Base64-encoded values** — `"cGFzc3dvcmQxMjM="` → AI decodes and recognizes it
- **Split variables** — Credentials assembled from multiple string concatenations
- **Unusual formats** — Custom auth schemes that don't match known patterns
- **Context-aware detection** — AI understands what a value is used for, not just what it looks like

**How to use it:**

```bash
# Run JS phase with AI scanning (uses your configured provider)
bughunter-pro phase 7 target.com

# Or run the AI batch scanner directly:
python3 brain.py --phase batch-js --js-dir ./recon/hunt_target_20260401/js/files
```

**What happens:**
1. Every downloaded JS file + source-map source is sent to the LLM
2. The AI identifies any credential-like strings
3. Results saved to `secrets/js_ai_findings.json`

### 2. The Brain — AI Analysis Layer (`brain.py`)

The Brain wraps 11 AI providers behind a single interface and powers:

| Feature | What It Does |
|---------|-------------|
| **Recon Analysis** | Given your recon data, suggests the most promising attack vectors |
| **JS Analysis** | Single-file or batch JS scanning for secrets |
| **Finding Triage** | Fast PASS/KILL/DOWNGRADE decision on any finding |
| **Exploit Chains** | Connects multiple findings into A→B→C attack chains |
| **Interactive Chat** | Free-form Q&A about your target or findings |

**Usage examples:**

```bash
# Analyze recon output
python3 brain.py --phase recon --recon-dir ./recon/hunt_target_20260401

# Triage a finding
python3 brain.py --phase triage --finding "SSRF at /api/proxy with internal host reflection"

# Interactive chat
python3 brain.py --phase chat
> What should I test after finding open S3 buckets?
```

**Provider auto-detection order:**
```
1. Ollama (local)     → 100% free, offline
2. Groq (cloud)       → Free tier, fast
3. DeepSeek (cloud)   → Very cheap
4. Cerebras (cloud)   → Fastest inference
5. Gemini (cloud)     → Google's model
6. Claude (cloud)     → Paid
7. OpenAI (cloud)     → Paid
8. Grok/xAI (cloud)   → Paid
```

### 3. Validation Gate — AI-Assisted Triage

The validation gate can run in **auto-triage mode** where it uses keywords and heuristics to score a finding's quality:

```
Input: "RCE at /api/exec?cmd=ls with PoC curl command"
→ Heuristic score: RCE (+3), PoC mentioned (+2) = HIGH confidence

Input: "Maybe reflected XSS in search param, couldn't reproduce"
→ Heuristic score: "Maybe" (-2), no PoC = LOW confidence
```

### 4. Autonomous Agent — LLM-Driven Decision Making

The ReAct agent uses an LLM to decide which phase to run next based on what it's already found:

```
1. Agent observes: "Found admin.example.com with 403 status"
2. AI thinks: "403 suggests the endpoint exists but is restricted. Should try bypass techniques."
3. Agent acts: Runs 403 bypass testing
4. Agent observes: "X-Forwarded-For bypass worked, found admin panel"
5. AI thinks: "Have access to admin panel. Should check for default credentials and then try SQLi on login."
6. Agent acts: Runs phase 11 (vuln scan) targeting the admin panel
```

---

## Validation Gate

### 7-Question Gate

Before you report any finding, the validation gate asks 7 critical questions:

| # | Question | What It Tests |
|---|----------|---------------|
| 1 | Can you reproduce it consistently? | Reliability of the finding |
| 2 | Is there a realistic attack scenario? | Real-world exploitability |
| 3 | Does it leak sensitive data or allow code execution? | Severity assessment |
| 4 | Is it in-scope for the program? | Program policy compliance |
| 5 | Can you provide a working PoC? | Proof of concept quality |
| 6 | Is this a known vulnerability? | Duplicate check |
| 7 | Is there a clear remediation? | Actionability |

**Scoring:**
- **6-7/7: PASS** — High confidence, ready to report
- **4-5/7: BORDERLINE** — Needs more verification
- **0-3/7: KILL** — Low confidence, not worth reporting

### Auto-Triage

```bash
bughunter-pro triage "CRLF injection at example.com via %0d%0a header injection"
```

Returns: `HIGH | CRLF injection confirmed, has PoC, remediable with input encoding`

---

## Autonomous Agent

The agent (`agent.py`) implements a ReAct (Reasoning + Acting) loop that runs autonomously:

```
Usage:
  python3 agent.py --target example.com           # Phases 1-7
  python3 agent.py --target example.com --deep    # All 13 phases
  python3 agent.py --target example.com --phase 7 # Single phase
```

**How it works:**
1. The agent has all 13 phases registered as callable "tools"
2. It runs them in sequence (or intelligently, if AI-powered)
3. Each phase result is logged to a session file
4. Sessions can be resumed after crashes

**Available agent tools:**
- `run_passive_subs` — Phase 1
- `run_dns_resolve` — Phase 2
- `run_http_probe` — Phase 3
- `run_port_scan` — Phase 4
- `run_content_discovery` — Phase 5
- `run_param_discovery` — Phase 6
- `run_js_recon` — Phase 7
- `run_graphql_scan` — Phase 8
- `run_api_fuzz` — Phase 9
- `run_google_dorks` — Phase 10
- `run_vuln_scan` — Phase 11
- `run_cloud_scan` — Phase 12
- `run_github_scan` — Phase 13
- `run_recon` — All phases 1-7
- `run_deep_recon` — All phases 1-13
- `run_ai_js_analysis` — AI-powered JS secret scanning

---

## Multi-AI Provider System

The AI system auto-detects and prioritizes providers:

**Priority order:** Ollama → Groq → DeepSeek → Cerebras → Gemini → Claude → OpenAI → Grok

**Set provider via environment variable:**
```bash
export BRAIN_PROVIDER=groq
bughunter-pro recon target.com
```

**Provider API keys:**

| Provider | Env Variable | Get Key |
|----------|-------------|---------|
| Ollama | `OLLAMA_HOST` (default: `http://localhost:11434`) | `curl -fsSL https://ollama.ai/install.sh \| sh` |
| Groq | `GROQ_API_KEY` | https://console.groq.com |
| DeepSeek | `DEEPSEEK_API_KEY` | https://platform.deepseek.com |
| Claude | `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com |
| Grok | `XAI_API_KEY` | https://console.x.ai |
| Gemini | `GEMINI_API_KEY` | https://aistudio.google.com |
| Mistral | `MISTRAL_API_KEY` | https://console.mistral.ai |
| Together | `TOGETHER_API_KEY` | https://together.ai |
| Cerebras | `CEREBRAS_API_KEY` | https://cloud.cerebras.ai |
| Perplexity | `PERPLEXITY_API_KEY` | https://perplexity.ai |

---

## Supported Tools

### Required Tools (Phase Will Skip If Missing)

`subfinder` `assetfinder` `httpx` `nuclei` `naabu` `dnsx` `katana` `gau` `waybackurls` `getJS` `puredns` `subzy` `ffuf` `arjun` `trufflehog` `jsluice` `unfurl` `amass` `altdns` `jq`

### Optional Tools (Phase Runs Without Them)

`masscan` `nmap` `feroxbuster` `wafw00f` `sqlmap` `dalfox` `aquatone` `gowitness` `hakrawler` `kr`

---

## Output Structure

Every recon run creates a timestamped directory:

```
recon/hunt_example.com_20260401_120000/
├── subdomains/
│   ├── all_passive.txt       ← All subdomains from every source
│   ├── subfinder.txt         ← subfinder results
│   ├── crt.txt               ← crt.sh results
│   └── ...
├── dns/
│   ├── resolved.txt          ← DNS-confirmed live subdomains
│   ├── dns_details.txt       ← A, CNAME, MX records
│   └── resolvers.txt         ← DNS resolvers used
├── web/
│   ├── live_urls.txt         ← Live HTTP/HTTPS URLs
│   ├── httpx_full.txt        ← Full tech detection output
│   ├── 403_hosts.txt         ← 403 Forbidden (bypass candidates)
│   └── waf_*.txt            ← WAF detection results
├── ips/
│   ├── all_ips.txt           ← All resolved IPs
│   ├── open_ports.txt        ← Open port scan results
│   └── nmap_services/        ← Nmap service detection
├── endpoints/
│   ├── all_urls.txt          ← All crawled URLs
│   ├── js_extracted_endpoints.txt  ← Endpoints from JS
│   ├── js_absolute_urls.txt  ← Absolute URLs from JS
│   ├── jsluice_endpoints.txt ← JSluice URL extraction
│   └── ...
├── params/
│   ├── ssrf_prone.txt        ← SSRF-vulnerable URLs
│   ├── redirect_prone.txt    ← Open redirect URLs
│   ├── injection_prone.txt   ← SQLi/XSS URLs
│   ├── xss_prone.txt         ← XSS-prone URLs
│   └── idor_prone.txt        ← IDOR-prone URLs
├── js/
│   ├── js_urls.txt           ← All discovered JS file URLs
│   ├── files/                ← Downloaded JS files
│   ├── maps/                 ← Downloaded source maps
│   │   └── sources/          ← Extracted source map source files
│   ├── source_maps_found.txt ← Detected source maps
│   ├── js_api_calls.json     ← API calls extracted from JS
│   ├── graphql_operations.json  ← GraphQL ops from JS
│   ├── storage_keys.txt      ← localStorage/sessionStorage keys
│   └── interesting_config.txt   ← Config values from JS
├── secrets/
│   ├── js_findings_per_file.txt ← Per-file findings report
│   ├── js_findings_per_file.json ← Machine-readable version
│   ├── js_*.json             ← Pattern-specific findings files
│   ├── js_ai_findings.json   ← AI-powered findings (if enabled)
│   ├── jsluice_secrets.json  ← JSluice secrets
│   └── ...
├── graphql/
│   ├── graphql_endpoints.txt ← Discovered GraphQL endpoints
│   ├── schema_types.txt      ← Extracted schema types
│   └── introspection_*.json  ← Full introspection dumps
├── api/
│   ├── found_api_paths.txt   ← Discovered API paths
│   ├── method_allowed.txt    ← HTTP method fuzzing hits
│   └── ffuf_*.json           ← ffuf fuzzing results
├── dorks/
│   └── google_dorks.txt      ← Generated dorks for manual searching
├── vulns/
│   ├── nuclei_cve.txt        ← Nuclei CVE findings
│   ├── nuclei_panels.txt     ← Exposed admin panels
│   ├── nuclei_default_creds.txt  ← Default credentials
│   ├── cname_takeovers.txt   ← Dangling CNAME targets
│   ├── sensitive_files.txt   ← Exposed sensitive paths
│   ├── cors_misconfig.txt    ← CORS misconfigurations
│   ├── open_redirects.txt    ← Verified open redirects
│   ├── host_header_injection.txt  ← Host header injections
│   ├── 403_bypasses.txt      ← Successful bypasses
│   ├── dalfox_xss.txt        ← XSS findings
│   └── ...
├── screenshots/              ← Visual screenshots (gowitness/aquatone)
├── secrets/                  ← Cloud asset findings
│   ├── open_s3_buckets.txt   ← Open AWS S3 buckets
│   ├── open_gcp_buckets.txt  ← Open GCP buckets
│   ├── firebase_*.json       ← Firebase database dumps
│   └── trufflehog_github.txt ← GitHub secrets
└── HUNT_REPORT.md            ← Final summary report
```

---

## Example Workflow

### Full Deep Recon on a Bug Bounty Target

```bash
# ── 1. SETUP ──
bughunter-pro setup                      # Choose Ollama (free)
bughunter-pro status                     # Verify everything is ready

# ── 2. FULL DEEP RECON (all 13 phases) ──
bughunter-pro deep target.com
# This runs all phases and takes 20-60 minutes depending on target size
# Output goes to: recon/hunt_target.com_20260401_120000/

# ── 3. REVIEW FINDINGS ──
cat recon/hunt_target.com_*/vulns/nuclei_cve.txt       # CVEs found
cat recon/hunt_target.com_*/secrets/js_findings_per_file.txt  # JS secrets
cat recon/hunt_target.com_*/secrets/open_s3_buckets.txt       # Cloud leaks
cat recon/hunt_target.com_*/graphql/graphql_endpoints.txt     # GraphQL endpoints
cat recon/hunt_target.com_*/vulns/cname_takeovers.txt         # Takeover candidates

# ── 4. VALIDATE A FINDING ──
bughunter-pro validate "Open S3 bucket at target-backup.s3.amazonaws.com with public read access"
# Answer the 7 questions → get PASS/KILL decision

# ── 5. GENERATE REPORT ──
bughunter-pro report
# Creates: reports/bug_report_20260401_120000.md

# ── 6. (OPTIONAL) AI ANALYSIS ──
python3 brain.py --phase recon --recon-dir ./recon/hunt_target.com_20260401_120000
# AI reads all your recon data and tells you where to attack first
```

### Quick JS Secret Hunt (Fastest Path to a Payout)

```bash
bughunter-pro js target.com
# Downloads all JS files, scans for secrets, source maps, endpoints
# Takes 5-15 minutes
# Check: recon/hunt_target.com_*/secrets/js_findings_per_file.txt
```

---

## Project Architecture

```
bughunter-pro/
│
├── engine.py                    # Main CLI — all commands (recon, deep, js, hunt, etc.)
├── brain.py                     # Multi-provider AI layer (11 providers)
│                                #   - LLMClient: unified chat interface
│                                #   - Brain: recon analysis, JS scanning, triage, chains, chat
│
├── agent.py                     # ReAct autonomous agent with 15+ tools
│                                #   - Runs all 13 phases as callable tools
│                                #   - Session persistence to disk
│                                #   - LangGraph backend support
│
├── tools/
│   ├── hunt.py                  # 13-phase orchestration pipeline (the core)
│   ├── validate.py              # 7-Question Validation Gate + auto-triage
│   ├── auth_session.py          # Authenticated session management
│   ├── banner.py                # ASCII art banner
│   │
│   ├── recon_engine.sh          # Shell-based subdomain + URL discovery
│   ├── vuln_scanner.sh          # XSS/SQLi/SSTI/SSRF/MFA pipeline
│   ├── param_discovery.sh       # Hidden parameter discovery
│   ├── cloud_recon.sh           # Cloud asset discovery
│   ├── takeover_scanner.sh      # Subdomain takeover scanner
│   ├── secrets_hunter.sh        # trufflehog/noseyparker/gitleaks wrapper
│   ├── bypass_403.sh            # 403 bypass techniques
│   ├── cve_scan.sh              # Focused CVE scanning
│   ├── cicd_scanner.sh          # CI/CD security scanning
│   └── ... (25+ additional tools)
│
├── tests/                       # 24 pytest test files
│   ├── test_hunt_target_types.py
│   ├── test_auth_session.py
│   ├── test_brain_auto_detect.py
│   ├── test_validation_handoff.py
│   └── ...
│
├── memory/                      # Cross-session learning
│   ├── pattern_db.py            # Cross-target pattern learning
│   ├── audit_log.py             # Request audit log, rate limiter, circuit breaker
│   ├── rotation.py              # JSONL rotation (10MB cap, 3 backups)
│   └── schemas.py               # Schema validation
│
├── agents/                      # Agent prompt templates
│   ├── autopilot.md             # Autonomous workflow prompt
│   ├── recon-agent.md           # Subdomain enumeration agent
│   ├── validator.md             # 4-gate validation agent
│   ├── report-writer.md         # Report writing agent
│   ├── web3-auditor.md          # Smart contract auditor
│   ├── chain-builder.md         # Exploit chain builder
│   └── ...
│
├── web3/                        # Smart contract auditing guides
│   ├── 00-START-HERE.md         # Web3 auditing intro
│   ├── 02-bug-classes.md        # Smart contract bug classes
│   ├── 10-meme-coin-bugs.md     # Meme coin specific vulnerabilities
│   └── ... (14 files)
│
├── wordlists/                   # Discovery wordlists
│   ├── common.txt               # Common web paths
│   ├── api-endpoints.txt        # API endpoint wordlist
│   ├── raft-medium-dirs.txt     # Directory brute-force wordlist
│   ├── params.txt               # Parameter name wordlist
│   └── sensitive-files.txt      # Sensitive file wordlist
│
├── docs/                        # Documentation
│   ├── TUTORIAL.md              # Step-by-step tutorial
│   ├── auth-sessions.md         # Authenticated scanning guide
│   ├── payloads.md              # Payload references
│   ├── advanced-techniques.md   # Advanced techniques
│   └── smart-contract-audit.md  # Web3 auditing guide
│
├── mcp/                         # MCP integrations
│   ├── hackerone-mcp/           # HackerOne public API integration
│   ├── burp-mcp-client/         # Burp Suite proxy integration
│   └── caido-mcp-client/        # Caido proxy integration
│
├── scripts/                     # Utility scripts
│   ├── dork_runner.py           # Automated dork execution
│   └── full_hunt.sh             # Full automation script
│
├── install.sh                   # System-wide installer
├── install_tools.sh             # External tool installer
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── config.example.json          # Example configuration
└── FAQ.md                       # Frequently asked questions
```

---

## Credits

- **BugHunter Pro v4.0** — 13-phase pipeline, 70+ JS secret patterns, entropy analysis, JS deep recon, all scanning phases
- **Claude Bug Bounty** (shuvonsec) — Modular architecture, multi-AI provider system, ReAct agent, validation gate, Web3 modules, memory system, MCP integrations, tests

---

## License

MIT
