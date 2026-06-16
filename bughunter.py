#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║             BugHunter Pro — Real Recon CLI Tool              ║
║                   Made By KJI                                ║
║      Usage: python3 bughunter.py <domain> [options]          ║
║             python3 bughunter.py --scope scope.txt           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, json, re, time, shutil, argparse, hashlib, socket, shlex, math, signal
import urllib.request, urllib.error, urllib.parse
import concurrent.futures
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Color codes ──────────────────────────────────────────────
R  = "\033[0;31m"
G  = "\033[0;32m"
Y  = "\033[1;33m"
C  = "\033[0;36m"
P  = "\033[0;35m"
B  = "\033[0;34m"
W  = "\033[1;37m"
DIM= "\033[2m"
NC = "\033[0m"
BOLD="\033[1m"

def banner():
    print(f"""{C}
██████╗ ██╗   ██╗ ██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
██╔══██╗██║   ██║██╔════╝ ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██████╔╝██║   ██║██║  ███╗███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██╗██║   ██║██║   ██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{NC}{DIM}  Pro v4.0 · Real Recon · MADE BY KJI         {NC}
""")

def ph(msg):   print(f"\n{C}{BOLD}[+]══════ {msg} ══════{NC}")
def ok(msg):   print(f"{G}[✓]{NC} {msg}")
def info(msg): print(f"{Y}[~]{NC} {msg}")
def warn(msg): print(f"{Y}[!]{NC} {msg}")
def hit(msg):  print(f"{P}{BOLD}[★ HIT]{NC} {msg}")
def err(msg):  print(f"{R}[✗]{NC} {msg}")
def die(msg):  print(f"{R}[FATAL]{NC} {msg}"); sys.exit(1)

def run(cmd, timeout=300, capture=True):
    """Run a shell command, return (stdout, returncode)."""
    if timeout >= 120:
        info(f"Running external command (timeout {timeout}s): {cmd[:140]}")
    try:
        kwargs = {}
        if os.name != "nt":
            kwargs["start_new_session"] = True
        p = subprocess.Popen(
            cmd, shell=True, text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.DEVNULL,
            **kwargs
        )
        stdout, _ = p.communicate(timeout=timeout)
        if p.returncode != 0:
            warn(f"Command failed ({p.returncode}): {cmd[:140]}")
        return stdout.strip() if capture and stdout else "", p.returncode
    except subprocess.TimeoutExpired:
        try:
            if os.name != "nt":
                os.killpg(p.pid, signal.SIGTERM)
            else:
                p.kill()
            p.communicate(timeout=5)
        except Exception:
            try:
                if os.name != "nt":
                    os.killpg(p.pid, signal.SIGKILL)
                else:
                    p.kill()
            except Exception:
                pass
        warn(f"Command timed out after {timeout}s: {cmd[:140]}")
        return "", 1
    except Exception as e:
        warn(f"Command error: {e}")
        return "", 1

def check_tool(name):
    return shutil.which(name) is not None

def count_lines(path):
    try:
        with open(path) as f:
            return sum(1 for l in f if l.strip())
    except:
        return 0

def append_file(path, content):
    with open(path, "a") as f:
        f.write(content + "\n")

def read_lines(path):
    try:
        with open(path) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return []

