#!/usr/bin/env python3
"""
validate.py — 7-Question Validation Gate + Smart Triage for Bug Bounty Findings.
Validates findings before reporting: kills weak findings, prioritizes strong ones.
"""

import argparse, json, os, re, subprocess, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
FINDINGS_DIR = HERE / "findings"
REPORTS_DIR = HERE / "reports"

GREEN="\033[0;32m"; RED="\033[0;31m"; YELLOW="\033[1;33m"
CYAN="\033[0;36m"; BOLD="\033[1m"; NC="\033[0m"

def ok(msg): print(f"{GREEN}{BOLD}[+]{NC} {msg}")
def warn(msg): print(f"{YELLOW}{BOLD}[!]{NC} {msg}")
def err(msg): print(f"{RED}{BOLD}[-]{NC} {msg}")
def info(msg): print(f"{CYAN}{BOLD}[*]{NC} {msg}")

VALIDATION_QUESTIONS = [
    ("Can you reproduce it consistently?", "reproducible"),
    ("Is there a realistic attack scenario?", "realistic"),
    ("Does it leak sensitive data or allow code execution?", "impact"),
    ("Is it in-scope for the program?", "scope"),
    ("Can you provide a working PoC?", "poc"),
    ("Is this a known vulnerability (CVE/cve.mitre.org)?", "known"),
    ("Is there a clear remediation?", "remediation"),
]

def ask_questions(finding_text):
    scores = {}
    print(f"\n{BOLD}7-Question Validation Gate{NC}")
    print(f"Finding: {finding_text[:100]}\n")
    for question, key in VALIDATION_QUESTIONS:
        while True:
            answer = input(f"{BOLD}Q:{NC} {question} (y/n/?) ").strip().lower()
            if answer == "y": scores[key] = 1; break
            elif answer == "n": scores[key] = 0; break
            elif answer == "?":
                if key == "reproducible":
                    print("  Can you make it happen every time, or is it random? Manual vs automated?")
                elif key == "realistic":
                    print("  What would a real attacker need to do? Does it require unlikely preconditions?")
                elif key == "impact":
                    print("  Data exposure, account takeover, RCE, privilege escalation?")
                elif key == "scope":
                    print("  Check the program's scope policy. Is the asset Wildcard? *.target.com?")
                elif key == "poc":
                    print("  Do you have a curl command, script, or browser steps that prove it?")
                elif key == "known":
                    print("  Search CVE/NVD, hackerone reports, disclosure archives.")
                elif key == "remediation":
                    print("  Can you suggest a fix? Input validation? Rate limiting? Access control?")
    total = sum(scores.values())
    max_score = len(VALIDATION_QUESTIONS)
    print(f"\n{BOLD}Gate Score: {total}/{max_score}{NC}")
    if total >= 6:
        print(f"{GREEN}{BOLD}>> PASS: High-confidence finding, ready for report{NC}")
        return True, scores
    elif total >= 4:
        print(f"{YELLOW}{BOLD}>> BORDERLINE: Needs more verification{NC}")
        return False, scores
    else:
        print(f"{RED}{BOLD}>> KILL: Low confidence, not worth reporting{NC}")
        return False, scores


def auto_triage(finding_text):
    """Automated triage heuristic."""
    text = finding_text.lower()
    critical_kw = ["rce","remote code","sql injection","sqli","authentication bypass",
                   "privilege escalation","account takeover","ato","ssrf","idor",
                   "xss","stored","critical","cve-"]
    high_kw = ["csrf","open redirect","information disclosure","path traversal",
               "lfi","xxe","subdomain takeover","cors","high"]
    score = 0
    for kw in critical_kw:
        if kw in text: score += 3
    for kw in high_kw:
        if kw in text: score += 2
    if any(t in text for t in ["poc","reproducible","confirmed"]): score += 2
    if any(t in text for t in ["maybe","might","could","unlikely","low"]): score -= 2

    if score >= 5: return "HIGH", "High-confidence finding, ready for report"
    elif score >= 3: return "MEDIUM", "Medium confidence, needs manual verification"
    else: return "LOW", "Low confidence, consider killing or downgrading"


def generate_report(findings_dir=None):
    """Generate a submission-ready HackerOne/Bugcrowd report."""
    if not findings_dir:
        findings_dir = FINDINGS_DIR if FINDINGS_DIR.exists() else input("Findings directory: ")
    findings_path = Path(findings_dir)

    print(f"Generating report from: {findings_path}")
    findings = []
    for f in findings_path.rglob("*"):
        if f.suffix in (".txt", ".json", ".md"):
            try:
                content = f.read_text(errors="ignore")[:1000]
                findings.append({"file": str(f.relative_to(HERE)), "content": content})
            except: pass

    report = f"""# Bug Bounty Submission Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{len(findings)} findings identified during automated reconnaissance.

## Findings
"""
    for i, finding in enumerate(findings, 1):
        report += f"\n### Finding {i}: {finding['file']}\n```\n{finding['content']}\n```\n"

    REPORTS_DIR.mkdir(exist_ok=True)
    report_file = REPORTS_DIR / f"bug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report)
    ok(f"Report saved: {report_file}")
    return report_file


def main():
    ap = argparse.ArgumentParser(description="BugHunter Pro — Finding Validation Gate")
    ap.add_argument("finding", nargs="?", help="Finding description to validate")
    ap.add_argument("--report", action="store_true", help="Generate report from findings")
    ap.add_argument("--findings-dir", help="Path to findings directory")
    ap.add_argument("--auto", action="store_true", help="Auto-triage without interactive questions")
    args = ap.parse_args()

    if args.report:
        generate_report(args.findings_dir)
        return 0

    if not args.finding:
        err("Usage: bughunter-pro validate \"finding description\"")
        ap.print_help()
        return 1

    if args.auto:
        severity, reason = auto_triage(args.finding)
        print(f"{BOLD}Auto-triage result: {severity}{NC}")
        print(f"Reason: {reason}")
    else:
        passed, scores = ask_questions(args.finding)
        if passed:
            ok("Finding validated — proceed to report")
        else:
            warn("Finding needs more work before reporting")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
