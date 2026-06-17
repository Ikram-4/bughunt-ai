# BugHunter Pro v4.0

Command-line recon and bug-hunting helper for authorized security testing.

This project is intended to run on Linux or WSL/Kali/Ubuntu. Native Windows shells are not supported because the scanner uses Linux tools and shell pipelines.

## Quick Start

```bash
# 1. Install tools one time
chmod +x install.sh
sudo bash install.sh

# 2. Verify dependencies
python3 bughunter.py --check-tools

# 3. Run a full recon
python3 bughunter.py example.com

# 4. Run a single phase
python3 bughunter.py example.com --phase js
python3 bughunter.py example.com --phase dorks
python3 bughunter.py example.com --phase vulns

# 5. Run with an authenticated session cookie
python3 bughunter.py example.com --cookie "session=YOUR_COOKIE"
```

## Supported Runtime

- Python 3.8+
- Linux, WSL, Kali, Parrot, or Ubuntu 22.04+
- Go 1.20+
- Internet access for recon tools and public data sources

The script now stops early on native Windows so scans are not mistaken for reliable results there.

## Phases

| Phase | Purpose |
| --- | --- |
| `subs` | Passive subdomain discovery |
| `dns` | DNS resolution, bruteforce, permutations |
| `http` | HTTP probing, tech detection, screenshots |
| `ports` | High-value port scanning |
| `content` | Crawling and historical URL collection |
| `params` | Parameter candidate extraction |
| `js` | JavaScript download, endpoint extraction, secret scanning |
| `graphql` | GraphQL endpoint and introspection checks |
| `apifuzz` | API path and method discovery |
| `dorks` | Google/GitHub dork generation |
| `vulns` | Nuclei, CORS, CRLF, redirect, XSS, SQLi helper checks |
| `cloud` | Cloud bucket and storage checks |
| `github` | GitHub and secret scanning helpers |

## AI Secret Scanning

AI scanning is optional and runs after JavaScript collection.

```bash
export OPENAI_API_KEY="sk-..."
python3 bughunter.py example.com --phase js --ai-secrets

python3 bughunter.py example.com --phase js --ai-secrets-only --ai-provider ollama
```

Supported providers:

| Provider | Flag | Default model |
| --- | --- | --- |
| OpenAI-compatible | `--ai-provider openai` | `gpt-4o-mini` |
| Anthropic Claude | `--ai-provider claude` | `claude-sonnet-4-20250514` |
| Ollama | `--ai-provider ollama` | `llama3` |

## Output

By default, output is written to:

```text
hunt_<target>_<timestamp>/
```

Important folders:

```text
subdomains/   discovered subdomains
dns/          resolved domains and DNS details
web/          live URLs and HTTP fingerprints
endpoints/    crawled and historical URLs
params/       parameter candidate lists
js/           downloaded JavaScript and source-map data
secrets/      regex and AI secret findings
graphql/      GraphQL findings
api/          API fuzzing results
vulns/        scanner findings that need manual verification
dorks/        search dorks
```

## Important Notes

- Only scan targets you are authorized to test.
- Treat generated vulnerability output as a review queue. Manually verify findings before reporting them.
- Historical URLs can create many candidates even when live host probing finds few or no active hosts.
- Use WSL/Linux for real runs; native Windows is intentionally blocked.