def fetch_url(url, timeout=10, headers=None):
    """Simple HTTP GET, returns (body, status_code)."""
    try:
        req = urllib.request.Request(url, headers=headers or {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore"), r.status
    except urllib.error.HTTPError as e:
        return "", e.code
    except:
        return "", 0

# ─────────────────────────────────────────────────────────────
# TOOL CHECKER
# ─────────────────────────────────────────────────────────────
REQUIRED_TOOLS = [
    "subfinder", "assetfinder", "httpx", "nuclei", "naabu",
    "dnsx", "katana", "gau", "waybackurls", "getJS",
    "puredns", "subzy", "ffuf", "arjun", "trufflehog",
    "jsluice", "unfurl", "amass", "altdns", "jq"
]

OPTIONAL_TOOLS = ["masscan", "nmap", "feroxbuster", "wafw00f", "sqlmap", "dalfox", "aquatone", "gowitness"]

def check_tools():
    ph("TOOL VERIFICATION")
    missing = []
    for t in REQUIRED_TOOLS:
        if check_tool(t):
            ok(t)
        else:
            warn(f"MISSING (required): {t}")
            missing.append(t)
    for t in OPTIONAL_TOOLS:
        if check_tool(t):
            ok(f"{t} {DIM}(optional){NC}")
        else:
            info(f"missing (optional): {t}")
    if missing:
        warn(f"{len(missing)} required tools missing. Run: python3 bughunter.py --install")
    return missing

# ─────────────────────────────────────────────────────────────
# PHASE 1 — PASSIVE SUBDOMAIN ENUM
# ─────────────────────────────────────────────────────────────
def phase_passive_subs(target, out):
    ph("PHASE 1: PASSIVE SUBDOMAIN ENUMERATION")
    subs_dir = out / "subdomains"
    subs_dir.mkdir(exist_ok=True)

    # subfinder
    if check_tool("subfinder"):
        info("subfinder (all sources, recursive)...")
        run(f"subfinder -d {target} -all -recursive -silent -o {subs_dir}/subfinder.txt")
        ok(f"subfinder: {count_lines(subs_dir/'subfinder.txt')} subdomains")
    else:
        warn("subfinder not found, skipping")

    # assetfinder
    if check_tool("assetfinder"):
        info("assetfinder...")
        run(f"assetfinder --subs-only {target} > {subs_dir}/assetfinder.txt")
        ok(f"assetfinder: {count_lines(subs_dir/'assetfinder.txt')} subdomains")

    # amass passive
    if check_tool("amass"):
        info("amass passive (this may take a few minutes)...")
        run(f"amass enum -passive -d {target} -o {subs_dir}/amass.txt", timeout=300)
        ok(f"amass: {count_lines(subs_dir/'amass.txt')} subdomains")

    # crt.sh
    info("crt.sh certificate transparency...")
    try:
        body, code = fetch_url(f"https://crt.sh/?q=%.{target}&output=json")
        if code == 200 and body:
            import json as _json
            entries = _json.loads(body)
            names = set()
            for e in entries:
                for name in e.get("name_value", "").split("\n"):
                    name = name.strip().lstrip("*.")
                    if name.endswith(target):
                        names.add(name)
            with open(subs_dir / "crt.txt", "w") as f:
                f.write("\n".join(sorted(names)))
            ok(f"crt.sh: {len(names)} subdomains")
    except Exception as e:
        warn(f"crt.sh failed: {e}")

    # gau + waybackurls
    if check_tool("gau"):
        info("gau wayback harvest...")
        run(f"gau --subs {target} 2>/dev/null | grep -oP '(?:https?://)[a-zA-Z0-9._-]+\\.{re.escape(target)}' | sed 's|https\\?://||' | sort -u > {subs_dir}/gau_subs.txt")
        ok(f"gau: {count_lines(subs_dir/'gau_subs.txt')} subdomains")

    if check_tool("waybackurls"):
        info("waybackurls harvest...")
        run(f"waybackurls {target} 2>/dev/null | grep -oP '(?:https?://)[a-zA-Z0-9._-]+\\.{re.escape(target)}' | sed 's|https\\?://||' | sort -u > {subs_dir}/wayback_subs.txt")

    # GitHub subdomains
    if check_tool("github-subdomains"):
        info("github-subdomains (set GITHUB_TOKEN env var for best results)...")
        token = os.environ.get("GITHUB_TOKEN", "")
        flag = f"-t {token}" if token else ""
        run(f"github-subdomains -d {target} {flag} -o {subs_dir}/github_subs.txt")

    # Merge all
    info("Merging and deduplicating...")
    run(f"cat {subs_dir}/*.txt 2>/dev/null | grep -E '^[a-zA-Z0-9._-]+$' | grep -E '\\.{re.escape(target)}$|^{re.escape(target)}$' | sort -u > {subs_dir}/all_passive.txt")
    total = count_lines(subs_dir / "all_passive.txt")
    ok(f"Total passive unique subdomains: {total}")
    return total

# ─────────────────────────────────────────────────────────────
# PHASE 2 — ACTIVE DNS + PERMUTATIONS
# ─────────────────────────────────────────────────────────────
def phase_dns(target, out):
    ph("PHASE 2: DNS RESOLUTION + ACTIVE BRUTING")
    dns_dir  = out / "dns"
    subs_dir = out / "subdomains"
    dns_dir.mkdir(exist_ok=True)

    # Download resolvers
    info("Downloading fresh DNS resolvers...")
    resolvers = dns_dir / "resolvers.txt"
    try:
        body, _ = fetch_url("https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt")
        if body:
            resolvers.write_text(body)
            ok(f"Resolvers: {count_lines(resolvers)}")
    except:
        resolvers.write_text("8.8.8.8\n1.1.1.1\n9.9.9.9\n8.8.4.4\n")

    # puredns bruteforce
    if check_tool("puredns"):
        wordlist = "/opt/SecLists/Discovery/DNS/dns-Jhaddix.txt"
        if os.path.exists(wordlist):
            info("puredns bruteforce (dns-Jhaddix.txt)...")
            run(f"puredns bruteforce {wordlist} {target} -r {resolvers} -o {subs_dir}/puredns_brute.txt", timeout=600)
            ok(f"puredns brute: {count_lines(subs_dir/'puredns_brute.txt')} new")
        else:
            warn(f"Wordlist not found: {wordlist} — install SecLists")

    # Combine all subs for permutations
    run(f"cat {subs_dir}/*.txt 2>/dev/null | sort -u > {subs_dir}/combined.txt")

    # altdns permutations
    if check_tool("altdns"):
        perm_words = "/opt/SecLists/Discovery/DNS/altdns_words.txt"
        if os.path.exists(perm_words):
            info("altdns permutations...")
            run(f"altdns -i {subs_dir}/combined.txt -o {subs_dir}/altdns_perms.txt -w {perm_words}", timeout=300)
            ok(f"altdns perms: {count_lines(subs_dir/'altdns_perms.txt')}")

    # gotator
    if check_tool("gotator"):
        info("gotator permutations...")
        run(f"gotator -sub {subs_dir}/combined.txt -depth 1 -numbers 3 2>/dev/null >> {subs_dir}/altdns_perms.txt", timeout=120)

    # Resolve everything
    info("Resolving all candidates with puredns...")
    run(f"cat {subs_dir}/combined.txt {subs_dir}/altdns_perms.txt 2>/dev/null | sort -u | puredns resolve -r {resolvers} -o {dns_dir}/resolved.txt 2>/dev/null || dnsx -l {subs_dir}/combined.txt -silent -o {dns_dir}/resolved.txt", timeout=600)
    ok(f"Resolved: {count_lines(dns_dir/'resolved.txt')} live subdomains")

    # Detailed DNS records
    if check_tool("dnsx"):
        info("Collecting DNS records (A, AAAA, CNAME, MX)...")
        run(f"dnsx -l {dns_dir}/resolved.txt -a -aaaa -cname -mx -resp -silent -o {dns_dir}/dns_details.txt", timeout=300)
        ok(f"DNS records: {count_lines(dns_dir/'dns_details.txt')}")

        # ── CNAME Takeover Detection ──
        info("Checking CNAMEs for dangling/takeover candidates...")
        cname_out, _ = run(f"dnsx -l {dns_dir}/resolved.txt -cname -resp -silent", timeout=120)
        dangling_services = [
            "amazonaws.com", "heroku", "github.io", "shopify",
            "fastly", "pantheon.io", "zendesk.com", "readme.io",
            "ghost.io", "helpscout", "statuspage.io", "surge.sh",
            "bitbucket.io", "netlify", "wordpress.com", "smugmug",
            "cargo.site", "feedpress", "freshdesk", "helpjuice",
            "youtrack", "unbouncepages", "launchrock", "tave.com",
            "wishpond", "aftership", "aha.io", "brightcove",
            "bigcartel", "campaignmonitor", "acquia-test",
            "proposify", "simplebooklet", "getresponse",
            "vend-web", "myjetbrains.com", "azure",
        ]
        if cname_out:
            takeover_dir = out / "vulns"
            takeover_dir.mkdir(exist_ok=True)
            for line in cname_out.split("\n"):
                line = line.strip()
                for svc in dangling_services:
                    if svc in line.lower():
                        hit(f"POTENTIAL CNAME TAKEOVER: {line}")
                        append_file(str(takeover_dir / "cname_takeovers.txt"), line)

    return count_lines(dns_dir / "resolved.txt")

# ─────────────────────────────────────────────────────────────
# PHASE 3 — HTTP PROBING + FINGERPRINTING
# ─────────────────────────────────────────────────────────────
def phase_http(target, out):
    ph("PHASE 3: HTTP PROBING + TECH FINGERPRINTING")
    web_dir = out / "web"
    dns_dir = out / "dns"
    web_dir.mkdir(exist_ok=True)

    if not check_tool("httpx"):
        warn("httpx not found, skipping HTTP probing")
        return 0

    # Fallback — if DNS resolution yielded nothing, probe target directly
    resolved = dns_dir / "resolved.txt"
    if not resolved.exists() or count_lines(resolved) == 0:
        warn("No resolved subdomains — probing target domain directly")
        tmp_targets = web_dir / "httpx_targets.txt"
        tmp_targets.write_text(f"{target}\nwww.{target}\n")
        probe_input = str(tmp_targets)
    else:
        probe_input = str(resolved)

    info("httpx — probing all resolved subdomains...")
    run(f"""httpx -l {probe_input} \
        -tech-detect -status-code -title -web-server -ip -cdn \
        -screenshot \
        -silent -o {web_dir}/httpx_full.txt""", timeout=600)
    ok(f"Live hosts: {count_lines(web_dir/'httpx_full.txt')}")

    # Extract live URLs
    run(f"cat {web_dir}/httpx_full.txt | grep -oP 'https?://[^\\s]+' | sort -u > {web_dir}/live_urls.txt")

    # Extract 403 hosts (bypass candidates)
    run(f"cat {web_dir}/httpx_full.txt | grep '\\[403\\]' | grep -oP 'https?://[^\\s]+' > {web_dir}/403_hosts.txt")
    fours = count_lines(web_dir / "403_hosts.txt")
    if fours > 0:
        warn(f"403 hosts found (test bypass): {fours} — check web/403_hosts.txt")

    # WAF detection
    if check_tool("wafw00f"):
        info("WAF detection on live hosts...")
        urls = read_lines(web_dir / "live_urls.txt")[:20]
        for url in urls:
            run(f"wafw00f {url} -o {web_dir}/waf_{hashlib.md5(url.encode()).hexdigest()[:8]}.txt 2>/dev/null &")

    live = count_lines(web_dir / "live_urls.txt")
    ok(f"Live URLs: {live}")

    # ── Visual Recon — Screenshots ──
    screenshots_dir = out / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    live_file = web_dir / "live_urls.txt"

    # gowitness (preferred — modern, fast, generates HTML gallery)
    if check_tool("gowitness"):
        info("gowitness — screenshotting all live hosts...")
        run(f"gowitness scan file -f {live_file} --screenshot-path {screenshots_dir} --write-db=false", timeout=600)
        screenshots = len(list(screenshots_dir.glob("*.png")))
        ok(f"gowitness screenshots: {screenshots}")
        if screenshots > 0:
            hit("Check screenshots/ folder for visual recon gallery")

    # aquatone (classic — HTML report with categorization)
    elif check_tool("aquatone"):
        info("aquatone — screenshotting all live hosts...")
        run(f"cat {live_file} | aquatone -out {screenshots_dir}/aquatone -silent -threads 5", timeout=600)
        if (screenshots_dir / "aquatone" / "aquatone_report.html").exists():
            ok("aquatone report generated")
            hit("Open screenshots/aquatone/aquatone_report.html in browser for visual overview")
        else:
            ok("aquatone complete")
    else:
        info("Install gowitness or aquatone for visual recon screenshots")

    return live

# ─────────────────────────────────────────────────────────────
# PHASE 4 — PORT SCANNING
# ─────────────────────────────────────────────────────────────
def phase_ports(target, out):
    ph("PHASE 4: PORT SCANNING")
    ips_dir = out / "ips"
    dns_dir = out / "dns"
    ips_dir.mkdir(exist_ok=True)

    # Extract IPs
    run(f"cat {dns_dir}/dns_details.txt 2>/dev/null | grep -oP '\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}' | sort -u > {ips_dir}/all_ips.txt")
    ip_count = count_lines(ips_dir / "all_ips.txt")

    if ip_count == 0:
        # Fallback: resolve the target domain itself
        info("No IPs from DNS details — resolving target domain directly...")
        ip_out, _ = run(f"dig +short {shlex.quote(target)} A 2>/dev/null || host {shlex.quote(target)} 2>/dev/null | grep -oP '\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}\\.\\d{{1,3}}'")
        if ip_out:
            ips = sorted(set(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_out)))
            if ips:
                (ips_dir / "all_ips.txt").write_text("\n".join(ips) + "\n")
                ip_count = len(ips)
                ok(f"Resolved {ip_count} IP(s) for {target}")

    if ip_count == 0:
        warn("No IPs found, skipping port scan")
        return

    info(f"Scanning {ip_count} IPs...")

    # naabu on high-value ports
    critical_ports = "80,443,8080,8443,8888,9200,9300,6379,27017,5432,3306,5601,4848,7001,9090,3000,8008,8161,50000,9000,4443,7443,9443,8090,8060,3389,5985,5986,22"
    if check_tool("naabu"):
        run(f"naabu -l {ips_dir}/all_ips.txt -p {critical_ports} -silent -o {ips_dir}/open_ports.txt", timeout=300)
        ok(f"Open ports: {count_lines(ips_dir/'open_ports.txt')}")

        # Flag dangerous services
        ports_content = ""
        try:
            ports_content = (ips_dir / "open_ports.txt").read_text()
        except: pass

        dangerous = {
            "9200": "ELASTICSEARCH (likely no-auth!)",
            "9300": "ELASTICSEARCH CLUSTER",
            "6379": "REDIS (likely no-auth!)",
            "27017": "MONGODB (likely no-auth!)",
            "5601": "KIBANA DASHBOARD",
            "4848":  "GLASSFISH ADMIN",
            "7001":  "WEBLOGIC (check CVE-2020-14882)",
        }
        for port, svc in dangerous.items():
            if f":{port}" in ports_content:
                hit(f"{svc} — port {port} open!")

    # nmap service detection on interesting ports
    if check_tool("nmap") and ip_count <= 50:
        info("nmap service detection on critical ports...")
        run(f"nmap -sV -sC -p 9200,6379,27017,5601,8080,8443,4848,7001 -iL {ips_dir}/all_ips.txt -oA {ips_dir}/nmap_services --open", timeout=300)

# ─────────────────────────────────────────────────────────────
# PHASE 5 — CONTENT DISCOVERY
# ─────────────────────────────────────────────────────────────
def phase_content(target, out, session_cookie=None):
    ph("PHASE 5: CONTENT DISCOVERY")
    ep_dir  = out / "endpoints"
    web_dir = out / "web"
    ep_dir.mkdir(exist_ok=True)

    cookie_flag = f"-H 'Cookie: {session_cookie}'" if session_cookie else ""
    live_urls = read_lines(web_dir / "live_urls.txt")

    # Fallback targets when no live hosts were discovered
    if live_urls:
        crawl_targets = live_urls[:20]
    else:
        crawl_targets = [f"https://{target}", f"http://{target}"]

    # katana crawl
    if check_tool("katana"):
        info("katana JS-aware crawl (unauthenticated)...")
        for url in crawl_targets:
            run(f"katana -u '{url}' -jc -d 5 -aff -ef css,png,svg,ico,woff,woff2,ttf -silent >> {ep_dir}/katana_unauth.txt", timeout=180)
        run(f"sort -u {ep_dir}/katana_unauth.txt -o {ep_dir}/katana_unauth.txt")
        ok(f"katana unauth: {count_lines(ep_dir/'katana_unauth.txt')} URLs")

        if session_cookie:
            info("katana authenticated crawl...")
            for url in crawl_targets:
                run(f"katana -u '{url}' -jc -d 5 -H 'Cookie: {session_cookie}' -silent >> {ep_dir}/katana_auth.txt", timeout=180)
            ok(f"katana auth: {count_lines(ep_dir/'katana_auth.txt')} URLs")

    # gau + waybackurls
    if check_tool("gau"):
        info("gau historical URL harvest...")
        run(f"gau {target} --subs 2>/dev/null | sort -u > {ep_dir}/gau_urls.txt", timeout=300)
        ok(f"gau historical: {count_lines(ep_dir/'gau_urls.txt')} URLs")

    if check_tool("waybackurls"):
        info("waybackurls harvest...")
        run(f"waybackurls {target} 2>/dev/null | sort -u >> {ep_dir}/gau_urls.txt", timeout=180)

    # hakrawler
    if check_tool("hakrawler"):
        info("hakrawler...")
        for url in crawl_targets[:10]:
            run(f"echo '{url}' | hakrawler -d 3 -js -subs 2>/dev/null >> {ep_dir}/hakrawler.txt", timeout=60)

    # feroxbuster directory fuzzing
    if check_tool("feroxbuster"):
        wordlist = "/opt/SecLists/Discovery/Web-Content/raft-large-words.txt"
        if os.path.exists(wordlist) and crawl_targets:
            info(f"feroxbuster dir fuzzing on top 3 targets...")
            for url in crawl_targets[:3]:
                safe = hashlib.md5(url.encode()).hexdigest()[:8]
                run(f"feroxbuster -u '{url}' -w {wordlist} -x php,asp,aspx,jsp,json,txt,bak,old,zip,env,config -r -s 200,301,302,403 -q --no-state -o {ep_dir}/ferox_{safe}.txt", timeout=300)
            ok("feroxbuster complete")

    # kiterunner API routes
    if check_tool("kr"):
        kite = "/opt/kiterunner/routes-large.kite"
        if os.path.exists(kite):
            info("kiterunner API route discovery...")
            for url in crawl_targets[:10]:
                safe = hashlib.md5(url.encode()).hexdigest()[:8]
                run(f"kr scan '{url}' -w {kite} -o {ep_dir}/kr_{safe}.txt", timeout=120)

    # ── Sensitive file / path probing ──
    info("Probing for exposed sensitive files on live hosts...")
    sensitive_dir = out / "vulns"
    sensitive_dir.mkdir(exist_ok=True)
    sensitive_paths = [
        "/.git/HEAD", "/.git/config", "/.env", "/.env.local", "/.env.production",
        "/robots.txt", "/sitemap.xml", "/.DS_Store", "/crossdomain.xml",
        "/server-status", "/server-info", "/.htaccess", "/.htpasswd",
        "/wp-config.php.bak", "/web.config", "/config.json", "/config.yaml",
        "/package.json", "/composer.json", "/Dockerfile", "/docker-compose.yml",
        "/.well-known/security.txt", "/swagger.json", "/swagger-ui.html",
        "/openapi.json", "/api-docs", "/graphql", "/graphiql",
        "/actuator", "/actuator/env", "/actuator/health", "/actuator/configprops",
        "/debug", "/trace", "/info", "/metrics", "/heapdump",
        "/elmah.axd", "/phpinfo.php", "/test.php", "/.svn/entries",
        "/backup.zip", "/backup.sql", "/db.sql", "/dump.sql",
        "/.idea/workspace.xml", "/.vscode/settings.json",
        "/WEB-INF/web.xml", "/META-INF/MANIFEST.MF",
        "/console", "/admin", "/login", "/register",
    ]
    probe_targets = crawl_targets[:5]
    for base_url in probe_targets:
        base = base_url.rstrip("/")
        for path in sensitive_paths:
            body, code = fetch_url(f"{base}{path}", timeout=5)
            if code == 200 and len(body) > 10:
                # Validate it's not a generic error page
                is_git = path.startswith("/.git") and ("ref:" in body or "[core]" in body)
                is_env = path == "/.env" and ("=" in body and any(k in body.upper() for k in ["KEY", "SECRET", "PASSWORD", "TOKEN", "DB_"]))
                is_json = path.endswith(".json") and (body.strip().startswith("{") or body.strip().startswith("["))
                is_xml = path.endswith(".xml") and "<" in body
                is_actuator = "actuator" in path and (body.strip().startswith("{") or body.strip().startswith("["))
                is_plain = path in ["/robots.txt", "/.htpasswd", "/server-status", "/server-info"]
                is_php = path in ["/phpinfo.php"] and "phpinfo" in body.lower()
                is_backup = any(path.endswith(ext) for ext in [".zip", ".sql", ".bak"])

                if any([is_git, is_env, is_json, is_xml, is_actuator, is_plain, is_php, is_backup]):
                    hit(f"SENSITIVE FILE: {base}{path} [{code}]")
                    append_file(str(sensitive_dir / "sensitive_files.txt"), f"{base}{path}")
    sens_count = count_lines(sensitive_dir / "sensitive_files.txt")
    if sens_count > 0:
        hit(f"Total sensitive files found: {sens_count}")
    else:
        ok("No obvious sensitive files exposed")

    # Merge all URLs
    run(f"cat {ep_dir}/*.txt 2>/dev/null | sort -u > {ep_dir}/all_urls.txt")
    total = count_lines(ep_dir / "all_urls.txt")
    ok(f"Total unique URLs: {total}")
    return total

# ─────────────────────────────────────────────────────────────
# PHASE 6 — PARAMETER DISCOVERY
# ─────────────────────────────────────────────────────────────
def phase_params(target, out):
    ph("PHASE 6: PARAMETER DISCOVERY")
    params_dir = out / "params"
    ep_dir     = out / "endpoints"
    params_dir.mkdir(exist_ok=True)

    # Extract params from historical URLs
    if check_tool("unfurl"):
        info("Extracting params from historical URLs...")
        run(f"cat {ep_dir}/gau_urls.txt 2>/dev/null | unfurl keys | sort -u > {params_dir}/historical_params.txt")
        ok(f"Historical params: {count_lines(params_dir/'historical_params.txt')}")

    all_urls_file = ep_dir / "all_urls.txt"

    # SSRF-prone params
    ssrf_params = r"(url|redirect|next|dest|callback|path|uri|href|src|fetch|load|import|export|proxy|target|return|file|view|preview|show|link|host|domain|page|open|to|forward|redir|r|u|ref)="
    run(f"grep -iE '{ssrf_params}' {all_urls_file} 2>/dev/null | sort -u > {params_dir}/ssrf_prone.txt")
    ssrf_count = count_lines(params_dir / "ssrf_prone.txt")
    if ssrf_count > 0:
        hit(f"SSRF-prone parameters: {ssrf_count} URLs — test with Interactsh!")

    # Open redirect params
    redirect_params = r"(url=|return=|next=|goto=|redirect=|redir=|dest=|destination=|r=|go=|target=|continue=|back=|jump=)"
    run(f"grep -iE '{redirect_params}' {all_urls_file} 2>/dev/null | sort -u > {params_dir}/redirect_prone.txt")
    ok(f"Redirect-prone params: {count_lines(params_dir/'redirect_prone.txt')}")

    # Injection params
    inject_params = r"(q=|search=|id=|uid=|user_id=|pid=|query=|keyword=|cmd=|exec=|order=|sort=|filter=|cat=|type=|role=|user=|name=|where=|select=|report=)"
    run(f"grep -iE '{inject_params}' {all_urls_file} 2>/dev/null | sort -u > {params_dir}/injection_prone.txt")
    ok(f"Injection-prone params: {count_lines(params_dir/'injection_prone.txt')}")

    # XSS-prone params (reflected input candidates)
    xss_params = r"(q=|search=|query=|keyword=|lang=|title=|msg=|message=|comment=|body=|text=|content=|html=|value=|data=|input=|name=|username=|email=|error=|preview=|template=|markup=|callback=|jsonp=)"
    run(f"grep -iE '{xss_params}' {all_urls_file} 2>/dev/null | sort -u > {params_dir}/xss_prone.txt")
    xss_count = count_lines(params_dir / "xss_prone.txt")
    if xss_count > 0:
        hit(f"XSS-prone parameters: {xss_count} URLs — feed to dalfox or XSStrike!")
    else:
        ok("No XSS-prone parameters found")

    # IDOR-prone params
    idor_params = r"(id=|uid=|user_id=|pid=|account=|order_id=|invoice=|doc=|document=|profile=|ref=|number=|no=|num=)"
    run(f"grep -iE '{idor_params}' {all_urls_file} 2>/dev/null | sort -u > {params_dir}/idor_prone.txt")
    idor_count = count_lines(params_dir / "idor_prone.txt")
    if idor_count > 0:
        hit(f"IDOR-prone parameters: {idor_count} URLs — test with different user IDs!")
    else:
        ok("No IDOR-prone parameters found")

    # arjun hidden parameter discovery
    if check_tool("arjun"):
        info("arjun hidden parameter discovery (top 15 endpoints)...")
        live_urls = read_lines(out / "web" / "live_urls.txt")
        for url in live_urls[:15]:
            safe = hashlib.md5(url.encode()).hexdigest()[:8]
            run(f"arjun -u '{url}' -m GET -oJ {params_dir}/arjun_{safe}.json -q", timeout=60)
        ok("arjun complete")

    ok(f"Parameter discovery done")

# ─────────────────────────────────────────────────────────────
# PHASE 7 — JS DEEP RECON
# ─────────────────────────────────────────────────────────────
SECRET_PATTERNS = [
    # ── AWS ──
    ("AWS Access Key",       r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",                                      "CRITICAL"),
    ("AWS Access Key Assignment", r"(?:aws[._-]?)?(?:access[._-]?key[._-]?id|accessKeyId|AWSAccessKeyId)\s*[:=]\s*[\"']?(?:AKIA|ASIA)[0-9A-Z]{16}[\"']?", "CRITICAL"),
    ("AWS Secret Key",       r"(?:aws[._-]?)?(?:secret[._-]?access[._-]?key|secretAccessKey|secret[._-]?key|secretKey|awsSecretAccessKey|AWS_SECRET_ACCESS_KEY|aws_secret)\s*[:=]\s*[\"']?([A-Za-z0-9/+=]{40})[\"']?", "CRITICAL"),
    ("AWS Session Token",    r"(?:aws[._-]?)?(?:session[._-]?token|sessionToken|AWS_SESSION_TOKEN)\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{80,}[\"']?", "CRITICAL"),
    ("AWS Username/Name",    r"(?:aws[._-]?(?:user|username|name|login)|awsUser|awsUsername|awsName)\s*[:=]\s*[\"'][^\"']{3,}[\"']", "MEDIUM"),
    ("AWS Password",         r"(?:aws[._-]?(?:password|passwd|pwd)|awsPassword|awsPass|awsPwd)\s*[:=]\s*[\"'][^\"']{4,}[\"']", "CRITICAL"),
    ("AWS Account ID",       r"(?:aws_account_id|AWS_ACCOUNT_ID)\s*[:=]\s*[\"']?\d{12}[\"']?",       "MEDIUM"),
    ("AWS ARN",              r"arn:aws:[a-zA-Z0-9\-]+:[a-z0-9\-]*:\d{12}:[^\s\"']+",                "MEDIUM"),
    # ── GCP / Firebase ──
    ("Google API Key",       r"AIza[0-9A-Za-z\-_]{35}",                                              "HIGH"),
    ("Google OAuth ID",      r"\d{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com",                   "HIGH"),
    ("Google OAuth Secret",  r"GOCSPX-[a-zA-Z0-9_\-]{28}",                                          "HIGH"),
    ("Firebase URL",         r"https://[a-zA-Z0-9\-]+\.firebaseio\.com",                             "MEDIUM"),
    ("Firebase API Key",     r"(?:firebase|FIREBASE)[_-]?(?:API[_-]?KEY|KEY)\s*[:=]\s*[\"']?AIza[0-9A-Za-z\-_]{35}", "HIGH"),
    ("GCP Service Account",  r"\"type\":\s*\"service_account\"",                                      "CRITICAL"),
    # ── Stripe ──
    ("Stripe Secret",        r"sk_live_[0-9a-zA-Z]{24,99}",                                          "CRITICAL"),
    ("Stripe Restricted",    r"rk_live_[0-9a-zA-Z]{24,99}",                                          "CRITICAL"),
    ("Stripe Publishable",   r"pk_(live|test)_[0-9a-zA-Z]{24,99}",                                   "INFO"),
    # ── GitHub / GitLab ──
    ("GitHub Token",         r"(ghp_|gho_|ghu_|ghs_|ghr_)[0-9a-zA-Z]{36}",                          "CRITICAL"),
    ("GitHub Fine-Grained",  r"github_pat_[0-9a-zA-Z_]{82}",                                         "CRITICAL"),
    ("GitLab Token",         r"glpat-[0-9a-zA-Z\-_]{20}",                                            "CRITICAL"),
    ("GitLab Pipeline",      r"glptt-[0-9a-fA-F]{40}",                                               "HIGH"),
    # ── Slack ──
    ("Slack Token",          r"xox[baprs]-[0-9A-Za-z\-]{10,250}",                                    "HIGH"),
    ("Slack Webhook",        r"https://hooks\.slack\.com/services/T[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]+","HIGH"),
    # ── Communication / SaaS ──
    ("Discord Webhook",      r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_\-]+",       "HIGH"),
    ("Discord Bot Token",    r"[MN][A-Za-z\d]{23,68}\.[A-Za-z\d\-_]{6}\.[A-Za-z\d\-_]{27,}",        "HIGH"),
    ("Twilio SID",           r"AC[a-zA-Z0-9]{32}",                                                    "HIGH"),
    ("Twilio Auth Token",    r"(?:twilio|TWILIO).*(?:auth|AUTH).*[:=]\s*[\"']?[a-f0-9]{32}[\"']?",   "HIGH"),
    ("SendGrid Key",         r"SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}",                         "HIGH"),
    ("Mailgun Key",          r"key-[0-9a-zA-Z]{32}",                                                  "HIGH"),
    ("Mailchimp Key",        r"[a-f0-9]{32}-us\d{1,2}",                                               "HIGH"),
    # ── Auth Tokens ──
    ("JWT Token",            r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]*",          "HIGH"),
    ("Bearer Token",         r"Bearer\s+[a-zA-Z0-9._\-]{20,}",                                       "HIGH"),
    ("Private Key",          r"-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----",                 "CRITICAL"),
    ("Basic Auth URL",       r"https?://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_!@#$%^&*]+@[a-zA-Z0-9.-]+",     "CRITICAL"),
    ("OAuth Client Secret",  r"(?:client_secret|CLIENT_SECRET)\s*[:=]\s*[\"'][a-zA-Z0-9_\-]{20,}[\"']", "HIGH"),
    # ── Cloud Providers ──
    ("Azure Secret",         r"(?:azure|AZURE).*(?:secret|SECRET|key|KEY)\s*[:=]\s*[\"'][A-Za-z0-9+/=]{30,}[\"']", "CRITICAL"),
    ("Azure Connection Str", r"(?:DefaultEndpointsProtocol|AccountKey|SharedAccessSignature)=[^\s;\"']+", "CRITICAL"),
    ("DigitalOcean Token",   r"dop_v1_[a-f0-9]{64}",                                                  "CRITICAL"),
    ("DigitalOcean Spaces",  r"(?:SPACES|DIGITAL_OCEAN).*(?:SECRET|KEY)\s*[:=]\s*[\"'][A-Za-z0-9/+=]{40,}[\"']", "HIGH"),
    # ── Database ──
    ("MongoDB URI",          r"mongodb(\+srv)?://[^\s\"'<>]{10,}",                                    "CRITICAL"),
    ("PostgreSQL URI",       r"postgres(ql)?://[^\s\"'<>]{10,}",                                      "CRITICAL"),
    ("MySQL URI",            r"mysql://[^\s\"'<>]{10,}",                                               "CRITICAL"),
    ("Redis URI",            r"redis://[^\s\"'<>]{10,}",                                               "HIGH"),
    # ── AI / ML Keys ──
    ("OpenAI Key",           r"sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}",                          "CRITICAL"),
    ("OpenAI Project Key",   r"sk-proj-[a-zA-Z0-9_\-]{80,}",                                         "CRITICAL"),
    ("Anthropic Key",        r"sk-ant-[a-zA-Z0-9_\-]{80,}",                                           "CRITICAL"),
    ("HuggingFace Token",    r"hf_[a-zA-Z0-9]{34}",                                                   "HIGH"),
    # ── SaaS Specific ──
    ("Shopify Token",        r"(shpat_|shpss_|shppa_)[a-fA-F0-9]{32}",                               "CRITICAL"),
    ("Supabase Key",         r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",              "HIGH"),
    ("Supabase Service Key", r"(?:supabase|SUPABASE).*(?:service|SERVICE).*[:=]\s*[\"']?eyJ[^\s\"']+","CRITICAL"),
    ("Algolia Admin Key",    r"(?:algolia|ALGOLIA).*(?:admin|ADMIN).*[:=]\s*[\"']?[a-f0-9]{32}[\"']?","HIGH"),
    ("Mapbox Token",         r"(pk|sk)\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+",                       "HIGH"),
    ("NPM Token",            r"npm_[a-zA-Z0-9]{36}",                                                  "CRITICAL"),
    ("Cloudinary URL",       r"cloudinary://\d+:[A-Za-z0-9_\-]+@[a-zA-Z0-9]+",                      "HIGH"),
    ("Sentry DSN",           r"https://[a-f0-9]{32}@[a-z0-9]+\.ingest\.sentry\.io/\d+",             "MEDIUM"),
    ("Datadog Key",          r"(?:datadog|DD).*(?:API|APP).*(?:KEY|key)\s*[:=]\s*[\"']?[a-f0-9]{32,40}[\"']?", "HIGH"),
    ("LaunchDarkly SDK Key", r"sdk-[a-f0-9]{24,}",                                                   "HIGH"),
    ("Sentry Auth Token",    r"sntryu_[A-Za-z0-9_\-]{20,}",                                          "HIGH"),
    ("Vercel Token",         r"(?:vercel|VERCEL).*?(?:token|TOKEN)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{20,}[\"']", "HIGH"),
    ("Clerk Key",            r"(?:pk|sk)_(?:test|live)_[A-Za-z0-9]{20,}",                            "HIGH"),
    ("Razorpay Key",         r"rzp_(?:test|live)_[A-Za-z0-9]{14,}",                                  "MEDIUM"),
    # ── Generic High-Value ──
    ("API Key Generic",      r"(?:api[._-]?key|apikey|api[._-]?secret|access[._-]?key)\s*[:=]+\s*[\"'][^\"']{10,}[\"']", "HIGH"),
    ("Frontend Env Value",   r"(?:REACT_APP|NEXT_PUBLIC|VITE|PUBLIC)_[A-Z0-9_]{3,}\s*[:=]\s*[\"'][^\"']{8,}[\"']", "MEDIUM"),
    ("Secret Generic",       r"(?:secret|SECRET|private[._-]?key|PRIVATE[._-]?KEY|auth[._-]?token|AUTH[._-]?TOKEN)\s*[:=]+\s*[\"'][^\"']{10,}[\"']", "HIGH"),
    ("Password",             r"(?:password|passwd|pwd|passphrase|PASS|PASSWORD)\s*[:=]+\s*[\"'][^\"']{4,}[\"']", "HIGH"),
    ("Username/Login",       r"(?:username|user_name|login|account|client[._-]?id|clientId)\s*[:=]+\s*[\"'][^\"']{3,}[\"']", "MEDIUM"),
    ("Encryption Key",       r"(?:encryption[._-]?key|ENCRYPTION[._-]?KEY|crypto[._-]?key|aes[._-]?key)\s*[:=]+\s*[\"'][^\"']{10,}[\"']", "HIGH"),
    ("Internal URL",         r"https?://(internal\.|staging\.|dev\.|localhost|127\.0\.0\.1|192\.168\.|10\.)[^\s\"']+", "MEDIUM"),
    # ── Dev Hygiene ──
    ("Feature Flag",         r"(isAdmin|adminMode|debugMode|devMode|featureFlag|isSuperUser)\s*[:=]", "MEDIUM"),
    ("Hardcoded Creds",      r"(?:username|user|login)\s*[:=]+\s*[\"'][^\"']{3,}[\"'].*(?:password|passwd|pwd)\s*[:=]+\s*[\"'][^\"']{3,}[\"']", "CRITICAL"),
    ("TODO/FIXME",           r"(TODO|FIXME|HACK|backdoor|hardcoded|remove.?before.?prod)", "INFO"),
    ("Debug Statement",      r"(console\.log|debugger;|alert\(|print_r\(|var_dump\()",     "INFO"),
]

def calc_shannon_entropy(s):
    """Calculate Shannon entropy of a string."""
    import math
    if not s:
        return 0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count/length) * math.log2(count/length) for count in freq.values())

def scan_js_secrets(js_dir, secrets_dir, extra_dirs=None):
    """Scan downloaded JS and extracted sources for secrets + credential pairs."""
    secrets_dir = Path(secrets_dir)
    scan_roots = [Path(js_dir)]
    for extra in extra_dirs or []:
        extra = Path(extra)
        if extra.exists():
            scan_roots.append(extra)

    allowed_suffixes = {".js", ".mjs", ".jsx", ".ts", ".tsx", ".map", ".txt"}
    scan_files = []
    seen_paths = set()
    for root in scan_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
                continue
            resolved = str(path.resolve())
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            if path.parent.name in ("maps", "sources"):
                label = f"{path.parent.name}/{path.name}"
            else:
                label = path.name
            scan_files.append((path, label))

    if not scan_files:
        return {}

    findings = {}

    def save_finding(pattern_name, severity, matches):
        if not matches:
            return
        deduped = []
        seen = set()
        for item in matches:
            marker = (item.get("file", ""), item.get("match", ""), item.get("context", ""))
            if marker in seen:
                continue
            seen.add(marker)
            deduped.append(item)
        if not deduped:
            return
        findings[pattern_name] = {"severity": severity, "matches": deduped}
        safe_name = pattern_name.lower().replace(' ', '_').replace('/', '_')
        out_file = secrets_dir / f"js_{safe_name}.json"
        import json as _json
        with open(out_file, "w") as f:
            _json.dump(deduped, f, indent=2)

    for pattern_name, pattern, severity in SECRET_PATTERNS:
        matches = []
        regex = re.compile(pattern, re.IGNORECASE)
        for jsf, label in scan_files:
            try:
                content = jsf.read_text(errors="ignore")
                for m in regex.finditer(content):
                    snippet = content[max(0, m.start()-80):m.end()+120].replace("\n", " ")
                    matches.append({"file": label, "match": m.group(), "context": snippet[:300]})
            except:
                pass
        save_finding(pattern_name, severity, matches)

    kv_re = re.compile(
        r"""(?:(?P<q>["'])(?P<qkey>[A-Za-z0-9_$ .\-]{2,80})(?P=q)|(?P<key>[A-Za-z_$][\w$.-]{1,80}))"""
        r"""\s*[:=]\s*(?P<quote>["'`])(?P<value>[^"'`\r\n]{3,300})(?P=quote)""",
        re.IGNORECASE
    )
    placeholder_values = {"true", "false", "null", "undefined", "none", "todo", "changeme", "change_me", "example", "sample"}

    def norm_key(key):
        return re.sub(r"[^a-z0-9]", "", key.lower())

    def is_secret_key(key):
        k = norm_key(key)
        return any(x in k for x in [
            "password", "passwd", "pwd", "passphrase", "secret", "token", "credential",
            "privatekey", "clientsecret", "apikey", "accesskey", "secretaccesskey", "sessiontoken"
        ])

    def is_identity_key(key, context=""):
        k = norm_key(key)
        ctx = context.lower()
        if any(x in k for x in ["username", "user", "login", "email", "account", "clientid", "accesskeyid", "awsname", "awsuser"]):
            return True
        return k == "name" and ("aws" in ctx or "credential" in ctx or "auth" in ctx)

    def is_aws_context(key, context):
        k = norm_key(key)
        ctx = context.lower()
        return "aws" in k or "aws" in ctx or "amazonaws" in ctx or "accesskeyid" in k or "secretaccesskey" in k

    assignment_hits = []
    aws_assignment_hits = []
    credential_pair_hits = []
    aws_pair_hits = []

    for jsf, label in scan_files:
        try:
            content = jsf.read_text(errors="ignore")
        except:
            continue

        kvs = []
        for m in kv_re.finditer(content):
            key = (m.group("qkey") or m.group("key") or "").strip()
            value = (m.group("value") or "").strip()
            if not key or value.lower() in placeholder_values:
                continue
            context = content[max(0, m.start()-250):m.end()+250].replace("\n", " ")
            kvs.append({"key": key, "value": value, "start": m.start(), "end": m.end(), "context": context})

            if is_secret_key(key) and len(value) >= 4:
                hit_item = {
                    "file": label,
                    "match": f"{key}={value[:100]}",
                    "context": context[:350]
                }
                assignment_hits.append(hit_item)
                if is_aws_context(key, context):
                    aws_assignment_hits.append(hit_item)
            elif is_aws_context(key, context) and is_identity_key(key, context) and len(value) >= 3:
                aws_assignment_hits.append({
                    "file": label,
                    "match": f"{key}={value[:100]}",
                    "context": context[:350]
                })

        identities = [item for item in kvs if is_identity_key(item["key"], item["context"])]
        secrets = [item for item in kvs if is_secret_key(item["key"]) and len(item["value"]) >= 4]
        for secret in secrets:
            for identity in identities:
                if abs(secret["start"] - identity["start"]) > 1800:
                    continue
                start = max(0, min(secret["start"], identity["start"]) - 250)
                end = min(len(content), max(secret["end"], identity["end"]) + 250)
                context = content[start:end].replace("\n", " ")[:500]
                pair = {
                    "file": label,
                    "match": f"{identity['key']}={identity['value'][:80]} | {secret['key']}={secret['value'][:80]}",
                    "context": context
                }
                if is_aws_context(identity["key"] + secret["key"], context):
                    aws_pair_hits.append(pair)
                else:
                    credential_pair_hits.append(pair)

    save_finding("Sensitive Key Assignment", "HIGH", assignment_hits)
    save_finding("AWS Named Credential", "CRITICAL", aws_assignment_hits)
    save_finding("Credential Pair", "CRITICAL", credential_pair_hits)
    save_finding("AWS Credential Pair", "CRITICAL", aws_pair_hits)

    # ── Entropy-based secret detection ──
    # Catches secrets that don't match any known pattern.
    # Match both standalone keywords AND keywords embedded in camelCase/snake_case/PascalCase identifiers.
    high_entropy_re = re.compile(
        r"""(?:[a-zA-Z0-9_$]*?(?:secret|key|token|password|passwd|pwd|passphrase|credential|apikey|api_key|access_key|private|session|auth|hash|salt|cipher)[a-zA-Z0-9_$]*?)"""
        r"""\s*[:=]\s*["']([A-Za-z0-9+/=_\-.$@!]{16,})["']""",
        re.IGNORECASE
    )
    entropy_hits = []
    for jsf, label in scan_files:
        try:
            content = jsf.read_text(errors="ignore")
            for m in high_entropy_re.finditer(content):
                val = m.group(1)
                ent = calc_shannon_entropy(val)
                if ent > 3.5 and len(val) >= 16 and val.lower() not in ("true", "false", "null", "undefined", "none"):
                    snippet = content[max(0, m.start()-80):m.end()+120].replace("\n", " ")
                    entropy_hits.append({
                        "file": label,
                        "match": val[:80] + ("..." if len(val) > 80 else ""),
                        "entropy": round(ent, 2),
                        "context": snippet[:300]
                    })
        except:
            pass

    save_finding("High Entropy Secrets", "HIGH", entropy_hits)

    # ── Naked Credential Scan ──
    # Catches credential-like values that appear without a key-value assignment or
    # that don't fit the entropy regex pattern but are clearly credentials.
    naked_re = re.compile(
        r"""["']([A-Za-z0-9+/=_\-.$@!\\]{20,})["']""",
        re.IGNORECASE
    )
    naked_cred_hits = []
    seen_naked = set()
    for jsf, label in scan_files:
        try:
            content = jsf.read_text(errors="ignore")
        except Exception:
            continue
        for m in naked_re.finditer(content):
            val = m.group(1)
            if len(val) < 20 or len(val) > 500:
                continue
            val_lower = val.lower()
            if val_lower in ("true", "false", "null", "undefined", "none", "changeme", "example"):
                continue
            # Skip values that look like typical non-secret patterns (URLs, dates, hex colors, etc.)
            if re.match(r"^[a-fA-F0-9]{32,}$", val):
                continue  # pure hex md5/sha1-like hashes are too noisy
            if re.match(r"^https?://", val):
                continue
            if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", val):
                continue  # email
            # Check if this value is near a credential-like keyword in the surrounding context
            start = max(0, m.start() - 200)
            end = min(len(content), m.end() + 200)
            context = content[start:end].lower()
            if not any(kw in context for kw in
                ["password", "secret", "token", "key", "auth", "credential",
                 "access", "login", "user", "admin", "passwd", "pwd",
                 "aws", "api", "private", "bearer", "jwt", "session"]):
                continue
            ent = calc_shannon_entropy(val)
            if ent < 3.2 and not any(val.startswith(prefix) for prefix in ("AKIA", "ASIA", "eyJ", "sk-", "ghp_", "gho_", "ghs_", "ghr_", "xox", "glpat", "dop_v", "npm_")):
                continue
            marker = (label, val[:60])
            if marker in seen_naked:
                continue
            seen_naked.add(marker)
            snippet = content[max(0, m.start()-80):m.end()+120].replace("\n", " ")
            naked_cred_hits.append({
                "file": label,
                "match": val[:80] + ("..." if len(val) > 80 else ""),
                "entropy": round(ent, 2),
                "context": snippet[:350]
            })

    save_finding("Naked Credential (untyped)", "HIGH", naked_cred_hits)

    return findings


# ─────────────────────────────────────────────────────────────
# AI-POWERED SECRET SCANNING (optional — overrides regex)
# ─────────────────────────────────────────────────────────────
# When enabled via --ai-secrets, this function scans all JS files
# and extracted source-map sources using an LLM instead of regex.
#
# Supported providers (set via --ai-provider):
#   openai   – OpenAI-compatible API (env: OPENAI_API_KEY) — works with GPT, DeepSeek, etc.
#   claude   – Anthropic Claude API (env: ANTHROPIC_API_KEY)
#   ollama   – local Ollama (default http://localhost:11434, env: OLLAMA_HOST)
#
# Returns a list of finding dicts compatible with the per-file report.
# -----------------------------------------------------------------
AI_CONFIG = {"enabled": False, "only": False, "provider": "openai", "model": None, "api_key": None, "api_base": None}

def ai_scan_js_secrets(files_dir, maps_dir, secrets_dir):
    """Use an LLM to find secrets in JS files and extracted source-map sources.
    Returns a list of {severity, type, file, match, context} dicts or empty list.
    """
    cfg = AI_CONFIG
    provider = cfg.get("provider", "openai")
    model = cfg.get("model")
    api_key = cfg.get("api_key") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    api_base = cfg.get("api_base") or os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    if provider == "ollama":
        api_base = api_base.rstrip("/")
    elif provider == "claude":
        if not api_base:
            api_base = "https://api.anthropic.com/v1"

    # Gather all scan targets (JS files + extracted source-map sources)
    scan_roots = [Path(files_dir)]
    sources_dir = Path(str(maps_dir)) / "sources"
    if sources_dir.exists():
        scan_roots.append(sources_dir)
    scan_targets = []
    for root in scan_roots:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in (".js", ".mjs", ".jsx", ".ts", ".tsx", ".txt", ".json", ".env"):
                continue
            # Derive a short label that includes parent dir context (files/ vs sources/)
            rel = p.relative_to(root.parent if root.name in ("files", "sources") else root)
            scan_targets.append((str(rel), p))

    if not scan_targets:
        return []

    total = len(scan_targets)
    info(f"AI secret scan: {total} file(s) across {len(scan_roots)} source(s) via {provider}")

    system_prompt = (
        "You are a JavaScript security analyst. Your task is to find hardcoded "
        "secrets, credentials, API keys, tokens, passwords, and other sensitive "
        "strings in JavaScript source code.\n\n"
        "Rules:\n"
        "- Return ONLY a valid JSON array. No markdown, no explanation.\n"
        "- If nothing is found, return []\n"
        "- Each element must have these keys:\n"
        '  "type": short label like "AWS Access Key" / "Password" / "API Token"\n'
        '  "value": the full secret or first 120 chars\n'
        '  "file": the filename (use the exact label provided after ``FILE:``)\n'
        '  "line": approximate line number (or 0 if unsure)\n'
        '  "confidence": "high" or "medium"\n'
        "- Only report real secrets. Ignore placeholder values like 'your-api-key', 'changeme', 'password123', example.com.\n"
        "- Be thorough: look for base64-encoded credentials, JWT tokens, AWS keys (AKIA...), "
        "Google API keys (AIza...), private keys, connection strings, hardcoded passwords, "
        "OAuth tokens, bearer tokens, and any credential-like strings.\n"
        "- Report a secret even if it looks obfuscated or split across variables.\n"
    )

    headers_json = {"Content-Type": "application/json"}
    all_findings = []
    seen_markers = set()
    files_skipped = 0

    for label, filepath in scan_targets:
        try:
            body = filepath.read_text(errors="ignore")
        except Exception:
            continue
        if not body.strip():
            continue

        # Skip files that are obviously large bundles (over 50k chars) — send last 30k + first 5k
        chunk = body
        if len(body) > 50000:
            chunk = body[:5000] + "\n\n... [SNIPPED] ...\n\n" + body[-30000:]
            files_skipped += 1

        # Wrap with a file marker so the AI can report which file a secret is in
        user_msg = f"FILE: {label}\n```javascript\n{chunk[:32000]}\n```"

        payload = None
        try:
            if provider == "ollama":
                effective_model = model or "llama3"
                payload = json.dumps({
                    "model": effective_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "stream": False,
                    "options": {"num_predict": 2048, "temperature": 0.1}
                }).encode()
                req = urllib.request.Request(
                    f"{api_base}/api/chat",
                    data=payload,
                    headers=headers_json,
                    method="POST"
                )
            elif provider == "claude":
                effective_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
                effective_model = model or "claude-sonnet-4-20250514"
                if not effective_key:
                    warn("ANTHROPIC_API_KEY not set — skipping AI scan")
                    return []
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": effective_key,
                    "anthropic-version": "2023-06-01"
                }
                payload = json.dumps({
                    "model": effective_model,
                    "max_tokens": 2048,
                    "temperature": 0.1,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_msg}
                    ]
                }).encode()
                req = urllib.request.Request(
                    f"{api_base}/messages",
                    data=payload,
                    headers=headers,
                    method="POST"
                )
            else:
                # default: OpenAI-compatible (GPT, DeepSeek, etc.)
                effective_key = api_key or os.environ.get("OPENAI_API_KEY", "")
                effective_model = model or "gpt-4o-mini"
                if not effective_key:
                    warn("OPENAI_API_KEY not set — skipping AI scan")
                    return []
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {effective_key}"
                }
                payload = json.dumps({
                    "model": effective_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.1
                }).encode()
                req = urllib.request.Request(
                    f"{cfg.get('api_base') or 'https://api.openai.com/v1'}/chat/completions",
                    data=payload,
                    headers=headers,
                    method="POST"
                )

            resp = urllib.request.urlopen(req, timeout=120)
            raw = resp.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)

            if provider == "ollama":
                content = data.get("message", {}).get("content", "")
            elif provider == "claude":
                content = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        content += block.get("text", "")
            else:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                continue

            # AI may try to wrap in markdown fences; strip those
            clean = content.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[-1]
                clean = clean.rsplit("```", 1)[0]
            clean = clean.strip()

            if clean.startswith("["):
                try:
                    items = json.loads(clean)
                    if isinstance(items, list):
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            ftype = item.get("type", "Unknown") or "Unknown"
                            fval = (item.get("value") or "")[:120]
                            ffile = item.get("file") or label
                            fline = item.get("line", 0) or 0
                            conf = item.get("confidence", "medium") or "medium"
                            sev = "CRITICAL" if conf == "high" else "HIGH"
                            marker = (ffile, fval[:60])
                            if marker in seen_markers:
                                continue
                            seen_markers.add(marker)
                            all_findings.append({
                                "severity": sev,
                                "type": ftype,
                                "file": ffile,
                                "match": fval,
                                "line": fline,
                                "context": f"[AI {provider}/{conf}] {ftype}"
                            })
                except Exception:
                    pass
        except urllib.error.HTTPError as e:
            body_err = e.read().decode(errors="ignore")[:300]
            warn(f"AI API error for {label} (HTTP {e.code}): {body_err}")
        except urllib.error.URLError:
            if provider == "ollama":
                warn(f"Ollama not reachable at {api_base}. Is it running?")
            else:
                warn(f"API unreachable. Check --ai-api-base or network.")
            break  # no point retrying if the service is down
        except (json.JSONDecodeError, socket.timeout, Exception) as e:
            warn(f"AI parse/connection error for {label}: {e}")

    if files_skipped:
        info(f"AI scan: {files_skipped} large file(s) were truncated")

    # Save results
    if all_findings:
        findings_file = Path(secrets_dir) / "js_ai_findings.json"
        with open(findings_file, "w") as f:
            json.dump(all_findings, f, indent=2)
        txt_lines = []
        for item in all_findings:
            txt_lines.append(f"[{item['severity']}] {item['type']} in {item['file']} (line {item.get('line', '?')})")
            txt_lines.append(f"  Value: {item['match']}")
            txt_lines.append("")
        (Path(secrets_dir) / "js_ai_findings.txt").write_text("\n".join(txt_lines))
        hit(f"AI secrets found: {len(all_findings)} → secrets/js_ai_findings.json")
    else:
        ok("AI scan: no secrets found")

    return all_findings


