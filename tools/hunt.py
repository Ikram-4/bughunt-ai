#!/usr/bin/env python3
from __future__ import annotations
"""
Bug Hunter Pro — 13-Phase Recon + Vulnerability Pipeline
Combines the best of BugHunter Pro v4.0 and Claude Bug Bounty.

Phases:
  1. Passive Subdomains
  2. DNS Resolution + Permutations
  3. HTTP Probing + Tech Fingerprinting
  4. Port Scanning + Dangerous Service Detection
  5. Content Discovery + Sensitive File Probing
  6. Parameter Discovery (SSRF, redirect, XSS, IDOR)
  7. JS Deep Recon (download, source maps, secrets, endpoints, GraphQL in JS)
  8. GraphQL Detection & Introspection
  9. API Fuzzing
  10. Google Dork Generation
  11. Vulnerability Scanning (nuclei, CORS, CRLF, redirects, host header)
  12. Cloud Asset Discovery (S3, Firebase, GCP, Azure, DO)
  13. GitHub Secret Scanning + TruffleHog

Usage:
  python3 hunt.py --target example.com              # Full pipeline
  python3 hunt.py --target example.com --phase 7     # Single phase
  python3 hunt.py --target example.com --deep        # All 13 phases
  python3 hunt.py --target example.com --quick       # Quick scan (phases 1-5)
  python3 hunt.py --target example.com --phase js    # JS deep recon
  python3 hunt.py --target example.com --phase vulns # Vuln scan only
  python3 hunt.py --target example.com --no-ai       # Skip AI analysis
"""

import argparse, concurrent.futures, hashlib, ipaddress, itertools, json, math, os
import re, shutil, signal, socket, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from tools.auth_session import AuthSession, add_cli_args, session_from_args
    from tools.banner import print_banner
except ImportError:
    AuthSession = None
    def print_banner(): pass
    def add_cli_args(p): pass
    def session_from_args(a): return None

TOOLS_DIR = Path(__file__).resolve().parent
BASE_DIR  = TOOLS_DIR.parent
RECON_DIR = BASE_DIR / "recon"
TARGETS_DIR = BASE_DIR / "targets"
FINDINGS_DIR = BASE_DIR / "findings"
REPORTS_DIR  = BASE_DIR / "reports"
WORDLIST_DIR = BASE_DIR / "wordlists"

