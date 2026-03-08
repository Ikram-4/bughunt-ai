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