def generate_js_findings_report(js_dir, secrets_dir, findings):
    """Generate a per-file report: for each JS file, list what was found in it."""
    files_dir = Path(js_dir) / "files"
    source_dir = Path(js_dir) / "maps" / "sources"
    js_files = list(files_dir.glob("*.js"))
    if source_dir.exists():
        js_files.extend([p for p in source_dir.rglob("*") if p.is_file() and p.suffix.lower() in (".js", ".mjs", ".jsx", ".ts", ".tsx", ".txt")])
    if not js_files:
        return

    # Build reverse map: filename -> list of (pattern_name, severity, match, context)
    file_map = {}
    for pattern_name, data in findings.items():
        for m in data["matches"]:
            fname = m.get("file", "")
            if fname not in file_map:
                file_map[fname] = []
            file_map[fname].append({
                "type": pattern_name,
                "severity": data["severity"],
                "match": m.get("match", ""),
                "context": m.get("context", ""),
                "entropy": m.get("entropy", None),
            })

    # Also scan for sensitive patterns in JS files that might not be in findings
    # (e.g. interesting strings, API routes, internal URLs)
    extra_patterns = [
        ("Internal/Staging URL", r"https?://(internal\.|staging\.|dev\.|localhost|127\.0\.0\.1|192\.168\.|10\.)[^\s\"']+"),
        ("Admin/Debug Route",    r"[\"'](/(?:admin|debug|internal|config|backup|swagger|api-docs)[^\"']*)[\"']"),
        ("Hardcoded Email",      r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        ("Commented Credential", r"//.*(?:password|secret|token|key)\s*[:=]\s*[^\s]+"),
    ]
    for jsf in js_files:
        fname = jsf.name
        try:
            content = jsf.read_text(errors="ignore")
            for pname, pat in extra_patterns:
                for m in re.finditer(pat, content, re.IGNORECASE):
                    snippet = content[max(0, m.start()-30):m.end()+30].replace("\n", " ")
                    if fname not in file_map:
                        file_map[fname] = []
                    # Avoid adding an exact duplicate
                    match_text = m.group()
                    if not any(e["match"] == match_text and e["type"] == pname for e in file_map[fname]):
                        file_map[fname].append({
                            "type": pname,
                            "severity": "INFO",
                            "match": match_text[:120],
                            "context": snippet[:200],
                            "entropy": None,
                        })
        except:
            pass

    if not file_map:
        return

    # Sort by severity order: CRITICAL > HIGH > MEDIUM > INFO
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("  JS SENSITIVE DATA FINDINGS — PER-FILE REPORT")
    report_lines.append("  Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary
    total_findings = sum(len(v) for v in file_map.values())
    crit_count = sum(1 for v in file_map.values() for e in v if e["severity"] == "CRITICAL")
    high_count = sum(1 for v in file_map.values() for e in v if e["severity"] == "HIGH")
    med_count  = sum(1 for v in file_map.values() for e in v if e["severity"] == "MEDIUM")
    info_count = sum(1 for v in file_map.values() for e in v if e["severity"] == "INFO")

    report_lines.append(f"  SUMMARY: {total_findings} findings in {len(file_map)} files")
    report_lines.append(f"  CRITICAL: {crit_count}  |  HIGH: {high_count}  |  MEDIUM: {med_count}  |  INFO: {info_count}")
    report_lines.append("")
    report_lines.append("-" * 80)

    # Sort files: files with CRITICAL findings first, then HIGH, etc.
    def file_sort_key(item):
        fname, entries = item
        best = min(sev_order.get(e["severity"], 99) for e in entries)
        return (best, fname)

    for fname, entries in sorted(file_map.items(), key=file_sort_key):
        # Sort entries within file by severity
        entries.sort(key=lambda e: sev_order.get(e["severity"], 99))

        report_lines.append("")
        report_lines.append(f"  FILE: {fname}")
        report_lines.append(f"  {'─' * 70}")
        report_lines.append(f"  Findings: {len(entries)}")
        report_lines.append("")

        for i, entry in enumerate(entries, 1):
            sev_tag = entry["severity"]
            report_lines.append(f"    [{sev_tag}] {entry['type']}")
            report_lines.append(f"      Match   : {entry['match']}")
            if entry.get("entropy"):
                report_lines.append(f"      Entropy : {entry['entropy']}")
            report_lines.append(f"      Context : {entry['context']}")
            report_lines.append("")

        report_lines.append("-" * 80)

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("  END OF REPORT")
    report_lines.append("=" * 80)

    report_path = Path(secrets_dir) / "js_findings_per_file.txt"
    report_path.write_text("\n".join(report_lines))
    ok(f"Per-file JS findings report saved: {report_path}")

    # Also save as JSON for programmatic access
    import json as _json
    json_report = {}
    for fname, entries in sorted(file_map.items(), key=file_sort_key):
        json_report[fname] = entries
    json_path = Path(secrets_dir) / "js_findings_per_file.json"
    with open(json_path, "w") as f:
        _json.dump(json_report, f, indent=2)

    return report_path


def phase_js(target, out):
    ph("PHASE 7: JAVASCRIPT DEEP RECON")
    js_dir      = out / "js"
    files_dir   = js_dir / "files"
    maps_dir    = js_dir / "maps"
    ep_dir      = out / "endpoints"
    secrets_dir = out / "secrets"
    web_dir     = out / "web"

    for d in [js_dir, files_dir, maps_dir, secrets_dir]:
        d.mkdir(exist_ok=True)

    js_urls_file = js_dir / "js_urls.txt"

    def normalize_js_url(ref, base_url=None):
        ref = (ref or "").strip().strip('"\'`<>')
        if not ref or ref.startswith(("data:", "blob:", "javascript:")):
            return None
        if ref.startswith("//"):
            ref = "https:" + ref
        elif base_url and not ref.startswith(("http://", "https://")):
            ref = urllib.parse.urljoin(base_url, ref)
        if not ref.startswith(("http://", "https://")):
            return None
        parsed = urllib.parse.urlparse(ref)
        path = parsed.path.lower()
        if path.endswith((".js", ".mjs", ".jsx", ".ts", ".tsx")) or "/_next/static/" in path or "/assets/" in path or "/static/" in path:
            return urllib.parse.urlunparse(parsed._replace(fragment=""))
        return None

    def extract_js_refs(content, base_url=None):
        refs = set()
        patterns = [
            r'<script[^>]+src=["\']([^"\']+)["\']',
            r'(?:import|from)\s*["\']([^"\']+)["\']',
            r'import\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'(?:require|importScripts|load)\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'(?:src|href|url)\s*[:=]\s*["\']([^"\']+\.(?:js|mjs|jsx|ts|tsx)(?:[?#][^"\']*)?)["\']',
            r'["\']([^"\']+\.(?:js|mjs|jsx|ts|tsx)(?:[?#][^"\']*)?)["\']',
            r'sourceMappingURL=([^\s*]+)',
        ]
        for pat in patterns:
            for m in re.finditer(pat, content, flags=re.I):
                ref = m.group(1)
                if ref.endswith(".map"):
                    ref = ref[:-4]
                url = normalize_js_url(ref, base_url)
                if url:
                    refs.add(url)
        return refs

    def extract_source_map_refs(content, base_url=None):
        refs = set()
        for m in re.finditer(r'sourceMappingURL=([^\s*]+)', content, flags=re.I):
            ref = m.group(1).strip().strip('"\'`)')
            if not ref or ref.startswith("data:"):
                continue
            if ref.startswith("//"):
                ref = "https:" + ref
            elif base_url and not ref.startswith(("http://", "https://")):
                ref = urllib.parse.urljoin(base_url, ref)
            if ref.startswith(("http://", "https://")) and ".map" in urllib.parse.urlparse(ref).path.lower():
                refs.add(urllib.parse.urlunparse(urllib.parse.urlparse(ref)._replace(fragment="")))
        return refs

    def extract_manifest_js_refs(content, manifest_url):
        refs = set()
        parsed_manifest = urllib.parse.urlparse(manifest_url)
        origin = f"{parsed_manifest.scheme}://{parsed_manifest.netloc}"
        cleaned = content.replace("\\/", "/").replace("\\u002F", "/").replace("\\u002f", "/")

        def add_ref(ref):
            ref = (ref or "").strip().strip('"\'`,')
            if not ref:
                return
            normalized = normalize_js_url(ref, manifest_url)
            if not normalized and ref.startswith("static/") and "/_next/static/" in parsed_manifest.path:
                normalized = normalize_js_url(f"{origin}/_next/{ref}")
            if not normalized and ref.startswith("chunks/"):
                normalized = normalize_js_url(f"{origin}/_next/static/{ref}")
            if normalized:
                refs.add(normalized)

        def walk_json(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    walk_json(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk_json(v)
            elif isinstance(obj, str):
                add_ref(obj)

        try:
            walk_json(json.loads(cleaned))
        except Exception:
            pass

        for m in re.finditer(r'([A-Za-z0-9_./@-]+\.(?:js|mjs|jsx|ts|tsx)(?:[?#][^"\'`\s,)]*)?)', cleaned, flags=re.I):
            add_ref(m.group(1))
        for m in re.finditer(r'(/_next/static/[^"\'`\s,)]*\.(?:js|mjs)(?:[?#][^"\'`\s,)]*)?)', cleaned, flags=re.I):
            add_ref(origin + m.group(1))
        return refs

    # Collect JS URLs
    info("Collecting JS URLs from all sources...")
    run(f"cat {ep_dir}/all_urls.txt 2>/dev/null | grep -E '\\.js([\\?#]|$)' | sort -u > {js_urls_file}")
    run(f"cat {ep_dir}/gau_urls.txt 2>/dev/null | grep -E '\\.js([\\?#]|$)' | sort -u >> {js_urls_file}")

    collected_js = set(read_lines(js_urls_file))
    for src_file in [ep_dir / "all_urls.txt", ep_dir / "gau_urls.txt", ep_dir / "katana_unauth.txt", ep_dir / "katana_auth.txt"]:
        for url in read_lines(src_file):
            normalized = normalize_js_url(url)
            if normalized:
                collected_js.add(normalized)

    # Pull script tags from live HTML pages. This catches webpack/vite/next chunks that crawlers miss.
    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls:
        live_urls = [f"https://{target}", f"http://{target}"]
    info("Extracting script URLs from live HTML pages...")
    base_origins = set()
    next_build_ids = set()
    for page_url in live_urls[:50]:
        parsed_page = urllib.parse.urlparse(page_url)
        if parsed_page.scheme and parsed_page.netloc:
            base_origins.add(f"{parsed_page.scheme}://{parsed_page.netloc}")
        body, code = fetch_url(page_url, timeout=10)
        if code in (200, 401, 403) and body:
            collected_js.update(extract_js_refs(body, page_url))
            for m in re.finditer(r'/_next/static/([^/"\']+)/', body):
                next_build_ids.add((f"{parsed_page.scheme}://{parsed_page.netloc}", m.group(1)))
            for m in re.finditer(r'"buildId"\s*:\s*"([^"\\]+)"', body):
                next_build_ids.add((f"{parsed_page.scheme}://{parsed_page.netloc}", m.group(1)))

    # Framework manifests often reveal chunks that crawlers never request directly.
    info("Checking framework build manifests for hidden JS chunks...")
    manifest_urls = set()
    for origin in sorted(base_origins)[:20]:
        for path in ["/asset-manifest.json", "/manifest.json", "/build/manifest.json", "/mix-manifest.json", "/vite-manifest.json"]:
            manifest_urls.add(origin.rstrip("/") + path)
    for origin, build_id in sorted(next_build_ids)[:50]:
        manifest_urls.add(f"{origin}/_next/static/{build_id}/_buildManifest.js")
        manifest_urls.add(f"{origin}/_next/static/{build_id}/_ssgManifest.js")

    checked_manifests = []
    for manifest_url in sorted(manifest_urls)[:150]:
        body, code = fetch_url(manifest_url, timeout=8)
        if code == 200 and body:
            refs = extract_manifest_js_refs(body, manifest_url)
            if refs:
                checked_manifests.append(f"{manifest_url} -> {len(refs)} JS refs")
                collected_js.update(refs)
    if checked_manifests:
        (js_dir / "js_manifests_checked.txt").write_text("\n".join(checked_manifests) + "\n")
        ok(f"Framework manifests added JS refs: {len(checked_manifests)} manifest(s)")

    if check_tool("getJS"):
        for url in live_urls[:20]:
            run(f"getJS --url '{url}' --complete --nocolors 2>/dev/null >> {js_urls_file}")

    with open(js_urls_file, "a") as f:
        for url in sorted(collected_js):
            f.write(url + "\n")

    run(f"sort -u {js_urls_file} -o {js_urls_file}")
    js_count = count_lines(js_urls_file)
    ok(f"JS files discovered: {js_count}")

    # Download JS files
    info("Downloading JS files locally...")
    js_urls = read_lines(js_urls_file)
    source_by_file = {}

    def download_js(url):
        try:
            fname = hashlib.md5(url.encode()).hexdigest() + ".js"
            out_path = files_dir / fname
            if out_path.exists():
                source_by_file[out_path.name] = url
                return out_path.name
            body, code = fetch_url(url, timeout=15)
            if code in (200, 401, 403) and body and ("javascript" in body[:500].lower() or len(body) > 200):
                out_path.write_text(body, errors="ignore")
                source_by_file[out_path.name] = url
                return out_path.name
        except:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(download_js, js_urls[:3000]))

    downloaded = len(list(files_dir.glob("*.js")))
    ok(f"Downloaded: {downloaded} JS files")

    # ── Recursive JS Crawling — discover JS imports/chunks inside JS ──
    info("Recursive JS crawling (depth 3) — finding imports/chunks inside JS files...")
    discovered_imports = set()
    for depth in range(3):
        new_js = set()
        for jsf in files_dir.glob("*.js"):
            try:
                content = jsf.read_text(errors="ignore")
                base_url = source_by_file.get(jsf.name)
                if not base_url and js_urls:
                    base_url = js_urls[0]
                new_js.update(extract_js_refs(content, base_url))
            except:
                pass
        # Filter out already-downloaded
        new_js -= discovered_imports
        new_js -= set(read_lines(js_urls_file))
        discovered_imports.update(new_js)
        if not new_js:
            break
        # Download newly discovered JS
        info(f"Recursive JS depth {depth + 1}: {len(new_js)} new candidate files")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            list(ex.map(download_js, list(new_js)[:500]))

    new_downloaded = len(list(files_dir.glob("*.js"))) - downloaded
    if new_downloaded > 0:
        ok(f"Recursive JS crawl: {new_downloaded} additional JS files from imports")
        # Append newly found URLs to js_urls_file
        with open(js_urls_file, "a") as f:
            for u in discovered_imports:
                f.write(u + "\n")
        run(f"sort -u {js_urls_file} -o {js_urls_file}")
    else:
        ok("Recursive JS crawl: no additional JS imports found")

    if source_by_file:
        with open(js_dir / "js_file_sources.json", "w") as f:
            json.dump(source_by_file, f, indent=2)

    # Source map detection
    info("Checking for exposed source maps (.js.map)...")
    explicit_map_urls = set()
    for jsf in files_dir.glob("*.js"):
        try:
            content = jsf.read_text(errors="ignore")
            explicit_map_urls.update(extract_source_map_refs(content, source_by_file.get(jsf.name)))
        except Exception:
            pass

    map_candidates = {url + ".map" for url in read_lines(js_urls_file)[:1000]}
    map_candidates.update(explicit_map_urls)
    map_found = []
    def check_map(map_url):
        body, code = fetch_url(map_url, timeout=10)
        if code == 200 and "mappings" in body:
            return map_url
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(check_map, sorted(map_candidates)[:1500]))
        map_found = [r for r in results if r]

    if map_found:
        (js_dir / "source_maps_found.txt").write_text("\n".join(map_found))
        hit(f"SOURCE MAPS FOUND: {len(map_found)} — full source code exposed!")
        for m in map_found:
            hit(f"  → {m}")
        # Download maps
        for map_url in map_found:
            fname = hashlib.md5(map_url.encode()).hexdigest() + ".map"
            body, _ = fetch_url(map_url)
            if body:
                (maps_dir / fname).write_text(body)
    else:
        ok("No public source maps found")

    # LinkFinder
    if check_tool("python3") and os.path.exists("/opt/LinkFinder/linkfinder.py"):
        info("LinkFinder endpoint extraction...")
        run(f"python3 /opt/LinkFinder/linkfinder.py -i '{files_dir}/*.js' -o cli 2>/dev/null | sort -u > {ep_dir}/linkfinder.txt")
        ok(f"LinkFinder endpoints: {count_lines(ep_dir/'linkfinder.txt')}")

    # JSluice (AST-level)
    if check_tool("jsluice"):
        info("JSluice AST-level analysis...")
        if check_tool("jq"):
            run(f"find {files_dir} -name '*.js' | xargs -P5 -I{{}} jsluice urls {{}} 2>/dev/null | jq -r '.url' 2>/dev/null | sort -u > {ep_dir}/jsluice_endpoints.txt")
        else:
            # Fallback: parse jsluice JSON output with grep when jq is missing
            warn("jq not found — using grep fallback for jsluice output")
            run(f"find {files_dir} -name '*.js' | xargs -P5 -I{{}} jsluice urls {{}} 2>/dev/null | grep -oP '\"url\":\\s*\"\\K[^\"]+' | sort -u > {ep_dir}/jsluice_endpoints.txt")
        run(f"find {files_dir} -name '*.js' | xargs -P5 -I{{}} jsluice secrets {{}} 2>/dev/null > {secrets_dir}/jsluice_secrets.json")
        ok(f"JSluice endpoints: {count_lines(ep_dir/'jsluice_endpoints.txt')}")

    # Advanced static analysis over JS and exposed source maps.
    info("Advanced JS analysis: API calls, routes, GraphQL, storage, sinks, configs...")
    endpoint_patterns = [
        r'"(/[a-zA-Z0-9_/${}?.=&%:,@+\-./]{2,})"',
        r"'(/[a-zA-Z0-9_/${}?.=&%:,@+\-./]{2,})'",
        r'`(/[a-zA-Z0-9_/${}?.=&%:,@+\-./]{2,})`',
        r"(?:url|uri|endpoint|baseURL|baseUrl|apiUrl|api_url|proxy|target)\s*[:=]\s*['\"]([^'\"]{3,})['\"]",
        r"fetch\s*\(\s*['\"]([^'\"]{3,})['\"]",
        r"axios\.(?:get|post|put|patch|delete|request)\s*\(\s*['\"]([^'\"]{3,})['\"]",
        r"https?://[^\s\"'`<>]+",
    ]
    ignore_exts = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".ico", ".woff", ".woff2", ".ttf", ".mp4", ".webp")
    analysis_blobs = []
    all_endpoints = set()
    all_absolute_urls = set()
    api_calls = []
    graphql_ops = []
    client_routes = set()
    storage_keys = set()
    interesting_config = set()
    dangerous_sinks = []
    priority_scores = {}

    for jsf in files_dir.glob("*.js"):
        try:
            analysis_blobs.append((jsf.name, jsf.read_text(errors="ignore"), source_by_file.get(jsf.name, "")))
        except Exception:
            pass

    source_map_sources = set()
    source_map_extracted = []
    source_extract_dir = maps_dir / "sources"
    if list(maps_dir.glob("*.map")):
        info("Analyzing exposed source map sources/content...")
        source_extract_dir.mkdir(exist_ok=True)
        for map_file in maps_dir.glob("*.map"):
            try:
                data = json.loads(map_file.read_text(errors="ignore"))
                sources = data.get("sources") or []
                source_root = data.get("sourceRoot") or ""
                sources_content = data.get("sourcesContent") or []
                for idx, src in enumerate(sources):
                    src_name = f"{source_root}{src}" if source_root else src
                    source_map_sources.add(src_name)
                    if idx < len(sources_content) and sources_content[idx]:
                        safe_base = re.sub(r'[^A-Za-z0-9_.-]+', '_', os.path.basename(src) or 'source.txt')[:80]
                        if not safe_base.lower().endswith((".js", ".mjs", ".jsx", ".ts", ".tsx", ".txt")):
                            safe_base += ".txt"
                        out_src = source_extract_dir / f"{hashlib.md5((map_file.name + src).encode()).hexdigest()[:10]}_{safe_base}"
                        out_src.write_text(sources_content[idx], errors="ignore")
                        label = f"sourcemap:{map_file.name}:{src_name}"
                        analysis_blobs.append((label, sources_content[idx], ""))
                        source_map_extracted.append(f"{src_name}\t{out_src}")
            except Exception as e:
                warn(f"Could not parse source map {map_file.name}: {e}")
        if source_map_sources:
            (js_dir / "source_map_sources.txt").write_text("\n".join(sorted(source_map_sources)) + "\n")
            ok(f"Source map source paths: {len(source_map_sources)}")
        if source_map_extracted:
            (maps_dir / "source_map_extracted_files.txt").write_text("\n".join(source_map_extracted) + "\n")
            ok(f"Extracted source map source files: {len(source_map_extracted)}")

    def bump(label, amount=1):
        priority_scores[label] = priority_scores.get(label, 0) + amount

    def clean_candidate(value):
        value = (value or "").replace("\\/", "/").replace("\\u002F", "/").replace("\\u002f", "/")
        value = value.strip().strip('"\'`),;')
        return value

    def add_endpoint(value, label):
        value = clean_candidate(value)
        if len(value) < 3 or value.lower().endswith(ignore_exts):
            return
        if value.startswith(("http://", "https://")):
            all_absolute_urls.add(value)
        elif value.startswith("/") or any(x in value.lower() for x in ("api/", "graphql", "oauth", "sso", "auth", "admin")):
            all_endpoints.add(value)
        if any(kw in value.lower() for kw in ["admin", "internal", "debug", "graphql", "token", "secret", "config", "oauth", "sso", "auth"]):
            bump(label, 3)

    sink_patterns = [
        ("DOM HTML sink", r"\b(?:innerHTML|outerHTML|insertAdjacentHTML|document\.write|dangerouslySetInnerHTML)\b"),
        ("Code execution sink", r"\b(?:eval|Function)\s*\(|set(?:Timeout|Interval)\s*\(\s*['\"`]") ,
        ("Wildcard postMessage", r"\.postMessage\s*\([^,]+,\s*['\"]\*['\"]"),
        ("Message listener", r"addEventListener\s*\(\s*['\"]message['\"]"),
        ("Client redirect sink", r"(?:window\.)?location\.(?:href|assign|replace)\s*[=(]"),
        ("Prototype pollution keyword", r"(?:__proto__|constructor\.prototype|prototype\[)") ,
    ]

    for label, content, base_url in analysis_blobs:
        for pat in endpoint_patterns:
            for m in re.finditer(pat, content, flags=re.I):
                add_endpoint(m.group(1) if m.lastindex else m.group(), label)

        for m in re.finditer(r"fetch\s*\(\s*(['\"`])([^'\"`]{3,})\1(?P<tail>.{0,500})", content, flags=re.I | re.S):
            url = clean_candidate(m.group(2))
            method_m = re.search(r"method\s*:\s*['\"]([A-Z]+)['\"]", m.group('tail'), flags=re.I)
            method = method_m.group(1).upper() if method_m else "GET"
            api_calls.append({"file": label, "method": method, "url": url, "source": base_url})
            add_endpoint(url, label)
            bump(label, 1)

        for m in re.finditer(r"axios\.(get|post|put|patch|delete|head|options)\s*\(\s*(['\"`])([^'\"`]{3,})\2", content, flags=re.I):
            method = m.group(1).upper()
            url = clean_candidate(m.group(3))
            api_calls.append({"file": label, "method": method, "url": url, "source": base_url})
            add_endpoint(url, label)
            bump(label, 1)

        for m in re.finditer(r"axios\s*\(\s*\{(?P<body>.{0,800}?)\}\s*\)", content, flags=re.I | re.S):
            body = m.group('body')
            url_m = re.search(r"url\s*:\s*['\"]([^'\"]{3,})['\"]", body, flags=re.I)
            method_m = re.search(r"method\s*:\s*['\"]([A-Z]+)['\"]", body, flags=re.I)
            if url_m:
                url = clean_candidate(url_m.group(1))
                method = method_m.group(1).upper() if method_m else "GET"
                api_calls.append({"file": label, "method": method, "url": url, "source": base_url})
                add_endpoint(url, label)
                bump(label, 1)

        for m in re.finditer(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)?\s*(?:\([^)]*\))?\s*\{", content):
            snippet = content[m.start():m.start()+500].replace("\n", " ")
            graphql_ops.append({"file": label, "type": m.group(1), "name": m.group(2) or "anonymous", "snippet": snippet[:500]})
            bump(label, 3 if m.group(1) == "mutation" else 2)

        for m in re.finditer(r"(?:gql|graphql)\s*`([^`]{20,1200})`", content, flags=re.I | re.S):
            snippet = m.group(1).replace("\n", " ")[:500]
            op_m = re.search(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)?", snippet)
            graphql_ops.append({"file": label, "type": op_m.group(1) if op_m else "graphql", "name": (op_m.group(2) if op_m and op_m.group(2) else "anonymous"), "snippet": snippet})
            bump(label, 3)

        for pat in [
            r"<Route[^>]+path=['\"]([^'\"]+)['\"]",
            r"path\s*:\s*['\"](/[^'\"]*)['\"]",
            r"router\.(?:push|replace)\s*\(\s*['\"]([^'\"]+)['\"]",
            r"navigate\s*\(\s*['\"]([^'\"]+)['\"]",
        ]:
            for m in re.finditer(pat, content, flags=re.I):
                route = clean_candidate(m.group(1))
                if route and not route.lower().endswith(ignore_exts):
                    client_routes.add(route)

        for m in re.finditer(r"(?:localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)\s*\(\s*['\"]([^'\"]+)['\"]", content):
            storage_keys.add(f"{m.group(1)}\t{label}")
            bump(label, 1)
        if "document.cookie" in content:
            storage_keys.add(f"document.cookie\t{label}")
            bump(label, 1)

        for m in re.finditer(r"([A-Za-z0-9_]*(?:api|auth|sso|oauth|client|tenant|realm|issuer|audience|environment|base)[A-Za-z0-9_]*)\s*[:=]\s*['\"]([^'\"]{3,})['\"]", content, flags=re.I):
            interesting_config.add(f"{m.group(1)} = {m.group(2)}\t{label}")
            bump(label, 2)
        for m in re.finditer(r"\b(?:is|has|enable|allow)[A-Z][A-Za-z0-9_]*(?:Admin|Debug|Beta|Internal|Experimental|Feature|Bypass)[A-Za-z0-9_]*\b", content):
            interesting_config.add(f"feature_flag = {m.group()}\t{label}")
            bump(label, 1)

        for sink_name, pat in sink_patterns:
            for m in re.finditer(pat, content, flags=re.I):
                context = content[max(0, m.start()-80):m.end()+120].replace("\n", " ")[:260]
                dangerous_sinks.append({"file": label, "type": sink_name, "match": m.group()[:120], "context": context})
                bump(label, 2 if sink_name in ("Wildcard postMessage", "Code execution sink") else 1)

    def unique_dict_rows(rows, keys):
        seen = set()
        unique = []
        for row in rows:
            marker = tuple(row.get(k, "") for k in keys)
            if marker in seen:
                continue
            seen.add(marker)
            unique.append(row)
        return unique

    api_calls = unique_dict_rows(api_calls, ["method", "url", "file"])
    graphql_ops = unique_dict_rows(graphql_ops, ["type", "name", "snippet", "file"])
    dangerous_sinks = unique_dict_rows(dangerous_sinks, ["type", "match", "file", "context"])

    if all_endpoints:
        (ep_dir / "js_extracted_endpoints.txt").write_text("\n".join(sorted(all_endpoints)) + "\n")
        ok(f"Endpoints extracted from JS/source maps: {len(all_endpoints)}")
    if all_absolute_urls:
        (ep_dir / "js_absolute_urls.txt").write_text("\n".join(sorted(all_absolute_urls)) + "\n")
        ok(f"Absolute URLs extracted from JS/source maps: {len(all_absolute_urls)}")
        for url in sorted(all_absolute_urls):
            if any(kw in url.lower() for kw in ["api", "auth", "admin", "internal", "graphql", "token", "config"]):
                hit(f"Interesting absolute URL in JS: {url}")
    if api_calls:
        with open(js_dir / "js_api_calls.json", "w") as f:
            json.dump(api_calls, f, indent=2)
        (ep_dir / "js_api_calls.txt").write_text("\n".join(f"{r['method']} {r['url']} [{r['file']}]" for r in api_calls) + "\n")
        ok(f"JS API calls cataloged: {len(api_calls)}")
    if graphql_ops:
        with open(js_dir / "graphql_operations.json", "w") as f:
            json.dump(graphql_ops, f, indent=2)
        (js_dir / "graphql_operations.txt").write_text("\n".join(f"{r['type']} {r['name']} [{r['file']}] {r['snippet']}" for r in graphql_ops) + "\n")
        hit(f"GraphQL operations found in JS: {len(graphql_ops)}")
    if client_routes:
        (js_dir / "client_routes.txt").write_text("\n".join(sorted(client_routes)) + "\n")
        ok(f"Client-side routes found: {len(client_routes)}")
    if storage_keys:
        (js_dir / "storage_keys.txt").write_text("\n".join(sorted(storage_keys)) + "\n")
        ok(f"Storage/cookie keys found: {len(storage_keys)}")
    if interesting_config:
        (js_dir / "interesting_config.txt").write_text("\n".join(sorted(interesting_config)) + "\n")
        ok(f"Interesting config values found: {len(interesting_config)}")
    if dangerous_sinks:
        with open(js_dir / "client_attack_surface.json", "w") as f:
            json.dump(dangerous_sinks, f, indent=2)
        (js_dir / "client_attack_surface.txt").write_text("\n".join(f"[{r['type']}] {r['file']} :: {r['context']}" for r in dangerous_sinks[:1000]) + "\n")
        warn(f"Client-side attack-surface sinks found: {len(dangerous_sinks)}")
    if priority_scores:
        ranked = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
        (js_dir / "js_priority_files.txt").write_text("\n".join(f"{score}\t{name}" for name, score in ranked[:200]) + "\n")
        hit(f"Priority JS files to review: {len(ranked[:200])} -> js/js_priority_files.txt")

    for ep in sorted(all_endpoints):
        for kw in ["admin", "internal", "debug", "export", "import", "config", "backup", "token", "secret", "key", "graphql", "oauth", "sso", "auth"]:
            if kw in ep.lower():
                hit(f"Interesting endpoint in JS: {ep}")
                break

    # Secret scanning — also scan extracted source map sources and config files
    total_secrets = 0
    findings = {}

    if AI_CONFIG.get("only"):
        info("AI-only mode: skipping regex secret scanning")
    else:
        extra_scan_dirs = []
        if maps_dir.exists():
            sources_dir = maps_dir / "sources"
            if sources_dir.exists():
                extra_scan_dirs.append(str(sources_dir))
        info(f"Scanning JS files for secrets ({len(SECRET_PATTERNS)} patterns + entropy analysis, {len(extra_scan_dirs)} extra dir(s))...")
        findings = scan_js_secrets(str(files_dir), secrets_dir, extra_dirs=extra_scan_dirs)
        total_secrets = sum(len(v["matches"]) for v in findings.values())

        if total_secrets > 0:
            hit(f"SECRETS FOUND: {total_secrets} items across {len(findings)} pattern types")
            for name, data in findings.items():
                if data["severity"] in ("CRITICAL", "HIGH"):
                    hit(f"  [{data['severity']}] {name}: {len(data['matches'])} occurrences")
        else:
            ok("No secrets found in JS files")

        # Generate per-file findings report
        info("Generating per-file JS findings report...")
        report_path = generate_js_findings_report(str(js_dir), str(secrets_dir), findings)
        if report_path:
            hit(f"Per-file findings report: {report_path}")

    # ── AI-powered secret scan (optional) ──
    ai_findings = []
    if AI_CONFIG.get("enabled"):
        info("AI-powered secret scanning enabled — running LLM analysis on JS files...")
        ai_findings = ai_scan_js_secrets(str(files_dir), str(maps_dir), str(secrets_dir))
        if ai_findings:
            total_secrets += len(ai_findings)
            hit(f"AI scan found {len(ai_findings)} secret(s)")

    return total_secrets, len(map_found)

# ─────────────────────────────────────────────────────────────
# PHASE 8 — GRAPHQL DETECTION & INTROSPECTION
# ─────────────────────────────────────────────────────────────
GRAPHQL_PATHS = [
    "/graphql", "/graphiql", "/v1/graphql", "/v2/graphql",
    "/api/graphql", "/api/v1/graphql", "/query", "/gql",
    "/graphql/console", "/altair", "/playground",
    "/__graphql", "/graphql/v1", "/graphql/api",
    "/graphql-explorer", "/graphql/schema",
]

INTROSPECTION_QUERY = '{"query":"{ __schema { types { name fields { name } } } }"}'

def phase_graphql(target, out):
    ph("PHASE 8: GRAPHQL DETECTION & INTROSPECTION")
    gql_dir = out / "graphql"
    web_dir = out / "web"
    ep_dir  = out / "endpoints"
    gql_dir.mkdir(exist_ok=True)

    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls:
        live_urls = [f"https://{target}", f"http://{target}"]

    found_endpoints = []

    # Probe common GraphQL paths on all live hosts
    info("Probing GraphQL endpoints on all live hosts...")
    def probe_gql(args):
        base, path = args
        url = base.rstrip("/") + path
        try:
            req = urllib.request.Request(url, method="POST",
                data=INTROSPECTION_QUERY.encode(),
                headers={"Content-Type": "application/json",
                         "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read().decode("utf-8", errors="ignore")
                if r.status == 200 and ("__schema" in body or "data" in body):
                    return (url, body, True)  # introspection enabled
                elif r.status == 200:
                    return (url, body, False)  # endpoint exists but no introspection
        except urllib.error.HTTPError as e:
            if e.code in (400, 405):
                # GraphQL endpoint exists but rejected our query format
                return (url, "", False)
        except:
            pass
        return None

    targets = [(base, path) for base in live_urls[:15] for path in GRAPHQL_PATHS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(probe_gql, targets))

    for r in results:
        if r is None:
            continue
        url, body, introspection = r
        found_endpoints.append(url)
        if introspection:
            hit(f"GRAPHQL INTROSPECTION ENABLED: {url}")
            safe = hashlib.md5(url.encode()).hexdigest()[:8]
            (gql_dir / f"introspection_{safe}.json").write_text(body)
        else:
            ok(f"GraphQL endpoint found (introspection disabled): {url}")

    # Also scan JS-extracted endpoints for graphql references
    js_eps = read_lines(ep_dir / "js_extracted_endpoints.txt")
    for ep in js_eps:
        if "graphql" in ep.lower() or "gql" in ep.lower():
            hit(f"GraphQL reference in JS: {ep}")
            found_endpoints.append(ep)

    if found_endpoints:
        (gql_dir / "graphql_endpoints.txt").write_text("\n".join(sorted(set(found_endpoints))))
        ok(f"GraphQL endpoints found: {len(set(found_endpoints))}")

        # Extract types/fields from introspection results
        info("Extracting schema types from introspection data...")
        for schema_file in gql_dir.glob("introspection_*.json"):
            try:
                data = json.loads(schema_file.read_text())
                types = data.get("data", {}).get("__schema", {}).get("types", [])
                interesting = [t for t in types if not t["name"].startswith("__")]
                if interesting:
                    type_names = [t["name"] for t in interesting]
                    (gql_dir / "schema_types.txt").write_text("\n".join(sorted(type_names)))
                    hit(f"Schema has {len(interesting)} custom types — check graphql/schema_types.txt")
                    # Flag sensitive types
                    for t in interesting:
                        name_l = t["name"].lower()
                        if any(kw in name_l for kw in ["user", "admin", "auth", "token", "secret", "payment", "order", "credential", "session", "permission", "role"]):
                            fields = [f["name"] for f in (t.get("fields") or [])]
                            hit(f"  Sensitive type: {t['name']} → fields: {', '.join(fields[:10])}")
            except:
                pass
    else:
        ok("No GraphQL endpoints discovered")

    # Nuclei GraphQL scan if available
    if check_tool("nuclei") and found_endpoints:
        info("nuclei — GraphQL-specific vulnerability scan...")
        gql_targets = gql_dir / "graphql_endpoints.txt"
        run(f"nuclei -l {gql_targets} -tags graphql -silent -o {gql_dir}/nuclei_graphql.txt", timeout=180)
        gql_vulns = count_lines(gql_dir / "nuclei_graphql.txt")
        if gql_vulns > 0:
            hit(f"GraphQL vulnerabilities: {gql_vulns} findings!")

    return len(found_endpoints)

# ─────────────────────────────────────────────────────────────
# PHASE 9 — API FUZZING
# ─────────────────────────────────────────────────────────────
API_WORDLIST_PATHS = [
    "/opt/SecLists/Discovery/Web-Content/api/api-endpoints.txt",
    "/opt/SecLists/Discovery/Web-Content/api/api-seen-in-wild.txt",
    "/opt/SecLists/Discovery/Web-Content/common-api-endpoints-mazen160.txt",
    "/opt/SecLists/Discovery/Web-Content/raft-medium-words.txt",
]

def phase_api_fuzz(target, out):
    ph("PHASE 9: API FUZZING & ENDPOINT DISCOVERY")
    api_dir = out / "api"
    web_dir = out / "web"
    ep_dir  = out / "endpoints"
    api_dir.mkdir(exist_ok=True)

    live_urls = read_lines(web_dir / "live_urls.txt")
    if not live_urls:
        live_urls = [f"https://{target}"]

    # ── API version path discovery ──
    info("Probing common API base paths...")
    api_bases = [
        "/api", "/api/v1", "/api/v2", "/api/v3", "/v1", "/v2", "/v3",
        "/rest", "/rest/v1", "/rest/v2", "/api/internal", "/api/admin",
        "/api/private", "/api/public", "/_api", "/api/latest",
        "/api-docs", "/swagger.json", "/openapi.json", "/swagger/v1/swagger.json",
        "/redoc", "/docs", "/api/docs", "/api/swagger",
    ]
    found_apis = []
    def probe_api(args):
        base, path = args
        url = base.rstrip("/") + path
        body, code = fetch_url(url, timeout=10)
        if code in (200, 301, 302, 401, 403):
            return (url, code)
        return None

    probe_targets = [(base, path) for base in live_urls[:10] for path in api_bases]
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(probe_api, probe_targets))

    for r in results:
        if r is None:
            continue
        url, code = r
        found_apis.append(url)
        if code == 200:
            if "swagger" in url.lower() or "openapi" in url.lower():
                hit(f"SWAGGER/OPENAPI SPEC FOUND: {url}")
            else:
                ok(f"API path alive [{code}]: {url}")
        elif code == 401:
            hit(f"API requires auth [{code}]: {url} — try token bypass!")
        elif code == 403:
            warn(f"API forbidden [{code}]: {url} — try 403 bypass")

    if found_apis:
        (api_dir / "found_api_paths.txt").write_text("\n".join(sorted(set(found_apis))))
        ok(f"API paths discovered: {len(set(found_apis))}")

    # ── ffuf API endpoint fuzzing ──
    if check_tool("ffuf"):
        # Pick best available wordlist
        wordlist = None
        for wl in API_WORDLIST_PATHS:
            if os.path.exists(wl):
                wordlist = wl
                break

        if wordlist:
            info(f"ffuf API fuzzing (wordlist: {os.path.basename(wordlist)})...")
            for base in live_urls[:5]:
                safe = hashlib.md5(base.encode()).hexdigest()[:8]
                # Fuzz /api/FUZZ
                run(f"ffuf -u '{base.rstrip('/')}/api/FUZZ' -w {wordlist} -mc 200,201,301,302,401,403,405 -t 50 -sf -s -o {api_dir}/ffuf_api_{safe}.json -of json 2>/dev/null", timeout=180)
                # Fuzz /FUZZ (top-level API routes)
                run(f"ffuf -u '{base.rstrip('/')}/FUZZ' -w {wordlist} -mc 200,201,301,302,401,403,405 -t 50 -sf -s -o {api_dir}/ffuf_root_{safe}.json -of json 2>/dev/null", timeout=180)
            ok("ffuf API fuzzing complete")

            # Parse ffuf results for hits
            total_hits = 0
            for fuzz_result in api_dir.glob("ffuf_*.json"):
                try:
                    data = json.loads(fuzz_result.read_text())
                    results_list = data.get("results", [])
                    total_hits += len(results_list)
                    for r in results_list:
                        status = r.get("status", 0)
                        fuzz_url = r.get("url", "")
                        if status in (200, 201):
                            hit(f"API endpoint [{status}]: {fuzz_url}")
                        elif status in (401, 403):
                            warn(f"Protected API [{status}]: {fuzz_url}")
                except:
                    pass
            ok(f"ffuf total hits: {total_hits}")
        else:
            warn("No API wordlist found — install SecLists: /opt/SecLists/")

    # ── HTTP method fuzzing on discovered API endpoints ──
    info("HTTP method fuzzing on discovered API paths...")
    methods_tested = 0
    for api_url in found_apis[:20]:
        for method in ["PUT", "DELETE", "PATCH", "OPTIONS"]:
            try:
                req = urllib.request.Request(api_url, method=method,
                    headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    if r.status in (200, 201, 204):
                        hit(f"Method {method} accepted: {api_url}")
                        append_file(str(api_dir / "method_allowed.txt"), f"{method} {api_url}")
            except urllib.error.HTTPError as e:
                if e.code == 405:
                    pass  # Method not allowed — normal
                elif e.code in (200, 201, 204, 401):
                    warn(f"Method {method} returned {e.code}: {api_url}")
            except:
                pass
            methods_tested += 1
    ok(f"HTTP method fuzzing done ({methods_tested} tests)")

    return len(found_apis)

# ─────────────────────────────────────────────────────────────
# PHASE 10 — GOOGLE DORK GENERATION
# ─────────────────────────────────────────────────────────────
def phase_dorks(target, out):
    ph("PHASE 10: GOOGLE DORK GENERATION")
    dorks_dir = out / "dorks"
    dorks_dir.mkdir(exist_ok=True)

    dorks = f"""# ====================================================================
# BugHunter Pro — Google Dorks for: {target}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Usage: Paste each into Google/Bing browser manually
# ====================================================================

# ===== SENSITIVE FILES =====
site:{target} ext:env | ext:log | ext:conf | ext:cnf | ext:ini | ext:sh | ext:bak | ext:backup
site:{target} ext:sql | ext:db | ext:sqlite | ext:dbf | ext:dump | ext:mdb
site:{target} ext:zip | ext:tar | ext:gz | ext:rar | ext:7z | ext:tgz
site:{target} ext:pem | ext:key | ext:crt | ext:csr | ext:der | ext:pfx | ext:p12
site:{target} filetype:log "error" | "exception" | "stack trace" | "password" | "token"
site:{target} filetype:txt "password" | "passwd" | "api_key" | "secret" | "token" | "credential"
site:{target} "index of" "/.git" | "/backup" | "/config" | "/private" | "/secret" | "/admin"
site:{target} ext:php.bak | ext:asp.bak | ext:aspx.bak | ext:conf.bak | ext:yml.bak
site:{target} ext:xml | ext:yaml | ext:yml | ext:toml | ext:properties intitle:"config"
site:{target} filetype:pdf intitle:"confidential" | intitle:"internal" | intitle:"restricted"
site:{target} "DB_PASSWORD" | "DB_USER" | "DATABASE_URL" | "MYSQL_ROOT_PASSWORD"
site:{target} "SECRET_KEY" | "SECRET_KEY_BASE" | "APP_SECRET" | "APP_KEY"
site:{target} intitle:"index of" intext:".env"

# ===== ADMIN & CONTROL PANELS =====
site:{target} inurl:admin | inurl:administrator | inurl:wp-admin | inurl:panel | inurl:dashboard
site:{target} inurl:login | inurl:signin | inurl:auth | inurl:sso | inurl:oauth | inurl:saml
site:{target} intitle:"admin" | intitle:"administrator" | intitle:"admin panel" | intitle:"control panel"
site:{target} inurl:jenkins | inurl:grafana | inurl:kibana | inurl:jira | inurl:confluence | inurl:gitlab
site:{target} inurl:phpmyadmin | inurl:adminer | inurl:phpinfo | inurl:cpanel | inurl:webmail
site:{target} inurl:console | inurl:management | inurl:portal | inurl:backend | inurl:internal
site:{target} intitle:"Grafana" | intitle:"Kibana" | intitle:"Elasticsearch" | intitle:"Prometheus"
site:{target} intitle:"Jupyter" | intitle:"Apache Airflow" | intitle:"Metabase" | intitle:"Superset"
site:{target} intitle:"GitLab" | intitle:"Jenkins" | intitle:"SonarQube" | intitle:"Nexus"
site:{target} intitle:"Portainer" | intitle:"Traefik" | intitle:"RabbitMQ" | intitle:"Redis"
site:{target} intitle:"phpMyAdmin" | intitle:"Adminer" | intitle:"pgAdmin" | intitle:"MongoDB"
site:{target} inurl:"/wp-admin" | inurl:"/wp-login.php" | inurl:"/administrator/" | inurl:"/admin.php"
site:{target} intitle:"kubernetes" | intitle:"k8s" | intitle:"docker" | intitle:"rancher"
site:{target} intitle:"Struts" | intitle:"Spring Boot" | intitle:"Tomcat" | intitle:"WebLogic"

# ===== API, SWAGGER & GRAPHQL =====
site:{target} inurl:api | inurl:swagger | inurl:api-docs | inurl:openapi | inurl:graphql
site:{target} inurl:"/api/v1" | inurl:"/api/v2" | inurl:"/api/v3" | inurl:"/v1/" | inurl:"/v2/"
site:{target} inurl:swagger-ui | inurl:api-explorer | inurl:redoc | inurl:stoplight
site:{target} intitle:"swagger" | intitle:"api documentation" | intitle:"rest api"
site:{target} inurl:"/graphql" | inurl:"/graphiql" | inurl:"/__graphql" | inurl:"/playground"
site:{target} inurl:webhook | inurl:webhooks | inurl:callback | inurl:callbacks
site:{target} filetype:json "swagger" | "openapi" | "paths" | "definitions"
site:{target} inurl:postman | filetype:json "postman_collection"
site:{target} inurl:"/api-docs" | inurl:"/api/swagger" | inurl:"/docs/api"

# ===== ERROR & DEBUG INFO =====
site:{target} inurl:"error" | intitle:"exception" | intitle:"failure" | "database error"
site:{target} "SQL syntax" | "SQL error" | "mysql_fetch" | "ORA-" | "PostgreSQL" | "SQLite"
site:{target} "undefined index" | "unhandled exception" | "stack trace" | "Traceback"
site:{target} "PHP Parse error" | "PHP Warning" | "PHP Notice" | "PHP Fatal error"
site:{target} "Error 500" | "Internal Server Error" | "Application Error" | "Whoops!"
site:{target} intitle:"error" "token" | "api_key" | "secret" | "password" | "database"
site:{target} "debug" inurl:debug | inurl:test | inurl:dev | inurl:staging
site:{target} "access_token" | "bearer" | "api_key" ext:json | ext:log
site:{target} "Warning: mysql_connect()" | "Warning: pg_connect()"
site:{target} "ORA-01756" | "ORA-00933" | "Microsoft OLE DB" | "ADODB.Field error"

# ===== OPEN REDIRECT & SSRF PARAMS =====
site:{target} inurl:url= | inurl:return= | inurl:next= | inurl:redirect= | inurl:redir=
site:{target} inurl:r2= | inurl:page= | inurl:target= | inurl:dest= | inurl:destination= | inurl:go=
site:{target} inurl:forward= | inurl:location= | inurl:out= | inurl:view= | inurl:from=
site:{target} inurl:fetch= | inurl:load= | inurl:file= | inurl:path= | inurl:uri= | inurl:href=
site:{target} inurl:proxy= | inurl:preview= | inurl:embed= | inurl:import= | inurl:export=
site:{target} inurl:callback= | inurl:src= | inurl:source= | inurl:include= | inurl:template=
site:{target} inurl:open= | inurl:host= | inurl:domain= | inurl:link= | inurl:jump=

# ===== SQL INJECTION PRONE =====
site:{target} inurl:q= | inurl:s= | inurl:search= | inurl:query= | inurl:keyword= | inurl:lang=
site:{target} inurl:id= | inurl:pid= | inurl:uid= | inurl:user_id= | inurl:account= | inurl:no=
site:{target} inurl:select= | inurl:report= | inurl:role= | inurl:filter= | inurl:cat= | inurl:type=
site:{target} inurl:cmd= | inurl:exec= | inurl:execute= | inurl:run= | inurl:command=
site:{target} inurl:order= | inurl:sort= | inurl:group= | inurl:where= | inurl:column=
site:{target} inurl:update= | inurl:delete= | inurl:remove= | inurl:modify= | inurl:edit=
site:{target} inurl:item= | inurl:product= | inurl:view= | inurl:detail= | inurl:show=

# ===== CLOUD & INFRASTRUCTURE =====
site:{target} "s3.amazonaws.com" | "s3-" | "storage.googleapis.com" | "blob.core.windows.net"
site:{target} "firebaseio.com" | "firebase.google.com" | "appspot.com"
site:{target} "herokuapps.com" | "herokuapp.com" | "azurewebsites.net" | "cloudfront.net"
site:{target} "amazonaws.com" "AKIA" | "ASIA" | "AROA"
"{target}" site:amazonaws.com | site:storage.googleapis.com | site:blob.core.windows.net
"{target}" "bucket" | "s3" | "storage" site:pastebin.com | site:github.com | site:gitlab.com
site:{target} inurl:".aws" | inurl:".gcp" | inurl:".azure" | inurl:"cloud-config"

# ===== SOURCE CODE LEAKS =====
"{target}" site:github.com | site:gitlab.com | site:bitbucket.org
"{target}" site:github.com password | secret | api_key | token | credential | config
"{target}" site:github.com ".env" | "config.php" | "settings.py" | "application.yml"
"{target}" site:github.com "internal" | "staging" | "production" | "dev" password
"{target}" site:pastebin.com | site:paste.org | site:justpaste.it | site:hastebin.com
"{target}" site:trello.com | site:notion.so | site:airtable.com "password" | "api_key"
"{target}" site:jsfiddle.net | site:codepen.io "api_key" | "secret"
"{target}" site:gist.github.com "password" | "token" | "secret"
"{target}" site:repl.it | site:glitch.com | site:codesandbox.io

# ===== SUBDOMAIN DISCOVERY =====
site:*.{target} -site:www.{target}
site:*.{target} inurl:dev | inurl:staging | inurl:test | inurl:internal | inurl:beta
site:*.{target} inurl:admin | inurl:api | inurl:mail | inurl:vpn | inurl:remote
site:*.{target} intitle:"index of" | intitle:"apache" | intitle:"IIS" | intitle:"nginx"
site:*.{target} ext:php | ext:asp | ext:jsp | ext:aspx | ext:cgi | ext:cfm
related:{target} -site:{target}

# ===== GITHUB DORKS (search on github.com/search) =====
org:{target.split('.')[0]} password
org:{target.split('.')[0]} api_key OR apikey OR api_secret
org:{target.split('.')[0]} "BEGIN RSA PRIVATE KEY"
org:{target.split('.')[0]} ".env"
org:{target.split('.')[0]} "config.php" password
org:{target.split('.')[0]} "settings.py" SECRET_KEY
org:{target.split('.')[0]} "database.yml" password
org:{target.split('.')[0]} "credentials" OR "credential"
org:{target.split('.')[0]} "AKIA" aws
org:{target.split('.')[0]} staging OR internal
org:{target.split('.')[0]} "firebaseio.com" databaseURL
org:{target.split('.')[0]} "Authorization: Bearer"
org:{target.split('.')[0]} "client_secret"
org:{target.split('.')[0]} filename:.env
org:{target.split('.')[0]} filename:config.json password
org:{target.split('.')[0]} filename:*.pem
org:{target.split('.')[0]} extension:sql "INSERT INTO" "password"
"""

    (dorks_dir / "google_dorks.txt").write_text(dorks)
    ok(f"Google dorks saved: dorks/google_dorks.txt")
    info("Open dorks/google_dorks.txt and paste each into Google/Bing/GitHub manually")

# ─────────────────────────────────────────────────────────────
# PHASE 11 — VULNERABILITY SCANNING
# ─────────────────────────────────────────────────────────────
def phase_vulns(target, out):
    ph("PHASE 11: VULNERABILITY SCANNING")
    vulns_dir = out / "vulns"
    web_dir   = out / "web"
    dns_dir   = out / "dns"
    vulns_dir.mkdir(exist_ok=True)

    if not check_tool("nuclei"):
        warn("nuclei not found, skipping automated vuln scan")
        return

    # Update templates
    info("Updating nuclei templates...")
    run("nuclei -update-templates -silent", timeout=120)

    live_urls = web_dir / "live_urls.txt"
    if not live_urls.exists() or count_lines(live_urls) == 0:
        warn("No live URLs found — creating fallback target list for nuclei")
        live_urls.write_text(f"https://{target}\nhttp://{target}\nhttps://www.{target}\n")
        ok(f"Using fallback targets: {target}, www.{target}")

    scans = [
        ("CVEs (high/critical)",    f"nuclei -l {live_urls} -tags cve -severity high,critical -silent -o {vulns_dir}/nuclei_cve.txt"),
        ("Exposed panels",          f"nuclei -l {live_urls} -tags exposed-panels -silent -o {vulns_dir}/nuclei_panels.txt"),
        ("Default credentials",     f"nuclei -l {live_urls} -tags default-logins -silent -o {vulns_dir}/nuclei_default_creds.txt"),
        ("Misconfigurations",       f"nuclei -l {live_urls} -tags misconfig -silent -o {vulns_dir}/nuclei_misconfig.txt"),
        ("Tokens/secrets",          f"nuclei -l {live_urls} -tags token -silent -o {vulns_dir}/nuclei_tokens.txt"),
        ("Exposed files",           f"nuclei -l {live_urls} -tags exposure -silent -o {vulns_dir}/nuclei_exposure.txt"),
        ("Tech detect",             f"nuclei -l {live_urls} -tags tech -silent -o {vulns_dir}/nuclei_tech.txt"),
        ("CORS misconfig",          f"nuclei -l {live_urls} -tags cors -silent -o {vulns_dir}/nuclei_cors.txt"),
    ]

    for name, cmd in scans:
        info(f"nuclei — {name}...")
        run(cmd, timeout=300)

    # Report counts
    for name, cmd in scans:
        fname = vulns_dir / (cmd.split("-o ")[1].split()[0].split("/")[-1])
        count = count_lines(fname)
        if count > 0:
            hit(f"nuclei [{name}]: {count} findings → {fname.name}")
        else:
            ok(f"nuclei [{name}]: 0 findings")

    # Subdomain takeover
    if check_tool("subzy"):
        info("subzy — subdomain takeover detection...")
        run(f"subzy run --targets {dns_dir}/resolved.txt --concurrency 100 --hide_fails > {vulns_dir}/subzy_results.txt", timeout=300)
        vuln_take = count_lines(vulns_dir / "subzy_results.txt")
        if vuln_take > 0:
            hit(f"SUBDOMAIN TAKEOVERS: {vuln_take} potential — check vulns/subzy_results.txt")

    # 403 bypass testing
    info("Testing 403 bypass techniques...")
    four03_hosts = read_lines(web_dir / "403_hosts.txt")
    for url in four03_hosts[:20]:
        # Path bypass
        for bypass in ["/%2f/", "/./", "//", "/.;/", "/%20/", "/%09/"]:
            body, code = fetch_url(url.rstrip("/") + bypass)
            if code == 200:
                hit(f"403 BYPASS (path): {url}{bypass}")
                append_file(str(vulns_dir / "403_bypasses.txt"), f"{url}{bypass}")

        # Header bypass
        for header, val in [
            ("X-Original-URL", "/"),
            ("X-Rewrite-URL", "/"),
            ("X-Custom-IP-Authorization", "127.0.0.1"),
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Originating-IP", "127.0.0.1"),
        ]:
            body, code = fetch_url(url, headers={header: val, "User-Agent": "Mozilla/5.0"})
            if code == 200:
                hit(f"403 BYPASS (header {header}): {url}")
                append_file(str(vulns_dir / "403_bypasses.txt"), f"[{header}] {url}")

    # ── CORS Misconfiguration Testing ──
    info("Testing CORS misconfigurations on live hosts...")
    cors_targets = read_lines(live_urls)[:30]
    evil_origins = [
        f"https://evil.com",
        f"https://{target}.evil.com",
        f"https://evil{target}",
        "null",
    ]
    for url in cors_targets:
        for origin in evil_origins:
            try:
                req = urllib.request.Request(url, headers={
                    "Origin": origin,
                    "User-Agent": "Mozilla/5.0"
                })
                resp = urllib.request.urlopen(req, timeout=8)
                acao = resp.headers.get("Access-Control-Allow-Origin", "")
                acac = resp.headers.get("Access-Control-Allow-Credentials", "")
                if acao == origin or (acao == "*" and acac.lower() == "true"):
                    hit(f"CORS MISCONFIG: {url} reflects origin={origin} credentials={acac}")
                    append_file(str(vulns_dir / "cors_misconfig.txt"), f"{url} | Origin: {origin} | ACAO: {acao} | ACAC: {acac}")
            except Exception:
                pass
    cors_count = count_lines(vulns_dir / "cors_misconfig.txt")
    if cors_count > 0:
        hit(f"CORS misconfigurations: {cors_count}")
    else:
        ok("No CORS misconfigurations found")

    # ── CRLF Injection Testing ──
    info("Testing CRLF injection on live hosts...")
    crlf_payloads = [
        "%0d%0aX-Injected:true",
        "%0aX-Injected:true",
        "%0d%0a%0d%0a<script>alert(1)</script>",
        "\\r\\nX-Injected:true",
        "%E5%98%8A%E5%98%8DX-Injected:true",
    ]
    for url in cors_targets:
        base = url.rstrip("/")
        for payload in crlf_payloads:
            try:
                test_url = f"{base}/{payload}"
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=8)
                if resp.headers.get("X-Injected"):
                    hit(f"CRLF INJECTION: {url} with payload {payload}")
                    append_file(str(vulns_dir / "crlf_injection.txt"), f"{url} | {payload}")
                    break
            except Exception:
                pass
    crlf_count = count_lines(vulns_dir / "crlf_injection.txt")
    if crlf_count > 0:
        hit(f"CRLF injections: {crlf_count}")
    else:
        ok("No CRLF injections found")

    # ── Open Redirect Validation ──
    info("Testing open redirects on parameter-bearing URLs...")
    redirect_targets = read_lines(out / "params" / "redirect_prone.txt")[:50]
    redirect_canary = "https://evil.com/redirect-test"
    for url in redirect_targets:
        # Replace the parameter value with our canary
        try:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for key in params:
                test_params = params.copy()
                test_params[key] = [redirect_canary]
                test_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(test_params, doseq=True)))
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=8)
                final_url = resp.geturl()
                if "evil.com" in final_url:
                    hit(f"OPEN REDIRECT: {url} → redirects to evil.com via param '{key}'")
                    append_file(str(vulns_dir / "open_redirects.txt"), f"{url} | param: {key}")
        except Exception:
            pass
    redir_count = count_lines(vulns_dir / "open_redirects.txt")
    if redir_count > 0:
        hit(f"Open redirects: {redir_count}")
    else:
        ok("No open redirects confirmed")

    # ── Host Header Injection ──
    info("Testing host header injection on live hosts...")
    for url in cors_targets[:15]:
        for evil_host in [f"evil.com", f"{target}.evil.com", "localhost"]:
            try:
                req = urllib.request.Request(url, headers={
                    "Host": evil_host,
                    "User-Agent": "Mozilla/5.0"
                })
                resp = urllib.request.urlopen(req, timeout=8)
                body_resp = resp.read(4096).decode("utf-8", errors="ignore")
                if evil_host in body_resp:
                    hit(f"HOST HEADER INJECTION: {url} reflects Host: {evil_host}")
                    append_file(str(vulns_dir / "host_header_injection.txt"), f"{url} | Host: {evil_host}")
                    break
            except Exception:
                pass
    hhi_count = count_lines(vulns_dir / "host_header_injection.txt")
    if hhi_count > 0:
        hit(f"Host header injections: {hhi_count}")
    else:
        ok("No host header injections found")

    # ── Dalfox XSS Scanning ──
    if check_tool("dalfox"):
        info("dalfox — reflected XSS scanning on parameter URLs...")
        params_dir = out / "params"
        # Feed injection-prone + ssrf-prone URLs to dalfox
        xss_input = vulns_dir / "dalfox_targets.txt"
        run(f"cat {params_dir}/injection_prone.txt {params_dir}/ssrf_prone.txt 2>/dev/null | sort -u | head -200 > {xss_input}")
        if count_lines(xss_input) > 0:
            run(f"dalfox file {xss_input} --silence --no-color --skip-bav --output {vulns_dir}/dalfox_xss.txt", timeout=600)
            xss_count = count_lines(vulns_dir / "dalfox_xss.txt")
            if xss_count > 0:
                hit(f"DALFOX XSS: {xss_count} potential XSS findings!")
            else:
                ok("dalfox: no reflected XSS found")
        else:
            ok("No parameter URLs for dalfox XSS scanning")
    else:
        info("Install dalfox for automated XSS scanning: go install github.com/hahwul/dalfox/v2@latest")

    # ── SQLMap on injection-prone params ──
    if check_tool("sqlmap"):
        info("sqlmap — testing top injection-prone URLs for SQLi...")
        inj_urls = read_lines(out / "params" / "injection_prone.txt")[:10]
        for url in inj_urls:
            safe = hashlib.md5(url.encode()).hexdigest()[:8]
            run(f"sqlmap -u '{url}' --batch --level=1 --risk=1 --smart --random-agent --output-dir={vulns_dir}/sqlmap_{safe} 2>/dev/null", timeout=120)
        ok("sqlmap scan complete — check vulns/sqlmap_* directories")
    else:
        info("Install sqlmap for automated SQL injection testing: apt install sqlmap")