GREEN = "\033[0;32m"; RED = "\033[0;31m"; YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"; MAGENTA = "\033[0;35m"; BOLD = "\033[1m"; DIM = "\033[2m"; NC = "\033[0m"

TOOL_TIMEOUT = 300

def ok(msg):   print(f"{GREEN}{BOLD}[+]{NC} {msg}")
def info(msg): print(f"{CYAN}{BOLD}[*]{NC} {msg}")
def warn(msg): print(f"{YELLOW}{BOLD}[!]{NC} {msg}")
def err(msg):  print(f"{RED}{BOLD}[-]{NC} {msg}")
def hit(msg):  print(f"{MAGENTA}{BOLD}[HIT]{NC} {msg}")
def ph(msg):   print(f"\n{CYAN}{BOLD}[+]══════ {msg} ══════{NC}")
def die(msg):  print(f"{RED}[FATAL]{NC} {msg}"); sys.exit(1)

def run_cmd(cmd, timeout=None, capture=True):
    if timeout is None: timeout = TOOL_TIMEOUT
    if timeout: info(f"Running (timeout {timeout}s): {cmd[:120]}")
    else: info(f"Running (no timeout): {cmd[:120]}")
    try:
        kwargs = {}
        if os.name != "nt": kwargs["start_new_session"] = True
        p = subprocess.Popen(cmd, shell=True, text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.DEVNULL, **kwargs)
        stdout, _ = p.communicate(timeout=timeout if timeout else None)
        if p.returncode != 0: warn(f"Exit code {p.returncode}: {cmd[:120]}")
        return (stdout.strip() if capture and stdout else ""), p.returncode
    except subprocess.TimeoutExpired:
        try:
            if os.name != "nt": os.killpg(p.pid, signal.SIGTERM)
            else: p.kill()
            p.communicate(timeout=5)
        except: pass
        warn(f"Timed out after {timeout}s: {cmd[:120]}")
        return "", 1
    except Exception as e:
        warn(f"Command error: {e}")
        return "", 1

def check_tool(name):
    return shutil.which(name) is not None

def count_lines(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return sum(1 for l in f if l.strip())
    except: return 0

def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return [l.strip() for l in f if l.strip()]
    except: return []

def append_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def fetch_url(url, timeout=10, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore"), r.status
    except urllib.error.HTTPError as e: return "", e.code
    except: return "", 0

def detect_target_type(target):
    if os.path.isfile(target): return "list"
    try:
        net = ipaddress.ip_network(target, strict=False)
        return "cidr" if net.num_addresses > 1 else "ip"
    except ValueError: return "domain"

REQUIRED_TOOLS = [
    "subfinder", "assetfinder", "httpx", "nuclei", "naabu",
    "dnsx", "katana", "gau", "waybackurls", "getJS",
    "puredns", "subzy", "ffuf", "arjun", "trufflehog",
    "jsluice", "unfurl", "amass", "altdns", "jq"
]
OPTIONAL_TOOLS = ["masscan", "nmap", "feroxbuster", "wafw00f", "sqlmap", "dalfox", "aquatone", "gowitness", "hakrawler", "kr"]

def print_tool_status():
    ready = sum(1 for t in REQUIRED_TOOLS if check_tool(t))
    total = len(REQUIRED_TOOLS)
    missing_opt = sum(1 for t in OPTIONAL_TOOLS if not check_tool(t))
    color = GREEN if ready == total else YELLOW if ready >= total // 2 else RED
    print(f"  {color}Tools: {ready}/{total} required ready, {missing_opt} optional missing{NC}\n")

def check_tools_installed():
    ph("TOOL VERIFICATION")
    missing = []
    for t in REQUIRED_TOOLS:
        if check_tool(t): ok(t)
        else: warn(f"MISSING (required): {t}"); missing.append(t)
    for t in OPTIONAL_TOOLS:
        if check_tool(t): ok(f"{t} {DIM}(optional){NC}")
        else: info(f"missing (optional): {t}")
    if missing:
        warn(f"{len(missing)} required tools missing.")
    return missing

# ═══════════════════════════════════════════════════════════════════
# PHASE 1: Passive Subdomain Enumeration
# ═══════════════════════════════════════════════════════════════════

def phase_passive_subs(target, out):
    ph("PHASE 1: PASSIVE SUBDOMAIN ENUMERATION")
    subs_dir = out / "subdomains"; subs_dir.mkdir(exist_ok=True)
    if check_tool("subfinder"):
        info("subfinder (all sources, recursive)...")
        run_cmd(f"subfinder -d {target} -all -recursive -silent -o {subs_dir}/subfinder.txt")
        ok(f"subfinder: {count_lines(subs_dir/'subfinder.txt')} subs")
    if check_tool("assetfinder"):
        info("assetfinder...")
        run_cmd(f"assetfinder --subs-only {target} > {subs_dir}/assetfinder.txt")
        ok(f"assetfinder: {count_lines(subs_dir/'assetfinder.txt')} subs")
    if check_tool("amass"):
        info("amass passive...")
        run_cmd(f"amass enum -passive -d {target} -o {subs_dir}/amass.txt", timeout=300)
        ok(f"amass: {count_lines(subs_dir/'amass.txt')} subs")
    info("crt.sh certificate transparency...")
    try:
        body, code = fetch_url(f"https://crt.sh/?q=%.{target}&output=json")
        if code == 200 and body:
            entries = json.loads(body)
            names = set()
            for e in entries:
                for name in e.get("name_value", "").split("\n"):
                    name = name.strip().lstrip("*.")
                    if name.endswith(target): names.add(name)
            with open(subs_dir / "crt.txt", "w") as f: f.write("\n".join(sorted(names)))
            ok(f"crt.sh: {len(names)} subs")
    except Exception as e: warn(f"crt.sh: {e}")
    if check_tool("gau"):
        info("gau wayback harvest...")
        run_cmd(f"gau --subs {target} 2>/dev/null | grep -oP '(?:https?://)[a-zA-Z0-9._-]+\\.{re.escape(target)}' | sed 's|https\\?://||' | sort -u > {subs_dir}/gau_subs.txt")
        ok(f"gau: {count_lines(subs_dir/'gau_subs.txt')} subs")
    if check_tool("waybackurls"):
        info("waybackurls harvest...")
        run_cmd(f"waybackurls {target} 2>/dev/null | grep -oP '(?:https?://)[a-zA-Z0-9._-]+\\.{re.escape(target)}' | sed 's|https\\?://||' | sort -u > {subs_dir}/wayback_subs.txt")
    run_cmd(f"cat {subs_dir}/*.txt 2>/dev/null | grep -E '^[a-zA-Z0-9._-]+$' | grep -E '\\.{re.escape(target)}$|^{re.escape(target)}$' | sort -u > {subs_dir}/all_passive.txt")
    total = count_lines(subs_dir / "all_passive.txt")
    ok(f"Total passive unique subdomains: {total}")
    return total

# ═══════════════════════════════════════════════════════════════════
# PHASE 2: DNS Resolution + Permutations
# ═══════════════════════════════════════════════════════════════════

def phase_dns(target, out):
    ph("PHASE 2: DNS RESOLUTION + PERMUTATIONS")
    dns_dir = out / "dns"; subs_dir = out / "subdomains"; dns_dir.mkdir(exist_ok=True)
    info("Downloading fresh DNS resolvers...")
    resolvers = dns_dir / "resolvers.txt"
    try:
        body, _ = fetch_url("https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt")
        if body: resolvers.write_text(body); ok(f"Resolvers: {count_lines(resolvers)}")
    except:
        resolvers.write_text("8.8.8.8\n1.1.1.1\n9.9.9.9\n8.8.4.4\n")
    if check_tool("puredns"):
        wordlist = "/opt/SecLists/Discovery/DNS/dns-Jhaddix.txt"
        if os.path.exists(wordlist):
            info("puredns bruteforce...")
            run_cmd(f"puredns bruteforce {wordlist} {target} -r {resolvers} -o {subs_dir}/puredns_brute.txt", timeout=600)
    run_cmd(f"cat {subs_dir}/*.txt 2>/dev/null | sort -u > {subs_dir}/combined.txt")
    if check_tool("altdns"):
        perm_words = "/opt/SecLists/Discovery/DNS/altdns_words.txt"
        if os.path.exists(perm_words):
            info("altdns permutations...")
            run_cmd(f"altdns -i {subs_dir}/combined.txt -o {subs_dir}/altdns_perms.txt -w {perm_words}", timeout=300)
    if check_tool("gotator"):
        info("gotator permutations...")
        run_cmd(f"gotator -sub {subs_dir}/combined.txt -depth 1 -numbers 3 2>/dev/null >> {subs_dir}/altdns_perms.txt", timeout=120)
    info("Resolving all candidates...")
    run_cmd(f"cat {subs_dir}/combined.txt {subs_dir}/altdns_perms.txt 2>/dev/null | sort -u | puredns resolve -r {resolvers} -o {dns_dir}/resolved.txt 2>/dev/null || dnsx -l {subs_dir}/combined.txt -silent -o {dns_dir}/resolved.txt", timeout=600)
    ok(f"Resolved: {count_lines(dns_dir/'resolved.txt')} live subs")
    if check_tool("dnsx"):
        info("Collecting DNS records...")
        run_cmd(f"dnsx -l {dns_dir}/resolved.txt -a -aaaa -cname -mx -resp -silent -o {dns_dir}/dns_details.txt", timeout=300)
        info("Checking CNAMEs for takeovers...")
        cname_out, _ = run_cmd(f"dnsx -l {dns_dir}/resolved.txt -cname -resp -silent", timeout=120)
        dangling_services = [
            "amazonaws.com", "heroku", "github.io", "shopify", "fastly",
            "pantheon.io", "zendesk.com", "readme.io", "ghost.io",
            "helpscout", "statuspage.io", "surge.sh", "bitbucket.io",
            "netlify", "wordpress.com", "smugmug", "azure"]
        if cname_out:
            takeover_dir = out / "vulns"; takeover_dir.mkdir(exist_ok=True)
            for line in cname_out.split("\n"):
                for svc in dangling_services:
                    if svc in line.lower():
                        hit(f"CNAME TAKEOVER: {line}")
                        append_file(str(takeover_dir / "cname_takeovers.txt"), line)
    return count_lines(dns_dir / "resolved.txt")

# ═══════════════════════════════════════════════════════════════════
# PHASE 3: HTTP Probing + Tech Fingerprinting
# ═══════════════════════════════════════════════════════════════════

def phase_http(target, out):
    ph("PHASE 3: HTTP PROBING + TECH FINGERPRINTING")
    web_dir = out / "web"; dns_dir = out / "dns"; web_dir.mkdir(exist_ok=True)
    if not check_tool("httpx"): warn("httpx not found"); return 0
    resolved = dns_dir / "resolved.txt"
    if not resolved.exists() or count_lines(resolved) == 0:
        warn("No resolved subs — probing target directly")
        tmp_targets = web_dir / "httpx_targets.txt"
        tmp_targets.write_text(f"{target}\nwww.{target}\n")
        probe_input = str(tmp_targets)
    else: probe_input = str(resolved)
    info("httpx probing all resolved subdomains...")
    run_cmd(f"httpx -l {probe_input} -tech-detect -status-code -title -web-server -ip -cdn -silent -o {web_dir}/httpx_full.txt", timeout=600)
    ok(f"Live hosts: {count_lines(web_dir/'httpx_full.txt')}")
    run_cmd(f"cat {web_dir}/httpx_full.txt | grep -oP 'https?://[^\\s]+' | sort -u > {web_dir}/live_urls.txt")
    run_cmd(f"cat {web_dir}/httpx_full.txt | grep '\\[403\\]' | grep -oP 'https?://[^\\s]+' > {web_dir}/403_hosts.txt")
    fours = count_lines(web_dir / "403_hosts.txt")
    if fours > 0: warn(f"403 hosts: {fours} — check web/403_hosts.txt")
    if check_tool("wafw00f"):
        info("WAF detection...")
        for url in read_lines(web_dir / "live_urls.txt")[:20]:
            run_cmd(f"wafw00f {url} -o {web_dir}/waf_{hashlib.md5(url.encode()).hexdigest()[:8]}.txt 2>/dev/null &")
    screenshots_dir = out / "screenshots"; screenshots_dir.mkdir(exist_ok=True)
    live_file = web_dir / "live_urls.txt"
    if check_tool("gowitness"):
        info("gowitness screenshots...")
        run_cmd(f"gowitness scan file -f {live_file} --screenshot-path {screenshots_dir} --write-db=false", timeout=600)
        screenshots = len(list(screenshots_dir.glob("*.png")))
        ok(f"gowitness: {screenshots} screenshots")
    elif check_tool("aquatone"):
        info("aquatone screenshots...")
        run_cmd(f"cat {live_file} | aquatone -out {screenshots_dir}/aquatone -silent -threads 5", timeout=600)
    live = count_lines(web_dir / "live_urls.txt"); ok(f"Live URLs: {live}")
    return live

# ═══════════════════════════════════════════════════════════════════
# PHASE 4: Port Scanning
# ═══════════════════════════════════════════════════════════════════

def phase_ports(target, out):
    ph("PHASE 4: PORT SCANNING")
    ips_dir = out / "ips"; dns_dir = out / "dns"; ips_dir.mkdir(exist_ok=True)
    run_cmd(f"cat {dns_dir}/dns_details.txt 2>/dev/null | grep -oP '\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}' | sort -u > {ips_dir}/all_ips.txt")
    ip_count = count_lines(ips_dir / "all_ips.txt")
    if ip_count == 0:
        info("Resolving target directly...")
        ip_out, _ = run_cmd(f"dig +short {target} A 2>/dev/null || host {target} 2>/dev/null | grep -oP '\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}'")
        if ip_out:
            ips = sorted(set(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_out)))
            if ips:
                (ips_dir / "all_ips.txt").write_text("\n".join(ips) + "\n")
                ip_count = len(ips); ok(f"Resolved {ip_count} IPs")
    if ip_count == 0: warn("No IPs found"); return
    critical_ports = "80,443,8080,8443,8888,9200,9300,6379,27017,5432,3306,5601,4848,7001,9090,3000,8008,8161,50000,9000,4443,7443,9443,8090,8060,3389,5985,5986,22"
    if check_tool("naabu"):
        run_cmd(f"naabu -l {ips_dir}/all_ips.txt -p {critical_ports} -silent -o {ips_dir}/open_ports.txt", timeout=300)
        ok(f"Open ports: {count_lines(ips_dir/'open_ports.txt')}")
        try:
            ports_content = (ips_dir / "open_ports.txt").read_text()
            dangerous = {"9200":"ELASTICSEARCH (no-auth!)","9300":"ELASTICSEARCH CLUSTER",
                         "6379":"REDIS (no-auth!)","27017":"MONGODB (no-auth!)","5601":"KIBANA",
                         "4848":"GLASSFISH ADMIN","7001":"WEBLOGIC CVE-2020-14882"}
            for port, svc in dangerous.items():
                if f":{port}" in ports_content: hit(f"{svc} — port {port} open!")
        except: pass
    if check_tool("nmap") and ip_count <= 50:
        info("nmap service detection...")
        run_cmd(f"nmap -sV -sC -p 9200,6379,27017,5601,8080,8443,4848,7001 -iL {ips_dir}/all_ips.txt -oA {ips_dir}/nmap_services --open", timeout=300)

# ═══════════════════════════════════════════════════════════════════
# PHASE 5: Content Discovery
# ═══════════════════════════════════════════════════════════════════

def phase_content(target, out, session_cookie=None):
    ph("PHASE 5: CONTENT DISCOVERY")
    ep_dir = out / "endpoints"; web_dir = out / "web"; ep_dir.mkdir(exist_ok=True)
    cookie_flag = f"-H 'Cookie: {session_cookie}'" if session_cookie else ""
    live_urls = read_lines(web_dir / "live_urls.txt")
    crawl_targets = live_urls[:20] if live_urls else [f"https://{target}", f"http://{target}"]
    if check_tool("katana"):
        info("katana crawl...")
        for url in crawl_targets:
            run_cmd(f"katana -u '{url}' -jc -d 5 -aff -ef css,png,svg,ico,woff,woff2,ttf -silent >> {ep_dir}/katana_unauth.txt", timeout=180)
        run_cmd(f"sort -u {ep_dir}/katana_unauth.txt -o {ep_dir}/katana_unauth.txt")
        ok(f"katana: {count_lines(ep_dir/'katana_unauth.txt')} URLs")
        if session_cookie:
            for url in crawl_targets:
                run_cmd(f"katana -u '{url}' -jc -d 5 -H 'Cookie: {session_cookie}' -silent >> {ep_dir}/katana_auth.txt", timeout=180)
    if check_tool("gau"):
        run_cmd(f"gau {target} --subs 2>/dev/null | sort -u > {ep_dir}/gau_urls.txt", timeout=300)
        ok(f"gau historical: {count_lines(ep_dir/'gau_urls.txt')} URLs")
    if check_tool("waybackurls"):
        run_cmd(f"waybackurls {target} 2>/dev/null | sort -u >> {ep_dir}/gau_urls.txt", timeout=180)
    if check_tool("hakrawler"):
        info("hakrawler...")
        for url in crawl_targets[:10]:
            run_cmd(f"echo '{url}' | hakrawler -d 3 -js -subs 2>/dev/null >> {ep_dir}/hakrawler.txt", timeout=60)
    if check_tool("feroxbuster"):
        wordlist = "/opt/SecLists/Discovery/Web-Content/raft-large-words.txt"
        if os.path.exists(wordlist):
            info("feroxbuster dir fuzzing...")
            for url in crawl_targets[:3]:
                safe = hashlib.md5(url.encode()).hexdigest()[:8]
                run_cmd(f"feroxbuster -u '{url}' -w {wordlist} -x php,asp,aspx,jsp,json,txt,bak,old,zip,env,config -r -s 200,301,302,403 -q --no-state -o {ep_dir}/ferox_{safe}.txt", timeout=300)
    if check_tool("kr"):
        kite = "/opt/kiterunner/routes-large.kite"
        if os.path.exists(kite):
            info("kiterunner API routes...")
            for url in crawl_targets[:10]:
                safe = hashlib.md5(url.encode()).hexdigest()[:8]
                run_cmd(f"kr scan '{url}' -w {kite} -o {ep_dir}/kr_{safe}.txt", timeout=120)
    # Sensitive file probing
    info("Probing sensitive files on live hosts...")
    sensitive_dir = out / "vulns"; sensitive_dir.mkdir(exist_ok=True)
    sensitive_paths = [
        "/.git/HEAD","/.git/config","/.env","/.env.local","/.env.production",
        "/robots.txt","/sitemap.xml","/.DS_Store","/crossdomain.xml",
        "/server-status","/server-info","/.htaccess","/.htpasswd",
        "/wp-config.php.bak","/web.config","/config.json","/config.yaml",
        "/package.json","/composer.json","/Dockerfile","/docker-compose.yml",
        "/.well-known/security.txt","/swagger.json","/swagger-ui.html",
        "/openapi.json","/api-docs","/graphql","/graphiql",
        "/actuator","/actuator/env","/actuator/health","/actuator/configprops",
        "/debug","/trace","/info","/metrics","/heapdump",
        "/elmah.axd","/phpinfo.php","/test.php","/.svn/entries",
        "/backup.zip","/backup.sql","/db.sql","/dump.sql",
        "/WEB-INF/web.xml","/META-INF/MANIFEST.MF",
        "/console","/admin","/login","/register",
    ]
    for base_url in crawl_targets[:5]:
        base = base_url.rstrip("/")
        for path in sensitive_paths:
            body, code = fetch_url(f"{base}{path}", timeout=5)
            if code == 200 and len(body) > 10:
                is_git = path.startswith("/.git") and ("ref:" in body or "[core]" in body)
                is_env = path == "/.env" and ("=" in body and any(k in body.upper() for k in ["KEY","SECRET","PASSWORD","TOKEN","DB_"]))
                is_json = path.endswith(".json") and (body.strip().startswith("{") or body.strip().startswith("["))
                is_actuator = "actuator" in path and (body.strip().startswith("{") or body.strip().startswith("["))
                is_php = path in ["/phpinfo.php"] and "phpinfo" in body.lower()
                is_backup = any(path.endswith(ext) for ext in [".zip", ".sql", ".bak"])
                if any([is_git, is_env, is_json, is_actuator, is_php, is_backup]):
                    hit(f"SENSITIVE FILE: {base}{path}")
                    append_file(str(sensitive_dir / "sensitive_files.txt"), f"{base}{path}")
    run_cmd(f"cat {ep_dir}/*.txt 2>/dev/null | sort -u > {ep_dir}/all_urls.txt")
    total = count_lines(ep_dir / "all_urls.txt"); ok(f"Total URLs: {total}")
    return total

# ═══════════════════════════════════════════════════════════════════
# PHASE 6: Parameter Discovery
# ═══════════════════════════════════════════════════════════════════

def phase_params(target, out):
    ph("PHASE 6: PARAMETER DISCOVERY")
    params_dir = out / "params"; ep_dir = out / "endpoints"; params_dir.mkdir(exist_ok=True)
    if check_tool("unfurl"):
        run_cmd(f"cat {ep_dir}/gau_urls.txt 2>/dev/null | unfurl keys | sort -u > {params_dir}/historical_params.txt")
        ok(f"Historical params: {count_lines(params_dir/'historical_params.txt')}")
    all_urls = ep_dir / "all_urls.txt"
    ssrf_params = r"(url|redirect|next|dest|callback|path|uri|href|src|fetch|load|import|export|proxy|target|return|file|view|preview|show|link|host|domain|page|open|to|forward|redir|r|u|ref)="
    run_cmd(f"grep -iE '{ssrf_params}' {all_urls} 2>/dev/null | sort -u > {params_dir}/ssrf_prone.txt")
    ssrf_cnt = count_lines(params_dir / "ssrf_prone.txt")
    if ssrf_cnt > 0: hit(f"SSRF-prone params: {ssrf_cnt} URLs")
    redirect_params = r"(url=|return=|next=|goto=|redirect=|redir=|dest=|destination=|r=|go=|target=|continue=|back=|jump=)"
    run_cmd(f"grep -iE '{redirect_params}' {all_urls} 2>/dev/null | sort -u > {params_dir}/redirect_prone.txt")
    ok(f"Redirect-prone: {count_lines(params_dir/'redirect_prone.txt')}")
    inject_params = r"(q=|search=|id=|uid=|user_id=|pid=|query=|keyword=|cmd=|exec=|order=|sort=|filter=|cat=|type=|role=|user=|name=|where=|select=|report=)"
    run_cmd(f"grep -iE '{inject_params}' {all_urls} 2>/dev/null | sort -u > {params_dir}/injection_prone.txt")
    ok(f"Injection-prone: {count_lines(params_dir/'injection_prone.txt')}")
    xss_params = r"(q=|search=|query=|keyword=|lang=|title=|msg=|message=|comment=|body=|text=|content=|html=|value=|data=|input=|name=|username=|email=|error=|preview=|template=|markup=|callback=|jsonp=)"
    run_cmd(f"grep -iE '{xss_params}' {all_urls} 2>/dev/null | sort -u > {params_dir}/xss_prone.txt")
    xss_cnt = count_lines(params_dir / "xss_prone.txt")
    if xss_cnt > 0: hit(f"XSS-prone params: {xss_cnt} URLs")
    idor_params = r"(id=|uid=|user_id=|pid=|account=|order_id=|invoice=|doc=|document=|profile=|ref=|number=|no=|num=)"
    run_cmd(f"grep -iE '{idor_params}' {all_urls} 2>/dev/null | sort -u > {params_dir}/idor_prone.txt")
    idor_cnt = count_lines(params_dir / "idor_prone.txt")
    if idor_cnt > 0: hit(f"IDOR-prone params: {idor_cnt} URLs")
    if check_tool("arjun"):
        info("arjun hidden param discovery...")
        for url in read_lines(out / "web" / "live_urls.txt")[:15]:
            safe = hashlib.md5(url.encode()).hexdigest()[:8]
            run_cmd(f"arjun -u '{url}' -m GET -oJ {params_dir}/arjun_{safe}.json -q", timeout=60)

# ═══════════════════════════════════════════════════════════════════
# PHASE 7: JS Deep Recon (the crown jewel from local project)
# ═══════════════════════════════════════════════════════════════════

SECRET_PATTERNS = [
    ("AWS Access Key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", "CRITICAL"),
    ("AWS Secret Key", r"(?:aws[._-]?)?(?:secret[._-]?access[._-]?key|secretAccessKey|awsSecretAccessKey|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*[\"']?([A-Za-z0-9/+=]{40})[\"']?", "CRITICAL"),
    ("Google API Key", r"AIza[0-9A-Za-z\-_]{35}", "HIGH"),
    ("Google OAuth ID", r"\d{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com", "HIGH"),
    ("Firebase URL", r"https://[a-zA-Z0-9\-]+\.firebaseio\.com", "MEDIUM"),
    ("Stripe Secret", r"sk_live_[0-9a-zA-Z]{24,99}", "CRITICAL"),
    ("Stripe Publishable", r"pk_(live|test)_[0-9a-zA-Z]{24,99}", "INFO"),
    ("GitHub Token", r"(ghp_|gho_|ghu_|ghs_|ghr_)[0-9a-zA-Z]{36}", "CRITICAL"),
    ("GitLab Token", r"glpat-[0-9a-zA-Z\-_]{20}", "CRITICAL"),
    ("Slack Token", r"xox[baprs]-[0-9A-Za-z\-]{10,250}", "HIGH"),
    ("Discord Webhook", r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_\-]+", "HIGH"),
    ("Twilio SID", r"AC[a-zA-Z0-9]{32}", "HIGH"),
    ("SendGrid Key", r"SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}", "HIGH"),
    ("Mailgun Key", r"key-[0-9a-zA-Z]{32}", "HIGH"),
    ("JWT Token", r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]*", "HIGH"),
    ("Bearer Token", r"Bearer\s+[a-zA-Z0-9._\-]{20,}", "HIGH"),
    ("Private Key", r"-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----", "CRITICAL"),
    ("Basic Auth URL", r"https?://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_!@#$%^&*]+@[a-zA-Z0-9.-]+", "CRITICAL"),
    ("MongoDB URI", r"mongodb(\+srv)?://[^\s\"'<>]{10,}", "CRITICAL"),
    ("PostgreSQL URI", r"postgres(ql)?://[^\s\"'<>]{10,}", "CRITICAL"),
    ("MySQL URI", r"mysql://[^\s\"'<>]{10,}", "CRITICAL"),
    ("OpenAI Key", r"sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}", "CRITICAL"),
    ("OpenAI Project Key", r"sk-proj-[a-zA-Z0-9_\-]{80,}", "CRITICAL"),
    ("Anthropic Key", r"sk-ant-[a-zA-Z0-9_\-]{80,}", "CRITICAL"),
    ("HuggingFace Token", r"hf_[a-zA-Z0-9]{34}", "HIGH"),
    ("Shopify Token", r"(shpat_|shpss_|shppa_)[a-fA-F0-9]{32}", "CRITICAL"),
    ("NPM Token", r"npm_[a-zA-Z0-9]{36}", "CRITICAL"),
    ("Azure Secret", r"(?:azure|AZURE).*(?:secret|SECRET|key|KEY)\s*[:=]\s*[\"'][A-Za-z0-9+/=]{30,}[\"']", "CRITICAL"),
    ("DigitalOcean Token", r"dop_v1_[a-f0-9]{64}", "CRITICAL"),
    ("API Key Generic", r"(?:api[._-]?key|apikey|api[._-]?secret|access[._-]?key)\s*[:=]+\s*[\"'][^\"']{10,}[\"']", "HIGH"),
    ("Password", r"(?:password|passwd|pwd|passphrase|PASS|PASSWORD)\s*[:=]+\s*[\"'][^\"']{4,}[\"']", "HIGH"),
    ("Internal URL", r"https?://(internal\.|staging\.|dev\.|localhost|127\.0\.0\.1|192\.168\.|10\.)[^\s\"']+", "MEDIUM"),
    ("Feature Flag", r"(isAdmin|adminMode|debugMode|devMode|featureFlag|isSuperUser)\s*[:=]", "MEDIUM"),
    ("TODO/FIXME", r"(TODO|FIXME|HACK|backdoor|hardcoded|remove.?before.?prod)", "INFO"),
    ("Debug Statement", r"(console\.log|debugger;|alert\(|print_r\(|var_dump\()", "INFO"),
    ("Hardcoded Creds", r"(?:username|user|login)\s*[:=]+\s*[\"'][^\"']{3,}[\"'].*(?:password|passwd|pwd)\s*[:=]+\s*[\"'][^\"']{3,}[\"']", "CRITICAL"),
    ("OAuth Client Secret", r"(?:client_secret|CLIENT_SECRET)\s*[:=]\s*[\"'][a-zA-Z0-9_\-]{20,}[\"']", "HIGH"),
    ("Frontend Env Value", r"(?:REACT_APP|NEXT_PUBLIC|VITE|PUBLIC)_[A-Z0-9_]{3,}\s*[:=]\s*[\"'][^\"']{8,}[\"']", "MEDIUM"),
]

def calc_shannon_entropy(s):
    if not s: return 0
    freq = {}
    for c in s: freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((c/length) * math.log2(c/length) for c in freq.values())

def scan_js_secrets(js_dir, secrets_dir, extra_dirs=None):
    secrets_dir = Path(secrets_dir); scan_roots = [Path(js_dir)]
    for extra in extra_dirs or []:
        p = Path(extra)
        if p.exists(): scan_roots.append(p)
    allowed = {".js", ".mjs", ".jsx", ".ts", ".tsx", ".map", ".txt"}
    scan_files = []; seen = set()
    for root in scan_roots:
        if not root.exists(): continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in allowed: continue
            r = str(path.resolve())
            if r in seen: continue
            seen.add(r)
            label = f"{path.parent.name}/{path.name}" if path.parent.name in ("maps","sources") else path.name
            scan_files.append((path, label))
    if not scan_files: return {}
    findings = {}
    def save_finding(pattern_name, severity, matches):
        if not matches: return
        deduped = []; seen_m = set()
        for item in matches:
            m = (item.get("file",""), item.get("match",""), item.get("context",""))
            if m in seen_m: continue
            seen_m.add(m); deduped.append(item)
        if not deduped: return
        findings[pattern_name] = {"severity": severity, "matches": deduped}
        safe_name = pattern_name.lower().replace(' ', '_').replace('/', '_')
        with open(secrets_dir / f"js_{safe_name}.json", "w") as f:
            json.dump(deduped, f, indent=2)
    for pattern_name, pattern, severity in SECRET_PATTERNS:
        matches = []; regex = re.compile(pattern, re.IGNORECASE)
        for jsf, label in scan_files:
            try:
                content = jsf.read_text(errors="ignore")
                for m in regex.finditer(content):
                    snippet = content[max(0,m.start()-80):m.end()+120].replace("\n"," ")
                    matches.append({"file":label,"match":m.group(),"context":snippet[:300]})
            except: pass
        save_finding(pattern_name, severity, matches)
    kv_re = re.compile(
        r"""(?:(?P<q>["'])(?P<qkey>[A-Za-z0-9_$ .\-]{2,80})(?P=q)|(?P<key>[A-Za-z_$][\w$.-]{1,80}))"""
        r"""\s*[:=]\s*(?P<quote>["'`])(?P<value>[^"'`\r\n]{3,300})(?P=quote)""", re.IGNORECASE)
    placeholder_values = {"true","false","null","undefined","none","todo","changeme","change_me","example","sample"}
    def norm_key(key): return re.sub(r"[^a-z0-9]","",key.lower())
    def is_secret_key(key):
        k = norm_key(key)
        return any(x in k for x in ["password","passwd","pwd","passphrase","secret","token","credential","privatekey","clientsecret","apikey","accesskey","secretaccesskey","sessiontoken"])
    assignment_hits = []; credential_pairs = []
    for jsf, label in scan_files:
        try: content = jsf.read_text(errors="ignore")
        except: continue
        kvs = []
        for m in kv_re.finditer(content):
            key = (m.group("qkey") or m.group("key") or "").strip()
            value = (m.group("value") or "").strip()
            if not key or value.lower() in placeholder_values: continue
            context = content[max(0,m.start()-250):m.end()+250].replace("\n"," ")
            kvs.append({"key":key,"value":value,"start":m.start(),"end":m.end(),"context":context})
            if is_secret_key(key) and len(value) >= 4:
                assignment_hits.append({"file":label,"match":f"{key}={value[:100]}","context":context[:350]})
        identities = [i for i in kvs if is_secret_key(i["key"]) and len(i["value"]) >= 4]
        secrets_list = [s for s in kvs if is_secret_key(s["key"]) and len(s["value"]) >= 4]
        for secret in secrets_list:
            for identity in identities:
                if abs(secret["start"] - identity["start"]) > 1800: continue
                credential_pairs.append({"file":label,"match":f"{identity['key']}={identity['value'][:80]} | {secret['key']}={secret['value'][:80]}"})
    save_finding("Sensitive_Key_Assignment","HIGH",assignment_hits)
    save_finding("Credential_Pair","CRITICAL",credential_pairs)
    # Entropy-based
    high_entropy_re = re.compile(
        r"""(?:[a-zA-Z0-9_$]*?(?:secret|key|token|password|passwd|pwd|passphrase|credential|apikey|api_key|access_key|private|session|auth|hash|salt|cipher)[a-zA-Z0-9_$]*?)"""
        r"""\s*[:=]\s*["']([A-Za-z0-9+/=_\-.$@!]{16,})["']""", re.IGNORECASE)
    entropy_hits = []
    for jsf, label in scan_files:
        try: content = jsf.read_text(errors="ignore")
        except: continue
        for m in high_entropy_re.finditer(content):
            val = m.group(1); ent = calc_shannon_entropy(val)
            if ent > 3.5 and len(val) >= 16 and val.lower() not in ("true","false","null","undefined","none"):
                snippet = content[max(0,m.start()-80):m.end()+120].replace("\n"," ")
                entropy_hits.append({"file":label,"match":val[:80],"entropy":round(ent,2),"context":snippet[:300]})
    save_finding("High_Entropy_Secrets","HIGH",entropy_hits)
    return findings

def phase_js(target, out):
    ph("PHASE 7: JAVASCRIPT DEEP RECON")
    js_dir = out / "js"; files_dir = js_dir / "files"; maps_dir = js_dir / "maps"
    ep_dir = out / "endpoints"; secrets_dir = out / "secrets"; web_dir = out / "web"
    for d in [js_dir, files_dir, maps_dir, secrets_dir, ep_dir]: d.mkdir(exist_ok=True)
    js_urls_file = js_dir / "js_urls.txt"

    def normalize_js_url(ref, base_url=None):
        ref = (ref or "").strip().strip('"\'`<>')
        if not ref or ref.startswith(("data:","blob:","javascript:")): return None
        if ref.startswith("//"): ref = "https:" + ref
        elif base_url and not ref.startswith(("http://","https://")):
            ref = urllib.parse.urljoin(base_url, ref)
        if not ref.startswith(("http://","https://")): return None
        parsed = urllib.parse.urlparse(ref)
        path = parsed.path.lower()
        if path.endswith((".js",".mjs",".jsx",".ts",".tsx")) or "/_next/static/" in path or "/assets/" in path or "/static/" in path:
            return urllib.parse.urlunparse(parsed._replace(fragment=""))
        return None

    def extract_js_refs(content, base_url=None):
        refs = set()
        patterns = [r'<script[^>]+src=["\']([^"\']+)["\']',
            r'(?:import|from)\s*["\']([^"\']+)["\']',
            r'import\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'(?:require|importScripts|load)\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'(?:src|href|url)\s*[:=]\s*["\']([^"\']+\.(?:js|mjs|jsx|ts|tsx)(?:[?#][^"\']*)?)["\']',
            r'["\']([^"\']+\.(?:js|mjs|jsx|ts|tsx)(?:[?#][^"\']*)?)["\']',
            r'sourceMappingURL=([^\s*]+)']
        for pat in patterns:
            for m in re.finditer(pat, content, flags=re.I):
                ref = m.group(1)
                if ref.endswith(".map"): ref = ref[:-4]
                url = normalize_js_url(ref, base_url)
                if url: refs.add(url)
        return refs

    info("Collecting JS URLs from all sources...")
    run_cmd(f"cat {ep_dir}/all_urls.txt 2>/dev/null | grep -E '\\.js([\\?#]|$)' | sort -u > {js_urls_file}")
    run_cmd(f"cat {ep_dir}/gau_urls.txt 2>/dev/null | grep -E '\\.js([\\?#]|$)' | sort -u >> {js_urls_file}")
    if not count_lines(js_urls_file):
        if check_tool("gau"):
            run_cmd(f"gau --blacklist png,jpg,gif,svg,css,woff,woff2,ttf,eot,ico,pdf,zip,tgz,gz --o {js_dir / 'gau_js_urls.txt'} {target} 2>/dev/null")
            run_cmd(f"grep -E '\\.js([\\?#]|$)' {js_dir / 'gau_js_urls.txt'} 2>/dev/null >> {js_urls_file}")
        if check_tool("waybackurls"):
            run_cmd(f"waybackurls {target} 2>/dev/null | grep -E '\\.js([\\?#]|$)' >> {js_urls_file}")

    collected_js = set(read_lines(js_urls_file))
    for src_file in [ep_dir/"all_urls.txt", ep_dir/"gau_urls.txt", ep_dir/"katana_unauth.txt", ep_dir/"katana_auth.txt"]:
        if src_file.exists():
            for url in read_lines(src_file):
                n = normalize_js_url(url)
                if n: collected_js.add(n)
    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls: live_urls = [f"https://{target}", f"http://{target}"]
    info("Extracting scripts from live HTML pages...")
    base_origins = set()
    for page_url in live_urls[:50]:
        parsed = urllib.parse.urlparse(page_url)
        if parsed.scheme and parsed.netloc:
            base_origins.add(f"{parsed.scheme}://{parsed.netloc}")
        body, code = fetch_url(page_url, timeout=10)
        if code in (200,401,403) and body:
            collected_js.update(extract_js_refs(body, page_url))
    with open(js_urls_file, "a") as f:
        for url in sorted(collected_js): f.write(url + "\n")
    run_cmd(f"sort -u {js_urls_file} -o {js_urls_file}")
    js_count = count_lines(js_urls_file); ok(f"JS files discovered: {js_count}")

    info("Downloading JS files...")
    js_urls = read_lines(js_urls_file)
    source_by_file = {}
    def download_js(url):
        try:
            fname = hashlib.md5(url.encode()).hexdigest() + ".js"
            out_path = files_dir / fname
            if out_path.exists(): source_by_file[out_path.name] = url; return out_path.name
            body, code = fetch_url(url, timeout=15)
            if code in (200,401,403) and body and ("javascript" in body[:500].lower() or len(body) > 200):
                out_path.write_text(body); source_by_file[out_path.name] = url
                return out_path.name
        except: pass
        return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(download_js, js_urls[:3000]))
    downloaded = len(list(files_dir.glob("*.js"))); ok(f"Downloaded: {downloaded} JS files")

    info("Recursive JS crawling for imports...")
    for depth in range(3):
        new_js = set()
        for jsf in files_dir.glob("*.js"):
            try:
                content = jsf.read_text(errors="ignore")
                base_url = source_by_file.get(jsf.name)
                if not base_url and js_urls: base_url = js_urls[0]
                new_js.update(extract_js_refs(content, base_url))
            except: pass
        new_js -= set(read_lines(js_urls_file))
        if not new_js: break
        info(f"Depth {depth+1}: {len(new_js)} new candidates")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            list(ex.map(download_js, list(new_js)[:500]))
    # Source maps
    info("Checking for source maps...")
    map_candidates = {url + ".map" for url in read_lines(js_urls_file)[:1000]}
    def check_map(url):
        body, code = fetch_url(url, timeout=10)
        return url if code == 200 and "mappings" in body else None
    map_found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(check_map, sorted(map_candidates)[:1500]))
        map_found = [r for r in results if r]
    if map_found:
        (js_dir / "source_maps_found.txt").write_text("\n".join(map_found))
        hit(f"SOURCE MAPS FOUND: {len(map_found)}")
        for map_url in map_found:
            fname = hashlib.md5(map_url.encode()).hexdigest() + ".map"
            body, _ = fetch_url(map_url)
            if body: (maps_dir / fname).write_text(body)
    else: ok("No public source maps found")

    if check_tool("jsluice"):
        info("JSluice analysis...")
        run_cmd(f"find {files_dir} -name '*.js' | xargs -P5 -I{{}} jsluice urls {{}} 2>/dev/null | grep -oP '\"url\":\\s*\"\\K[^\"]+' | sort -u > {ep_dir}/jsluice_endpoints.txt")
        run_cmd(f"find {files_dir} -name '*.js' | xargs -P5 -I{{}} jsluice secrets {{}} 2>/dev/null > {secrets_dir}/jsluice_secrets.json")
        ok(f"JSluice endpoints: {count_lines(ep_dir/'jsluice_endpoints.txt')}")

    # JS analysis: endpoints, API calls, GraphQL
    info("Advanced JS analysis...")
    analysis_blobs = []; all_endpoints = set(); all_absolute_urls = set(); api_calls = []
    graphql_ops = []; client_routes = set(); storage_keys = set(); interesting_config = set()
    ignore_exts = (".png",".jpg",".jpeg",".gif",".svg",".css",".ico",".woff",".woff2",".ttf",".mp4",".webp")
    for jsf in files_dir.glob("*.js"):
        try: analysis_blobs.append((jsf.name, jsf.read_text(errors="ignore"), source_by_file.get(jsf.name,"")))
        except: pass
    # Source map extraction
    if list(maps_dir.glob("*.map")):
        info("Extracting source map sources...")
        src_extract = maps_dir / "sources"; src_extract.mkdir(exist_ok=True)
        for map_file in maps_dir.glob("*.map"):
            try:
                data = json.loads(map_file.read_text(errors="ignore"))
                sc = data.get("sourcesContent") or []
                for idx, src in enumerate(data.get("sources") or []):
                    if idx < len(sc) and sc[idx]:
                        safe = re.sub(r'[^A-Za-z0-9_.-]+','_',os.path.basename(src) or 'source.txt')[:80]
                        fname = f"{hashlib.md5((map_file.name+src).encode()).hexdigest()[:10]}_{safe}"
                        (src_extract / fname).write_text(sc[idx])
                        analysis_blobs.append((f"sourcemap:{map_file.name}:{src}", sc[idx], ""))
            except: pass
    for label, content, base_url in analysis_blobs:
        for m in re.finditer(r'"(/[a-zA-Z0-9_/${}?.=&%:,@+\-./]{2,})"', content):
            all_endpoints.add(m.group(1))
        for m in re.finditer(r"'(/[a-zA-Z0-9_/${}?.=&%:,@+\-./]{2,})'", content):
            all_endpoints.add(m.group(1))
        for m in re.finditer(r"https?://[^\s\"'`<>]+", content):
            all_absolute_urls.add(m.group())
        for m in re.finditer(r"fetch\s*\(\s*(['\"`])([^'\"`]{3,})\1", content, flags=re.I|re.S):
            url = m.group(2)
            if not url.lower().endswith(ignore_exts): api_calls.append({"file":label,"method":"GET","url":url})
        for m in re.finditer(r"axios\.(get|post|put|patch|delete|head|options)\s*\(\s*(['\"`])([^'\"`]{3,})\2", content, flags=re.I):
            api_calls.append({"file":label,"method":m.group(1).upper(),"url":m.group(3)})
        for m in re.finditer(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)?\s*(?:\([^)]*\))?\s*\{", content):
            graphql_ops.append({"file":label,"type":m.group(1),"name":m.group(2) or "anonymous"})
        for m in re.finditer(r"(?:localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)\s*\(\s*['\"]([^'\"]+)['\"]", content):
            storage_keys.add(f"{m.group(1)}\t{label}")
        for m in re.finditer(r"(?:isAdmin|adminMode|debugMode|devMode|featureFlag|isSuperUser)\s*[:=]", content):
            interesting_config.add(f"feature_flag = {m.group()}\t{label}")

    if all_endpoints:
        (ep_dir/"js_extracted_endpoints.txt").write_text("\n".join(sorted(all_endpoints))+"\n")
        ok(f"JS endpoints extracted: {len(all_endpoints)}")
    if all_absolute_urls:
        (ep_dir/"js_absolute_urls.txt").write_text("\n".join(sorted(all_absolute_urls))+"\n")
        ok(f"Absolute URLs from JS: {len(all_absolute_urls)}")
    if api_calls:
        with open(js_dir/"js_api_calls.json","w") as f: json.dump(api_calls,f,indent=2)
        ok(f"API calls cataloged: {len(api_calls)}")
    if graphql_ops:
        with open(js_dir/"graphql_operations.json","w") as f: json.dump(graphql_ops,f,indent=2)
        hit(f"GraphQL ops in JS: {len(graphql_ops)}")
    if storage_keys:
        (js_dir/"storage_keys.txt").write_text("\n".join(sorted(storage_keys))+"\n")
        ok(f"Storage keys found: {len(storage_keys)}")
    if interesting_config:
        (js_dir/"interesting_config.txt").write_text("\n".join(sorted(interesting_config))+"\n")
        ok(f"Interesting config: {len(interesting_config)}")

    # Secret scanning
    info("Scanning JS for secrets...")
    extra_dirs = [str(maps_dir/"sources")] if (maps_dir/"sources").exists() else []
    findings = scan_js_secrets(str(files_dir), secrets_dir, extra_dirs=extra_dirs)
    total_secrets = sum(len(v["matches"]) for v in findings.values())
    if total_secrets > 0:
        hit(f"SECRETS FOUND: {total_secrets} items across {len(findings)} pattern types")
    else: ok("No secrets found in JS")
    return total_secrets, len(map_found)

# ═══════════════════════════════════════════════════════════════════
# PHASE 8: GraphQL Detection
# ═══════════════════════════════════════════════════════════════════

GRAPHQL_PATHS = ["/graphql","/graphiql","/v1/graphql","/v2/graphql","/api/graphql",
    "/api/v1/graphql","/query","/gql","/graphql/console","/altair","/playground",
    "/__graphql","/graphql-explorer"]
INTROSPECTION_QUERY = '{"query":"{ __schema { types { name fields { name } } } }"}'

def phase_graphql(target, out):
    ph("PHASE 8: GRAPHQL DETECTION & INTROSPECTION")
    gql_dir = out / "graphql"; web_dir = out / "web"; ep_dir = out / "endpoints"
    gql_dir.mkdir(exist_ok=True)
    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls: live_urls = [f"https://{target}", f"http://{target}"]
    found = []
    def probe_gql(args):
        base, path = args; url = base.rstrip("/") + path
        try:
            req = urllib.request.Request(url, method="POST", data=INTROSPECTION_QUERY.encode(),
                headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read().decode("utf-8", errors="ignore")
                return (url, body, "__schema" in body) if r.status == 200 else (url, "", False) if r.status == 200 else None
        except urllib.error.HTTPError as e:
            return (url, "", False) if e.code in (400,405) else None
        except: return None
    targets = [(base, path) for base in live_urls[:15] for path in GRAPHQL_PATHS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(probe_gql, targets))
    for r in results:
        if not r: continue
        url, body, introspection = r
        found.append(url)
        if introspection:
            hit(f"GRAPHQL INTROSPECTION: {url}")
            (gql_dir / f"introspection_{hashlib.md5(url.encode()).hexdigest()[:8]}.json").write_text(body)
        else: ok(f"GraphQL endpoint (no introspection): {url}")
    if found:
        (gql_dir/"graphql_endpoints.txt").write_text("\n".join(sorted(set(found))))
        ok(f"GraphQL endpoints: {len(set(found))}")
        for schema_file in gql_dir.glob("introspection_*.json"):
            try:
                data = json.loads(schema_file.read_text())
                types = data.get("data",{}).get("__schema",{}).get("types",[])
                interesting = [t for t in types if not t["name"].startswith("__")]
                if interesting:
                    (gql_dir/"schema_types.txt").write_text("\n".join(sorted(t["name"] for t in interesting)))
                    hit(f"Schema has {len(interesting)} custom types")
                    for t in interesting:
                        nl = t["name"].lower()
                        if any(kw in nl for kw in ["user","admin","auth","token","secret","payment","credential"]):
                            fields = [f["name"] for f in (t.get("fields") or [])]
                            hit(f"  Sensitive type: {t['name']} -> {', '.join(fields[:10])}")
            except: pass
    else: ok("No GraphQL endpoints found")
    return len(set(found))

# ═══════════════════════════════════════════════════════════════════
# PHASE 9: API Fuzzing
# ═══════════════════════════════════════════════════════════════════

API_BASES = ["/api","/api/v1","/api/v2","/api/v3","/v1","/v2",
    "/rest","/api/internal","/api/admin","/api/private","/api/public",
    "/api-docs","/swagger.json","/openapi.json","/docs"]

def phase_api_fuzz(target, out):
    ph("PHASE 9: API FUZZING")
    api_dir = out / "api"; web_dir = out / "web"; api_dir.mkdir(exist_ok=True)
    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls: live_urls = [f"https://{target}"]
    found = []
    def probe_api(args):
        base, path = args
        url = base.rstrip("/") + path
        body, code = fetch_url(url, timeout=10)
        return (url, code) if code in (200,301,302,401,403) else None
    targets = [(base, path) for base in live_urls[:10] for path in API_BASES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(probe_api, targets))
    for r in results:
        if not r: continue
        url, code = r; found.append(url)
        if "swagger" in url.lower() or "openapi" in url.lower(): hit(f"SWAGGER/OPENAPI: {url}")
        elif code == 200: ok(f"API path [{code}]: {url}")
        elif code == 401: hit(f"API requires auth: {url}")
        elif code == 403: warn(f"API forbidden: {url}")
    if found:
        (api_dir/"found_api_paths.txt").write_text("\n".join(sorted(set(found))))
        ok(f"API paths: {len(set(found))}")
    if check_tool("ffuf"):
        wordlist_paths = ["/opt/SecLists/Discovery/Web-Content/api/api-endpoints.txt",
            str(WORDLIST_DIR/"api-endpoints.txt")] if WORDLIST_DIR.exists() else []
        wordlist = None
        for wl in wordlist_paths:
            if os.path.exists(wl): wordlist = wl; break
        if wordlist:
            info("ffuf API fuzzing...")
            for base in live_urls[:5]:
                safe = hashlib.md5(base.encode()).hexdigest()[:8]
                run_cmd(f"ffuf -u '{base.rstrip('/')}/api/FUZZ' -w {wordlist} -mc 200,201,301,302,401,403,405 -t 50 -sf -s -o {api_dir}/ffuf_{safe}.json -of json 2>/dev/null", timeout=180)
            ok("ffuf complete")
            for fuzz_result in api_dir.glob("ffuf_*.json"):
                try:
                    data = json.loads(fuzz_result.read_text())
                    for r in data.get("results",[]):
                        status = r.get("status",0)
                        fuzz_url = r.get("url","")
                        if status in (200,201): hit(f"API [{status}]: {fuzz_url}")
                        elif status in (401,403): warn(f"Protected [{status}]: {fuzz_url}")
                except: pass
    return len(set(found))

# ═══════════════════════════════════════════════════════════════════
# PHASE 10: Google Dork Generation
# ═══════════════════════════════════════════════════════════════════

def phase_dorks(target, out):
    ph("PHASE 10: GOOGLE DORK GENERATION")
    dorks_dir = out / "dorks"; dorks_dir.mkdir(exist_ok=True)
    dorks = f"""# BugHunter Pro — Google Dorks for: {target}
# ===== SENSITIVE FILES =====
site:{target} ext:env | ext:log | ext:conf | ext:sql | ext:db | ext:zip | ext:bak
site:{target} ext:pem | ext:key | ext:crt | ext:pfx | ext:p12
site:{target} filetype:log "error" | "password" | "token" | "exception"
site:{target} "index of" "/.git" | "/backup" | "/config" | "/private" | "/admin"
site:{target} ext:php.bak | ext:asp.bak | ext:yml.bak | ext:xml
site:{target} "DB_PASSWORD" | "SECRET_KEY" | "DATABASE_URL" | "MYSQL_ROOT_PASSWORD"
site:{target} intitle:"index of" intext:".env"
# ===== ADMIN PANELS =====
site:{target} inurl:admin | inurl:login | inurl:wp-admin | inurl:dashboard | inurl:panel
site:{target} inurl:jenkins | inurl:grafana | inurl:kibana | inurl:jira | inurl:gitlab
site:{target} inurl:phpmyadmin | inurl:adminer | inurl:cpanel | inurl:webmail
# ===== API & DOCS =====
site:{target} inurl:api | inurl:swagger | inurl:api-docs | inurl:graphql
site:{target} inurl:webhook | inurl:callback | filetype:json "swagger" | "openapi"
# ===== OPEN REDIRECT & SSRF =====
site:{target} inurl:url= | inurl:return= | inurl:redirect= | inurl:next=
site:{target} inurl:proxy= | inurl:load= | inurl:file= | inurl:path=
# ===== CLOUD =====
site:{target} "s3.amazonaws.com" | "storage.googleapis.com" | "blob.core.windows.net"
"{target}" site:github.com | site:gitlab.com | site:bitbucket.org
"{target}" site:pastebin.com | site:gist.github.com
# ===== GITHUB DORKS =====
org:{target.split('.')[0]} password
org:{target.split('.')[0]} api_key OR apikey OR api_secret
org:{target.split('.')[0]} "BEGIN RSA PRIVATE KEY"
org:{target.split('.')[0]} ".env"
org:{target.split('.')[0]} "AKIA" aws
org:{target.split('.')[0]} filename:.env
org:{target.split('.')[0]} filename:config.json password
"""
    (dorks_dir/"google_dorks.txt").write_text(dorks)
    ok("Google dorks saved to dorks/google_dorks.txt")

# ═══════════════════════════════════════════════════════════════════
# PHASE 11: Vulnerability Scanning
# ═══════════════════════════════════════════════════════════════════

def phase_vulns(target, out):
    ph("PHASE 11: VULNERABILITY SCANNING")
    vulns_dir = out / "vulns"; web_dir = out / "web"; dns_dir = out / "dns"
    vulns_dir.mkdir(exist_ok=True)
    if check_tool("nuclei"):
        info("Updating nuclei templates...")
        run_cmd("nuclei -update-templates -silent", timeout=120)
        live_urls = web_dir / "live_urls.txt"
        if not live_urls.exists() or count_lines(live_urls) == 0:
            live_urls.write_text(f"https://{target}\nhttp://{target}\nhttps://www.{target}\n")
        scans = [
            ("CVEs (high/critical)", f"nuclei -l {live_urls} -tags cve -severity high,critical -silent -o {vulns_dir}/nuclei_cve.txt"),
            ("Exposed panels", f"nuclei -l {live_urls} -tags exposed-panels -silent -o {vulns_dir}/nuclei_panels.txt"),
            ("Default credentials", f"nuclei -l {live_urls} -tags default-logins -silent -o {vulns_dir}/nuclei_default_creds.txt"),
            ("Misconfigurations", f"nuclei -l {live_urls} -tags misconfig -silent -o {vulns_dir}/nuclei_misconfig.txt"),
            ("Exposed files", f"nuclei -l {live_urls} -tags exposure -silent -o {vulns_dir}/nuclei_exposure.txt"),
            ("CORS misconfig", f"nuclei -l {live_urls} -tags cors -silent -o {vulns_dir}/nuclei_cors.txt"),
        ]
        for name, cmd in scans:
            info(f"nuclei — {name}...")
            run_cmd(cmd, timeout=300)
        for name, cmd in scans:
            fname = cmd.split("-o ")[1].split()[0]
            fpath = Path(fname)
            if fpath.exists():
                c = count_lines(fpath)
                if c > 0: hit(f"nuclei [{name}]: {c} findings")
                else: ok(f"nuclei [{name}]: 0 findings")
    if check_tool("subzy"):
        info("subzy takeover detection...")
        resolved = dns_dir / "resolved.txt"
        if resolved.exists():
            run_cmd(f"subzy run --targets {resolved} --concurrency 100 --hide_fails > {vulns_dir}/subzy_results.txt", timeout=300)

    # 403 bypass
    info("Testing 403 bypass techniques...")
    for url in read_lines(web_dir / "403_hosts.txt")[:20]:
        for bypass in ["/%2f/", "/./", "//", "/.;/", "/%20/"]:
            body, code = fetch_url(url.rstrip("/") + bypass)
            if code == 200:
                hit(f"403 BYPASS: {url}{bypass}")
                append_file(str(vulns_dir/"403_bypasses.txt"), f"{url}{bypass}")
        for header, val in [("X-Original-URL","/"),("X-Rewrite-URL","/"),
            ("X-Custom-IP-Authorization","127.0.0.1"),("X-Forwarded-For","127.0.0.1")]:
            body, code = fetch_url(url, headers={header: val, "User-Agent":"Mozilla/5.0"})
            if code == 200:
                hit(f"403 BYPASS (header {header}): {url}")
                append_file(str(vulns_dir/"403_bypasses.txt"), f"[{header}] {url}")

    # CORS testing
    info("Testing CORS misconfigurations...")
    for url in read_lines(web_dir/"live_urls.txt")[:30]:
        for origin in [f"https://evil.com", "null"]:
            try:
                req = urllib.request.Request(url, headers={"Origin":origin,"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=8)
                acao = resp.headers.get("Access-Control-Allow-Origin","")
                acac = resp.headers.get("Access-Control-Allow-Credentials","")
                if acao == origin or (acao == "*" and acac.lower() == "true"):
                    hit(f"CORS MISCONFIG: {url} origin={origin}")
                    append_file(str(vulns_dir/"cors_misconfig.txt"), f"{url} | Origin: {origin} | ACAO: {acao}")
            except: pass

    # Open redirect validation
    info("Testing open redirects...")
    params_dir = out / "params"
    for url in read_lines(params_dir/"redirect_prone.txt")[:50]:
        try:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for key in params:
                test_params = params.copy()
                test_params[key] = ["https://evil.com/redirect-test"]
                test_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(test_params, doseq=True)))
                req = urllib.request.Request(test_url, headers={"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=8)
                if "evil.com" in resp.geturl():
                    hit(f"OPEN REDIRECT: {url} via param '{key}'")
                    append_file(str(vulns_dir/"open_redirects.txt"), f"{url} | param: {key}")
        except: pass

    # Host header injection
    info("Testing host header injection...")
    for url in read_lines(web_dir/"live_urls.txt")[:15]:
        for evil_host in [f"evil.com", f"{target}.evil.com", "localhost"]:
            try:
                req = urllib.request.Request(url, headers={"Host":evil_host,"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=8)
                body = resp.read(4096).decode("utf-8", errors="ignore")
                if evil_host in body:
                    hit(f"HOST HEADER INJECTION: {url} Host: {evil_host}")
                    append_file(str(vulns_dir/"host_header_injection.txt"), f"{url} | Host: {evil_host}")
                    break
            except: pass

    # dalfox XSS
    if check_tool("dalfox"):
        info("dalfox XSS scanning...")
        xss_input = vulns_dir/"dalfox_targets.txt"
        run_cmd(f"cat {params_dir}/injection_prone.txt {params_dir}/ssrf_prone.txt 2>/dev/null | sort -u | head -200 > {xss_input}")
        if count_lines(xss_input) > 0:
            run_cmd(f"dalfox file {xss_input} --silence --no-color --skip-bav --output {vulns_dir}/dalfox_xss.txt", timeout=600)
            xc = count_lines(vulns_dir/"dalfox_xss.txt")
            if xc > 0: hit(f"dalfox XSS: {xc} findings!")
            else: ok("dalfox: no XSS found")

# ═══════════════════════════════════════════════════════════════════
# PHASE 12: Cloud Asset Discovery
# ═══════════════════════════════════════════════════════════════════

def phase_cloud(target, out):
    ph("PHASE 12: CLOUD ASSET DISCOVERY")
    secrets_dir = out / "secrets"; secrets_dir.mkdir(exist_ok=True)
    base = target.split(".")[0]
    buckets = [target, target.replace(".","-"), base,
        f"{base}-dev", f"{base}-prod", f"{base}-staging", f"{base}-backup",
        f"{base}-data", f"{base}-assets", f"{base}-static", f"{base}-uploads",
        f"{base}-files", f"{base}-media", f"{base}-logs", f"{base}-archive",
        f"{base}-test", f"{base}-www", f"{base}-web",
        f"www.{target}", f"cdn.{target}", f"static.{target}"]
    info(f"Checking {len(buckets)} S3 bucket permutations...")
    for bucket in buckets:
        body, code = fetch_url(f"https://{bucket}.s3.amazonaws.com/", timeout=8)
        if code in (200,301) and "<ListBucketResult" in body:
            hit(f"OPEN S3 BUCKET: {bucket}.s3.amazonaws.com")
            append_file(str(secrets_dir/"open_s3_buckets.txt"), bucket)
        elif code == 403: ok(f"S3 private: {bucket}")
    info("Checking Firebase...")
    for fb_name in [base, f"{base}-default", f"{target.replace('.','-')}"]:
        body, code = fetch_url(f"https://{fb_name}-default-rtdb.firebaseio.com/.json", timeout=8)
        if code == 200 and body not in ("null",""):
            hit(f"OPEN FIREBASE DB: {fb_name}")
            (secrets_dir/f"firebase_{fb_name}.json").write_text(body)
    info("Checking GCP Storage...")
    for bucket in buckets[:10]:
        body, code = fetch_url(f"https://storage.googleapis.com/{bucket}/", timeout=8)
        if code == 200 and "<ListBucketResult" in body:
            hit(f"OPEN GCP BUCKET: {bucket}")
            append_file(str(secrets_dir/"open_gcp_buckets.txt"), bucket)

# ═══════════════════════════════════════════════════════════════════
# PHASE 13: GitHub Secret Scanning
# ═══════════════════════════════════════════════════════════════════

def phase_github(target, out):
    ph("PHASE 13: GITHUB SECRET SCANNING")
    secrets_dir = out / "secrets"; dorks_dir = out / "dorks"
    secrets_dir.mkdir(exist_ok=True); dorks_dir.mkdir(exist_ok=True)
    org = target.split(".")[0]
    if check_tool("trufflehog"):
        info(f"TruffleHog scanning GitHub org: {org}...")
        run_cmd(f"trufflehog github --org={org} --only-verified 2>/dev/null > {secrets_dir}/trufflehog_github.txt", timeout=300)
        c = count_lines(secrets_dir/"trufflehog_github.txt")
        if c > 0: hit(f"TruffleHog: {c} verified secrets!")
        else: ok("TruffleHog: no verified secrets")
    if check_tool("gitleaks"):
        info("gitleaks scan...")
        run_cmd(f"gitleaks detect --source {out} --report-format json -r {secrets_dir}/gitleaks.json 2>/dev/null")

# ═══════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════

def generate_report(target, out, stats):
    ph("GENERATING FINAL REPORT")
    vulns_dir = out / "vulns"; js_dir = out / "js"; secrets_dir = out / "secrets"
    params_dir = out / "params"; gql_dir = out / "graphql"; api_dir = out / "api"
    def cat(path, lines=30):
        try:
            content = Path(path).read_text().strip()
            return "\n".join(content.split("\n")[:lines]) if content else "None"
        except: return "None"
    report = f"""# BugHunter Pro Report — {target}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Recon Statistics
| Phase | Count |
|-------|-------|
| Passive Subdomains | {stats.get('passive_subs',0)} |
| Resolved Subdomains | {stats.get('resolved',0)} |
| Live Web Hosts | {stats.get('live',0)} |
| Total URLs | {stats.get('total_urls',0)} |
| Secrets Found | {stats.get('secrets',0)} |
| Source Maps Found | {stats.get('source_maps',0)} |
| GraphQL Endpoints | {stats.get('graphql_eps',0)} |
| API Paths | {stats.get('api_paths',0)} |
## HIGH PRIORITY FINDINGS
### Exposed Admin Panels
```\n{cat(vulns_dir/'nuclei_panels.txt')}\n```
### High/Critical CVEs
```\n{cat(vulns_dir/'nuclei_cve.txt')}\n```
### Secrets in JavaScript
```\n{cat(secrets_dir/'js_findings_per_file.txt',40)}\n```
### Source Maps Found
```\n{cat(js_dir/'source_maps_found.txt')}\n```
### Open S3 Buckets
```\n{cat(secrets_dir/'open_s3_buckets.txt')}\n```
### CORS Misconfigurations
```\n{cat(vulns_dir/'cors_misconfig.txt')}\n```
### Open Redirects
```\n{cat(vulns_dir/'open_redirects.txt')}\n```
### CRLF Injection
```\n{cat(vulns_dir/'crlf_injection.txt')}\n```
### 403 Bypasses
```\n{cat(vulns_dir/'403_bypasses.txt')}\n```
### SSRF-Prone Parameters
```\n{cat(params_dir/'ssrf_prone.txt',20)}\n```
### XSS-Prone Parameters
```\n{cat(params_dir/'xss_prone.txt',20)}\n```
"""
    report_path = out / "HUNT_REPORT.md"
    report_path.write_text(report)
    ok(f"Report saved: {report_path}")

# ═══════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

PHASE_ALIASES = {
    "subs": 1, "passive": 1, "dns": 2, "resolve": 2, "http": 3, "web": 3,
    "ports": 4, "port": 4, "content": 5, "crawl": 5, "params": 6, "parameters": 6,
    "js": 7, "javascript": 7, "graphql": 8, "gql": 8, "api": 9, "fuzz": 9,
    "dorks": 10, "vulns": 11, "vulnerability": 11, "cloud": 12, "aws": 12,
    "github": 13, "gh": 13,
}

def resolve_phase(phase_input):
    if phase_input is None: return None
    if isinstance(phase_input, int) or phase_input.isdigit():
        return int(phase_input)
    return PHASE_ALIASES.get(phase_input.lower())

def main():
    parser = argparse.ArgumentParser(description="BugHunter Pro — 13-Phase Pipeline")
    parser.add_argument("--target", help="Target domain")
    parser.add_argument("--phase", help="Phase number (1-13) or name (js, vulns, api, etc.)")
    parser.add_argument("--deep", action="store_true", help="Run all 13 phases")
    parser.add_argument("--quick", action="store_true", help="Quick scan (phases 1-5 only)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI analysis")
    parser.add_argument("--check-tools", action="store_true", help="Check installed tools")
    parser.add_argument("--cookie", help="Session cookie for authenticated scanning")
    args = parser.parse_args()

    print_banner()

    print_tool_status()

    if args.check_tools:
        check_tools_installed()
        return 0

    target = args.target
    if not target:
        err("No target specified. Use --target <domain>")
        parser.print_help()
        return 1

    target_type = detect_target_type(target)
    info(f"Target: {target} (type: {target_type})")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = target.replace("/", "_").replace(":", "_")
    out = RECON_DIR / f"hunt_{safe_target}_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    info(f"Output: {out}/")

    phase_input = resolve_phase(args.phase) if args.phase else None
    is_deep = args.deep or phase_input == "full"
    is_quick = args.quick

    # Determine which phases to run
    if phase_input and phase_input != "full":
        phases_to_run = [phase_input] if isinstance(phase_input, int) else [int(phase_input)]
    elif is_deep:
        phases_to_run = list(range(1, 14))
    elif is_quick:
        phases_to_run = list(range(1, 6))
    else:
        phases_to_run = list(range(1, 8))

    stats = {}

    for p in phases_to_run:
        try:
            if p == 1: stats['passive_subs'] = phase_passive_subs(target, out)
            elif p == 2: stats['resolved'] = phase_dns(target, out)
            elif p == 3: stats['live'] = phase_http(target, out)
            elif p == 4: phase_ports(target, out)
            elif p == 5: stats['total_urls'] = phase_content(target, out, args.cookie)
            elif p == 6: phase_params(target, out)
            elif p == 7: stats['secrets'], stats['source_maps'] = phase_js(target, out)
            elif p == 8: stats['graphql_eps'] = phase_graphql(target, out)
            elif p == 9: stats['api_paths'] = phase_api_fuzz(target, out)
            elif p == 10: phase_dorks(target, out)
            elif p == 11: phase_vulns(target, out)
            elif p == 12: phase_cloud(target, out)
            elif p == 13: phase_github(target, out)
            ok(f"Phase {p} complete.")
        except Exception as e:
            err(f"Phase {p} failed: {e}")
            import traceback; traceback.print_exc()

    generate_report(target, out, stats)
    hit(f"BugHunter Pro complete! Output: {out}/")
    hit(f"Report: {out/'HUNT_REPORT.md'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