# ─────────────────────────────────────────────────────────────
# PHASE 12 — CLOUD ASSETS
# ─────────────────────────────────────────────────────────────
def phase_cloud(target, out):
    ph("PHASE 12: CLOUD ASSET DISCOVERY")
    secrets_dir = out / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    base = target.split(".")[0]
    buckets = [
        target, target.replace(".", "-"), base,
        f"{base}-dev", f"{base}-prod", f"{base}-staging", f"{base}-backup",
        f"{base}-data", f"{base}-assets", f"{base}-static", f"{base}-uploads",
        f"{base}-files", f"{base}-media", f"{base}-images", f"{base}-logs",
        f"{base}-archive", f"{base}-test", f"{base}-www", f"{base}-web",
        f"{base}-admin", f"{base}-internal", f"{base}-private", f"{base}-public",
        f"www.{target}", f"cdn.{target}", f"static.{target}",
    ]

    info(f"Checking {len(buckets)} S3 bucket name permutations...")
    open_buckets = []
    for bucket in buckets:
        # Try direct HTTP access
        body, code = fetch_url(f"https://{bucket}.s3.amazonaws.com/", timeout=8)
        if code in (200, 301) and "<ListBucketResult" in body:
            hit(f"OPEN S3 BUCKET: {bucket}.s3.amazonaws.com")
            open_buckets.append(bucket)
            append_file(str(secrets_dir / "open_s3_buckets.txt"), bucket)
        elif code == 403:
            ok(f"S3 bucket exists but private: {bucket}")

        # Try via aws cli if available
        if check_tool("aws"):
            out_str, rc = run(f"aws s3 ls s3://{bucket} --no-sign-request 2>&1", timeout=10)
            if rc == 0 and out_str:
                hit(f"OPEN S3 BUCKET (aws cli): {bucket}")
                open_buckets.append(bucket)
                append_file(str(secrets_dir / "open_s3_buckets.txt"), bucket)

    ok(f"S3 check: {len(open_buckets)} open buckets found")

    # Firebase
    info("Checking Firebase database...")
    for fb_name in [base, f"{base}-default", f"{target.replace('.', '-')}"]:
        body, code = fetch_url(f"https://{fb_name}-default-rtdb.firebaseio.com/.json", timeout=8)
        if code == 200 and body not in ("null", ""):
            hit(f"OPEN FIREBASE DB: {fb_name}-default-rtdb.firebaseio.com")
            (secrets_dir / f"firebase_{fb_name}.json").write_text(body)
        elif code == 200 and body == "null":
            ok(f"Firebase exists but empty: {fb_name}")

    # GCP Storage
    info("Checking GCP Storage buckets...")
    for bucket in buckets[:10]:
        body, code = fetch_url(f"https://storage.googleapis.com/{bucket}/", timeout=8)
        if code == 200 and "<ListBucketResult" in body:
            hit(f"OPEN GCP BUCKET: {bucket}")
            append_file(str(secrets_dir / "open_gcp_buckets.txt"), bucket)

    # Azure Blob Storage
    info("Checking Azure Blob Storage containers...")
    azure_containers = ["images", "assets", "data", "backup", "files", "uploads",
                        "static", "media", "logs", "archive", "public", "private",
                        "web", "cdn", "$web", "documents"]
    azure_accounts = [base, f"{base}dev", f"{base}prod", f"{base}staging",
                      f"{base}storage", f"{base}data", f"{base}backup"]
    for account in azure_accounts:
        for container in azure_containers:
            body, code = fetch_url(f"https://{account}.blob.core.windows.net/{container}?restype=container&comp=list", timeout=5)
            if code == 200 and "<EnumerationResults" in body:
                hit(f"OPEN AZURE BLOB: {account}.blob.core.windows.net/{container}")
                append_file(str(secrets_dir / "open_azure_blobs.txt"), f"{account}/{container}")
            elif code == 404:
                pass  # Container doesn't exist
    azure_count = count_lines(secrets_dir / "open_azure_blobs.txt")
    if azure_count > 0:
        hit(f"Azure Blob: {azure_count} open containers found")
    else:
        ok("No open Azure Blob containers found")

    # DigitalOcean Spaces
    info("Checking DigitalOcean Spaces...")
    do_regions = ["nyc3", "sfo3", "ams3", "sgp1", "fra1"]
    for bucket in buckets[:8]:
        for region in do_regions:
            body, code = fetch_url(f"https://{bucket}.{region}.digitaloceanspaces.com/", timeout=5)
            if code == 200 and "<ListBucketResult" in body:
                hit(f"OPEN DO SPACE: {bucket}.{region}.digitaloceanspaces.com")
                append_file(str(secrets_dir / "open_do_spaces.txt"), f"{bucket}.{region}")

# ─────────────────────────────────────────────────────────────
# PHASE 13 — GITHUB SECRET SCANNING
# ─────────────────────────────────────────────────────────────
def phase_github(target, out):
    ph("PHASE 13: GITHUB SECRET SCANNING")
    secrets_dir = out / "secrets"
    dorks_dir   = out / "dorks"
    secrets_dir.mkdir(exist_ok=True)
    dorks_dir.mkdir(exist_ok=True)

    org = target.split(".")[0]

    # TruffleHog
    if check_tool("trufflehog"):
        info(f"TruffleHog scanning GitHub org: {org}...")
        run(f"trufflehog github --org={org} --only-verified 2>/dev/null > {secrets_dir}/trufflehog_github.txt", timeout=300)
        count = count_lines(secrets_dir / "trufflehog_github.txt")
        if count > 0:
            hit(f"TruffleHog: {count} verified secrets found!")
        else:
            ok("TruffleHog: no verified secrets")

    # gitleaks on any cloned repos
    if check_tool("gitleaks"):
        info("gitleaks scanning any cached repos...")
        run(f"gitleaks detect --source {out} --report-format json -r {secrets_dir}/gitleaks.json 2>/dev/null")

    # GitHub dorks output
    info("Generating GitHub search dorks...")
    gh_dorks = f"""# GitHub Dorks for: {target}
# Go to: https://github.com/search?q=DORK&type=code

org:{org} password
org:{org} api_key OR apikey OR api_secret
org:{org} secret_key OR client_secret
org:{org} "BEGIN RSA PRIVATE KEY" OR "BEGIN EC PRIVATE KEY"
org:{org} filename:.env
org:{org} filename:config.json password
org:{org} filename:database.yml password
org:{org} filename:settings.py SECRET_KEY
org:{org} filename:application.properties password
org:{org} filename:application.yml password
org:{org} filename:*.pem
org:{org} filename:*.ppk
org:{org} extension:sql "INSERT INTO" "password"
org:{org} "AKIA" aws OR amazon
org:{org} "Authorization: Bearer"
org:{org} "client_id" "client_secret"
org:{org} staging OR internal OR "do not commit"
org:{org} "firebaseio.com" databaseURL
org:{org} "DB_PASSWORD" OR "DATABASE_PASSWORD"
org:{org} "REDIS_URL" OR "REDIS_PASSWORD"
org:{org} "STRIPE_SECRET" OR "STRIPE_KEY"
org:{org} "TWILIO_AUTH_TOKEN" OR "SENDGRID_API_KEY"
org:{org} "SLACK_TOKEN" OR "SLACK_BOT_TOKEN"
org:{org} "GITHUB_TOKEN" OR "GH_TOKEN"
org:{org} "JWT_SECRET" OR "SESSION_SECRET"
org:{org} "ENCRYPTION_KEY" OR "CRYPTO_KEY"
"{target}" password OR secret OR token
"{target}" "api.{target}" internal OR staging
"""
    (dorks_dir / "github_dorks.txt").write_text(gh_dorks)
    ok("GitHub dorks saved: dorks/github_dorks.txt")

# ─────────────────────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────────────────────
def generate_report(target, out, stats):
    ph("GENERATING FINAL REPORT")

    vulns_dir   = out / "vulns"
    js_dir      = out / "js"
    secrets_dir = out / "secrets"
    params_dir  = out / "params"
    gql_dir     = out / "graphql"
    api_dir     = out / "api"
    screenshots_dir = out / "screenshots"

    def cat(path, lines=30):
        try:
            content = Path(path).read_text().strip()
            if content:
                return "\n".join(content.split("\n")[:lines])
            return "None found"
        except:
            return "None found"

    report = f"""# 🎯 BugHunter Pro Report — {target}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Output:** {out}/

---

## 📊 Recon Statistics

| Phase | Count |
|-------|-------|
| Passive Subdomains | {stats.get('passive_subs', 0)} |
| Resolved Subdomains | {stats.get('resolved', 0)} |
| Live Web Hosts | {stats.get('live', 0)} |
| Total URLs | {stats.get('total_urls', 0)} |
| JS Files Analyzed | {stats.get('js_files', 0)} |
| Source Maps Found | {stats.get('source_maps', 0)} |
| Secrets Found | {stats.get('secrets', 0)} |
| GraphQL Endpoints | {stats.get('graphql_eps', 0)} |
| API Paths Discovered | {stats.get('api_paths', 0)} |

---

## 🔥 HIGH PRIORITY FINDINGS

### 🔴 Exposed Admin Panels
```
{cat(vulns_dir/'nuclei_panels.txt')}
```

### 🔴 Default Credentials
```
{cat(vulns_dir/'nuclei_default_creds.txt')}
```

### 🔴 High/Critical CVEs
```
{cat(vulns_dir/'nuclei_cve.txt')}
```

### 🟠 Source Maps (Unminified Source Code Exposed)
```
{cat(js_dir/'source_maps_found.txt')}
```

### 🟠 Subdomain Takeovers
```
{cat(vulns_dir/'subzy_results.txt')}
```

### 🟠 CORS Misconfigurations
```
{cat(vulns_dir/'nuclei_cors.txt')}
```

### 🔴 CORS Standalone Testing
```
{cat(vulns_dir/'cors_misconfig.txt')}
```

### 🔴 CNAME Takeover Candidates
```
{cat(vulns_dir/'cname_takeovers.txt')}
```

### 🔴 Sensitive Files Exposed
```
{cat(vulns_dir/'sensitive_files.txt')}
```

### 🔴 CRLF Injection
```
{cat(vulns_dir/'crlf_injection.txt')}
```

### 🔴 Open Redirects Confirmed
```
{cat(vulns_dir/'open_redirects.txt')}
```

### 🟠 Host Header Injection
```
{cat(vulns_dir/'host_header_injection.txt')}
```

### 🔴 Dalfox XSS Findings
```
{cat(vulns_dir/'dalfox_xss.txt', 20)}
```

### 🟠 Secrets in JavaScript
```
{cat(secrets_dir/'js_api_key_generic.json', 10)}
```

### 🔴 JS Findings Per-File Report
> Full per-file breakdown: `secrets/js_findings_per_file.txt`
```
{cat(secrets_dir/'js_findings_per_file.txt', 50)}
```

### 🤖 AI-Powered Secret Scan
> AI-assisted detection — `secrets/js_ai_findings.txt`
```
{cat(secrets_dir/'js_ai_findings.txt', 30)}
```

### � GraphQL Introspection
```
{cat(gql_dir/'graphql_endpoints.txt')}
```

### 🔴 GraphQL Schema Types
```
{cat(gql_dir/'schema_types.txt', 20)}
```

### 🟠 API Endpoints Discovered
```
{cat(api_dir/'found_api_paths.txt', 20)}
```

### 🟠 HTTP Method Fuzzing Hits
```
{cat(api_dir/'method_allowed.txt')}
```

### �🟡 SSRF-Prone Parameters
```
{cat(params_dir/'ssrf_prone.txt', 20)}
```

### 🟡 Open Redirect Parameters
```
{cat(params_dir/'redirect_prone.txt', 20)}
```

### 🟡 XSS-Prone Parameters
```
{cat(params_dir/'xss_prone.txt', 20)}
```

### 🟡 IDOR-Prone Parameters
```
{cat(params_dir/'idor_prone.txt', 20)}
```

### 🟡 403 Bypass Successes
```
{cat(vulns_dir/'403_bypasses.txt')}
```

### 🟡 Exposed Files
```
{cat(vulns_dir/'nuclei_exposure.txt')}
```

### 🔵 Token/Secret Exposures
```
{cat(vulns_dir/'nuclei_tokens.txt')}
```

### 🔵 Misconfigurations
```
{cat(vulns_dir/'nuclei_misconfig.txt')}
```

---

## 📁 Output File Map

```
{out}/
├── subdomains/
│   ├── all_passive.txt        ← All discovered subdomains
│   └── [tool-specific files]
├── dns/
│   ├── resolved.txt           ← DNS-confirmed live subdomains
│   └── dns_details.txt        ← A, CNAME, MX records
├── web/
│   ├── live_urls.txt          ← Live HTTP/S hosts
│   ├── httpx_full.txt         ← Full httpx output + tech stack
│   └── 403_hosts.txt          ← 403 hosts (test bypass)
├── ips/
│   └── open_ports.txt         ← Open ports
├── endpoints/
│   ├── all_urls.txt           ← All discovered URLs
│   ├── linkfinder.txt         ← JS-extracted endpoints
│   ├── jsluice_endpoints.txt  ← AST-level JS endpoints
│   └── js_extracted_endpoints.txt ← Regex endpoint extraction
├── params/
│   ├── ssrf_prone.txt         ← SSRF-prone param URLs
│   ├── redirect_prone.txt     ← Open redirect param URLs
│   ├── injection_prone.txt    ← SQLi/XSS param URLs
│   ├── xss_prone.txt          ← Reflected XSS candidates
│   └── idor_prone.txt         ← IDOR-prone param URLs
├── js/
│   ├── js_urls.txt            ← All JS file URLs
│   ├── files/                 ← Downloaded JS files
│   └── maps/                  ← Downloaded source maps
├── secrets/                   ← All secret findings (JSON)
│   ├── js_findings_per_file.txt ← Per-file sensitive data report
│   └── js_findings_per_file.json← Per-file data (machine-readable)
├── graphql/
│   ├── graphql_endpoints.txt  ← Discovered GraphQL endpoints
│   ├── schema_types.txt       ← Extracted schema types
│   └── introspection_*.json   ← Full introspection dumps
├── api/
│   ├── found_api_paths.txt    ← API base paths found
│   ├── method_allowed.txt     ← HTTP method fuzzing hits
│   └── ffuf_*.json            ← ffuf API fuzzing results
├── screenshots/               ← gowitness/aquatone screenshots
├── vulns/                     ← Nuclei/subzy/CORS/CRLF/XSS results
│   ├── cname_takeovers.txt    ← Dangling CNAME takeover candidates
│   ├── sensitive_files.txt    ← Exposed .git/.env/configs
│   ├── cors_misconfig.txt     ← CORS misconfigurations
│   ├── crlf_injection.txt     ← CRLF injection findings
│   ├── open_redirects.txt     ← Confirmed open redirects
│   ├── host_header_injection.txt ← Host header injection
│   ├── dalfox_xss.txt         ← Reflected XSS findings
│   └── sqlmap_*/              ← SQLMap scan results
└── dorks/
    ├── google_dorks.txt       ← 80+ Google dorks
    └── github_dorks.txt       ← GitHub search dorks
```

---

## ⚡ Manual Attack Checklist

### Immediate Priority (check these first):
- [ ] Test all exposed panels in `vulns/nuclei_panels.txt` with default creds
- [ ] Decompile source maps: `sourcemapper -url <URL.map> -output ./src/`
- [ ] Validate all secrets in `secrets/` — test each API key manually
- [ ] Check `vulns/cname_takeovers.txt` — register dead services for takeover
- [ ] Verify `vulns/sensitive_files.txt` — download exposed .git/config/.env files
- [ ] Confirm CORS findings in `vulns/cors_misconfig.txt` — steal tokens via origin
- [ ] Test CRLF in `vulns/crlf_injection.txt` for cache poisoning / XSS
- [ ] Weaponize open redirects in `vulns/open_redirects.txt` for phishing + OAuth bypass
- [ ] Host header injection in `vulns/host_header_injection.txt` — password reset poisoning

### IDOR Testing:
- [ ] Install Autorize in Burp Suite
- [ ] Create 2 accounts (attacker + victim)
- [ ] Browse as high-priv, Autorize retests with low-priv
- [ ] Test all URLs in `endpoints/all_urls.txt` with numeric IDs

### SSRF Testing:
- [ ] Set up: `interactsh-client -v` (note your callback URL)
- [ ] Test all URLs in `params/ssrf_prone.txt`
- [ ] Payload: `http://169.254.169.254/latest/meta-data/` (AWS metadata)

### XSS Testing:
- [ ] Run: `cat endpoints/all_urls.txt | kxss` (reflected XSS finder)
- [ ] Run: `dalfox file endpoints/all_urls.txt --skip-bav`
- [ ] Blind XSS in profile fields with XSS Hunter payload

### Auth Testing:
- [ ] Test JWT: decode + try algorithm=none
- [ ] Password reset: inject `Host: attacker.com` header
- [ ] OAuth: test missing state param, redirect_uri bypass

### GraphQL Testing:
- [ ] If introspection enabled: dump full schema with InQL / graphql-voyager
- [ ] Test batch queries: `[{{"query":"..."}},{{"query":"..."}}]`
- [ ] Test query depth attacks (nested queries for DoS)
- [ ] Bypass disabled introspection: try `__type`, `__schema` individually
- [ ] Test for IDOR via GraphQL: `query {{ user(id: 1) {{ email }} }}`
- [ ] Check mutations for privilege escalation

### API Fuzzing:
- [ ] Test all endpoints in `api/found_api_paths.txt` with Burp
- [ ] Try PUT/DELETE on all found paths
- [ ] Test version rollback: /api/v1/ vs /api/v2/ for removed features
- [ ] Check `api/method_allowed.txt` for dangerous method access

### SQLi:
- [ ] Run: `sqlmap -l endpoints/injection_prone.txt --level 5 --batch`

*Generated by BugHunter Pro v4.0*
"""

    report_path = out / f"HUNT_REPORT_{target}.md"
    report_path.write_text(report)
    ok(f"Report saved: {report_path}")
    return report_path

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def clean_domain(raw):
    """Normalize a raw domain/URL/wildcard string into a clean domain."""
    line = raw.strip().lower()
    line = re.sub(r'^https?://', '', line)
    line = line.rstrip("/")
    line = line.split("/")[0]     # take only host
    line = line.split(":")[0]     # strip port
    line = line.lstrip("*.")
    return line


def parse_scope_file(path):
    """Parse a scope file. Supports:
    - One domain per line:        example.com
    - Wildcard prefix:            *.example.com  →  example.com
    - URL format:                 https://example.com  →  example.com
    - Comments (#) and blank lines are ignored
    - Lines starting with !  are out-of-scope (returned separately)
    """
    in_scope = []
    out_of_scope = []
    try:
        with open(path) as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                is_oos = line.startswith("!")
                if is_oos:
                    line = line.lstrip("!").strip()
                cleaned = clean_domain(line)
                if not cleaned:
                    continue
                if is_oos:
                    out_of_scope.append(cleaned)
                else:
                    in_scope.append(cleaned)
    except FileNotFoundError:
        die(f"Scope file not found: {path}")
    return list(dict.fromkeys(in_scope)), list(dict.fromkeys(out_of_scope))


def run_hunt(target, out, phase, cookie, stats):
    """Execute all requested phases for a single target domain."""
    if phase in ("all", "subs"):
        stats["passive_subs"] = stats.get("passive_subs", 0) + phase_passive_subs(target, out)

    if phase in ("all", "dns"):
        stats["resolved"] = stats.get("resolved", 0) + phase_dns(target, out)

    if phase in ("all", "http"):
        stats["live"] = stats.get("live", 0) + phase_http(target, out)

    if phase in ("all", "ports"):
        phase_ports(target, out)

    if phase in ("all", "content"):
        stats["total_urls"] = stats.get("total_urls", 0) + phase_content(target, out, cookie)

    if phase in ("all", "params"):
        phase_params(target, out)

    if phase in ("all", "js"):
        secrets, maps = phase_js(target, out)
        stats["secrets"]     = stats.get("secrets", 0) + secrets
        stats["source_maps"] = stats.get("source_maps", 0) + maps
        stats["js_files"]    = stats.get("js_files", 0) + len(list((out / "js" / "files").glob("*.js")))

    if phase in ("all", "graphql"):
        stats["graphql_eps"] = stats.get("graphql_eps", 0) + phase_graphql(target, out)

    if phase in ("all", "apifuzz"):
        stats["api_paths"] = stats.get("api_paths", 0) + phase_api_fuzz(target, out)

    if phase in ("all", "dorks"):
        phase_dorks(target, out)

    if phase in ("all", "vulns"):
        phase_vulns(target, out)

    if phase in ("all", "cloud"):
        phase_cloud(target, out)

    if phase in ("all", "github"):
        phase_github(target, out)


def main():
    parser = argparse.ArgumentParser(
        description="BugHunter Pro — Real Recon CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single domain
  python3 bughunter.py example.com
  python3 bughunter.py example.com --cookie "session=abc123"
  python3 bughunter.py example.com --phase js

  # Multiple domains (inline)
  python3 bughunter.py example.com api.example.com app.example.io

  # Scope file (one domain per line)
  python3 bughunter.py -s scope.txt
  python3 bughunter.py --scope scope.txt --cookie "session=abc123"

  # Comma-separated inline scope
  python3 bughunter.py -s "example.com,api.example.com,app.example.io"

  # Exclude specific subdomains
  python3 bughunter.py -s scope.txt --exclude "staging.example.com,dev.example.com"

  # Merge all domains into one output directory
  python3 bughunter.py -s scope.txt --merge

  # Scope file format (one domain per line):
  #   example.com
  #   *.api.example.com      -> wildcard stripped, becomes api.example.com
  #   https://app.example.io -> URL cleaned automatically
  #   !internal.example.com  -> excluded (out-of-scope)
  #   # this is a comment    -> ignored

  python3 bughunter.py --check-tools
  python3 bughunter.py --install
"""
    )
    parser.add_argument("target", nargs="*", help="Target domain(s) (e.g. example.com api.example.com)")
    parser.add_argument("-s", "--scope", help="Scope: path to file, or comma-separated domains (e.g. 'a.com,b.com')")
    parser.add_argument("--exclude", help="Comma-separated domains to exclude from scope")
    parser.add_argument("--cookie", help="Session cookie for authenticated crawling")
    parser.add_argument("--phase", choices=["all","subs","dns","http","ports","content","params","js","graphql","apifuzz","dorks","vulns","cloud","github"],
                        default="all", help="Run specific phase only")
    parser.add_argument("--check-tools", action="store_true", help="Check which tools are installed")
    parser.add_argument("--install", action="store_true", help="Show install commands for all tools")
    parser.add_argument("--output", help="Custom output directory")
    parser.add_argument("--threads", type=int, default=20, help="Thread count for parallel tasks")
    parser.add_argument("--merge", action="store_true", help="With --scope, merge all domains into a single output directory instead of one per domain")
    # ── AI-powered secret scanning ──
    parser.add_argument("--ai-secrets", action="store_true", help="Enable AI-powered secret scanning on JS files")
    parser.add_argument("--ai-secrets-only", action="store_true",
                        help="Skip regex entirely; use AI exclusively for JS secret detection")
    parser.add_argument("--ai-provider", choices=["openai", "claude", "ollama"], default="openai",
                        help="AI provider: openai (OpenAI/GPT/deepseek/any OpenAI-compat), claude (Anthropic Claude), or ollama (local)")
    parser.add_argument("--ai-model", help="AI model override (e.g. gpt-4o, claude-sonnet-4, deepseek-chat, llama3)")
    parser.add_argument("--ai-api-key", help="API key (defaults to OPENAI_API_KEY, ANTHROPIC_API_KEY, or provider-specific env)")
    parser.add_argument("--ai-api-base", help="Custom API base URL (e.g. https://api.openai.com/v1, https://api.anthropic.com/v1, http://localhost:11434)")

    args = parser.parse_args()
    banner()

    # ── AI config: --ai-secrets-only implies --ai-secrets ──
    global AI_CONFIG
    if args.ai_secrets_only or args.ai_secrets:
        AI_CONFIG["enabled"] = True
        AI_CONFIG["only"] = bool(args.ai_secrets_only)
        AI_CONFIG["provider"] = args.ai_provider or "openai"
        AI_CONFIG["model"] = args.ai_model
        AI_CONFIG["api_key"] = args.ai_api_key
        AI_CONFIG["api_base"] = args.ai_api_base

    if args.check_tools:
        check_tools()
        return

    if args.install:
        print_install_guide()
        return

    # ── Build target list ──
    excluded = []

    if args.scope:
        scope_val = args.scope.strip()
        # Check if it's a file path or inline comma-separated domains
        if os.path.isfile(scope_val):
            targets, excluded = parse_scope_file(scope_val)
        else:
            # Treat as comma/space separated domain list
            raw_domains = re.split(r'[,\s]+', scope_val)
            targets = list(dict.fromkeys(clean_domain(d) for d in raw_domains if clean_domain(d)))

        if not targets:
            die("Scope is empty or contains no valid domains")
        ok(f"Scope loaded: {len(targets)} domain(s) in-scope")

    elif args.target:
        # One or more positional domains
        targets = list(dict.fromkeys(clean_domain(t) for t in args.target if clean_domain(t)))
        if not targets:
            parser.print_help()
            return
    else:
        parser.print_help()
        return

    # Apply --exclude
    if args.exclude:
        extra_excl = [clean_domain(d) for d in re.split(r'[,\s]+', args.exclude) if clean_domain(d)]
        excluded.extend(extra_excl)

    if excluded:
        before = len(targets)
        targets = [t for t in targets if t not in excluded]
        removed = before - len(targets)
        if removed:
            warn(f"Excluded {removed} domain(s): {', '.join(excluded)}")
        if not targets:
            die("All domains were excluded — nothing to scan")

    if len(targets) > 1:
        ok(f"Targets: {', '.join(targets[:10])}{'...' if len(targets) > 10 else ''}")
    if excluded:
        warn(f"Out-of-scope: {', '.join(excluded)}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Check tools first
    missing = check_tools()
    if len(missing) > 10:
        warn("Many tools missing. Results will be limited. Run: python3 bughunter.py --install")
    print()

    stats = {}
    start = time.time()

    try:
        if args.merge and len(targets) > 1:
            # ── Merged mode: run each target in temp subdir, then merge ──
            primary = targets[0]
            out = Path(args.output) if args.output else Path(f"hunt_{primary}_{ts}")
            out.mkdir(parents=True, exist_ok=True)

            # Save scope info
            (out / "scope.txt").write_text("\n".join(targets) + "\n")
            if excluded:
                (out / "scope_excluded.txt").write_text("\n".join(excluded) + "\n")

            print(f"\n{W}Scope :{NC} {C}{', '.join(targets[:5])}{'...' if len(targets) > 5 else ''}{NC}")
            print(f"{W}Mode  :{NC} {C}MERGED (all results combined){NC}")
            print(f"{W}Output:{NC} {C}{out}/{NC}")
            print(f"{W}Time  :{NC} {C}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}\n")

            temp_dirs = []
            for i, target in enumerate(targets, 1):
                ph(f"TARGET {i}/{len(targets)}: {target}")
                temp_out = out / f".tmp_{target.replace('.', '_')}"
                temp_out.mkdir(parents=True, exist_ok=True)
                temp_dirs.append(temp_out)
                run_hunt(target, temp_out, args.phase, args.cookie, stats)

            # Merge all temp dirs into main output
            info("Merging results from all targets...")
            for temp_dir in temp_dirs:
                for root, dirs, files in os.walk(temp_dir):
                    rel = Path(root).relative_to(temp_dir)
                    dest_dir = out / rel
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    for fname in files:
                        src_file = Path(root) / fname
                        dest_file = dest_dir / fname
                        if dest_file.exists():
                            # Append and dedupe for text files
                            if fname.endswith(('.txt', '.json', '.md')):
                                existing = dest_file.read_text(errors='ignore')
                                new_data = src_file.read_text(errors='ignore')
                                merged = existing.rstrip("\n") + "\n" + new_data
                                if fname.endswith('.txt'):
                                    lines = sorted(set(l for l in merged.split("\n") if l.strip()))
                                    dest_file.write_text("\n".join(lines) + "\n")
                                else:
                                    dest_file.write_text(merged)
                            # Skip binaries / JS / maps that already exist
                        else:
                            shutil.copy2(str(src_file), str(dest_file))

            # Clean up temp dirs
            for temp_dir in temp_dirs:
                shutil.rmtree(str(temp_dir), ignore_errors=True)
            ok("Merge complete — all results combined")

            # Final report
            if args.phase == "all":
                generate_report(f"SCOPE ({len(targets)} domains)", out, stats)

            elapsed = int(time.time() - start)
            scope_label = f"{len(targets)} domains"
            print(f"""
{C}╔══════════════════════════════════════════════╗
║  HUNT COMPLETE in {elapsed}s                     
║  Scope  : {scope_label:<35}║
║  Output : {str(out):<35}║
╚══════════════════════════════════════════════╝{NC}
""")

        elif len(targets) == 1:
            # ── Single target ──
            target = targets[0]
            out = Path(args.output) if args.output else Path(f"hunt_{target}_{ts}")
            out.mkdir(parents=True, exist_ok=True)

            print(f"\n{W}Target:{NC} {C}{target}{NC}")
            print(f"{W}Output:{NC} {C}{out}/{NC}")
            print(f"{W}Time  :{NC} {C}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}\n")

            run_hunt(target, out, args.phase, args.cookie, stats)

            if args.phase == "all":
                generate_report(target, out, stats)

            elapsed = int(time.time() - start)
            print(f"""
{C}╔══════════════════════════════════════════════╗
║  HUNT COMPLETE in {elapsed}s                     
║  Target : {target:<35}║
║  Output : {str(out):<35}║
╚══════════════════════════════════════════════╝{NC}
""")

        else:
            # ── Separate mode: one output dir per domain ──
            base_dir = Path(args.output) if args.output else Path(f"hunt_scope_{ts}")
            base_dir.mkdir(parents=True, exist_ok=True)

            # Save scope info
            (base_dir / "scope.txt").write_text("\n".join(targets) + "\n")
            if excluded:
                (base_dir / "scope_excluded.txt").write_text("\n".join(excluded) + "\n")

            print(f"\n{W}Scope :{NC} {C}{len(targets)} domains → separate output dirs{NC}")
            print(f"{W}Base  :{NC} {C}{base_dir}/{NC}")
            print(f"{W}Time  :{NC} {C}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}\n")

            all_stats = {}
            for i, target in enumerate(targets, 1):
                ph(f"TARGET {i}/{len(targets)}: {target}")
                domain_out = base_dir / target.replace(".", "_")
                domain_out.mkdir(parents=True, exist_ok=True)
                domain_stats = {}
                run_hunt(target, domain_out, args.phase, args.cookie, domain_stats)

                # Per-domain report
                if args.phase == "all":
                    generate_report(target, domain_out, domain_stats)

                # Accumulate
                for k, v in domain_stats.items():
                    all_stats[k] = all_stats.get(k, 0) + v

                ok(f"Completed {target} → {domain_out}/")
                print()

            elapsed = int(time.time() - start)
            print(f"""
{C}╔══════════════════════════════════════════════╗
║  ALL HUNTS COMPLETE in {elapsed}s                
║  Scope  : {len(targets)} domains{' ' * (29 - len(str(len(targets))))}║
║  Output : {str(base_dir):<35}║
╚══════════════════════════════════════════════╝{NC}
""")

            # Summary across all domains
            print(f"{W}Combined Stats:{NC}")
            for k, v in all_stats.items():
                print(f"  {k}: {v}")

    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupted by user. Partial results saved.{NC}")


def print_install_guide():
    print(f"""
{C}========================================================
   BugHunter Pro v4.0 -- Tool Installer Guide
========================================================{NC}

{Y}QUICK INSTALL (recommended):{NC}
  chmod +x install.sh && sudo bash install.sh

{Y}--- OR install manually step by step: ---{NC}

{Y}Step 1 -- Install Go (1.23+):{NC}
  wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz
  sudo rm -rf /usr/local/go
  sudo tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz
  echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
  source ~/.bashrc

{Y}Step 2 -- Install Go recon tools (copy-paste entire block):{NC}
  # ProjectDiscovery suite
  go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
  go install github.com/projectdiscovery/httpx/cmd/httpx@latest
  go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
  go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
  go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
  go install github.com/projectdiscovery/katana/cmd/katana@latest
  go install github.com/projectdiscovery/asnmap/cmd/asnmap@latest
  go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

  # Tomnomnom suite
  go install github.com/tomnomnom/assetfinder@latest
  go install github.com/tomnomnom/waybackurls@latest
  go install github.com/tomnomnom/unfurl@latest
  go install github.com/tomnomnom/httprobe@latest
  go install github.com/tomnomnom/gf@latest

  # Fuzzing & crawling
  go install github.com/ffuf/ffuf/v2@latest
  go install github.com/hakluke/hakrawler@latest
  go install github.com/lc/gau/v2/cmd/gau@latest
  go install github.com/Emoe/kxss@latest

  # Scanners & recon
  go install github.com/hahwul/dalfox/v2@latest
  go install github.com/PentestPad/subzy@latest
  go install github.com/BishopFox/jsluice/cmd/jsluice@latest
  go install github.com/003random/getJS@latest
  go install github.com/d3mondev/puredns/v2@latest
  go install github.com/Josue87/gotator@latest
  go install github.com/bp0lr/gauplus@latest
  go install github.com/owasp-amass/amass/v4/...@master
  go install github.com/gwen001/github-subdomains@latest

  # Git scanners
  go install github.com/zricethezav/gitleaks/v8@latest

  # Route discovery
  go install github.com/assetnote/kiterunner/cmd/kr@latest

  # Screenshots
  go install github.com/sensepost/gowitness@latest

{Y}Step 3 -- Install system packages:{NC}
  sudo apt update
  sudo apt install -y nmap masscan jq wafw00f sqlmap awscli chromium-browser

{Y}Step 4 -- Install Python packages:{NC}
  pip3 install arjun py-altdns --break-system-packages

{Y}Step 5 -- Install TruffleHog:{NC}
  curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sudo sh -s -- -b /usr/local/bin

{Y}Step 6 -- Install feroxbuster:{NC}
  curl -sL https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh | bash

{Y}Step 7 -- Install LinkFinder:{NC}
  sudo git clone https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder
  pip3 install -r /opt/LinkFinder/requirements.txt --break-system-packages

{Y}Step 8 -- Install aquatone (optional):{NC}
  wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip -O /tmp/aquatone.zip
  sudo unzip -o /tmp/aquatone.zip -d /usr/local/bin/ aquatone
  sudo chmod +x /usr/local/bin/aquatone

{Y}Step 9 -- Install wordlists:{NC}
  sudo git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists

{Y}Step 10 -- Download DNS resolvers (for puredns):{NC}
  sudo wget https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt -O /opt/resolvers.txt

{Y}Step 11 -- Update nuclei templates:{NC}
  nuclei -update-templates

{Y}Step 12 -- Set GitHub token (for GitHub scanning):{NC}
  export GITHUB_TOKEN="ghp_your_token_here"
  echo 'export GITHUB_TOKEN="ghp_..."' >> ~/.bashrc

{G}All done! Run:{NC}
  python3 bughunter.py example.com
  python3 bughunter.py --scope scope.txt
  python3 bughunter.py --check-tools
""")


if __name__ == "__main__":
    main()
