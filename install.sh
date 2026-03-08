#!/bin/bash
# ============================================================
# BugHunter Pro v4.0 -- One-Shot Tool Installer
# Tested on: Kali Linux 2024+, Ubuntu 22.04/24.04, Parrot OS
# Run:  chmod +x install.sh && sudo bash install.sh
# ============================================================

set -uo pipefail    # no -e : we handle failures per-tool
G='\033[0;32m'; C='\033[0;36m'; Y='\033[1;33m'; R='\033[0;31m'; W='\033[1;37m'; NC='\033[0m'
ok()   { echo -e "${G}[+]${NC} $1"; }
info() { echo -e "${C}[~]${NC} $1"; }
warn() { echo -e "${Y}[!]${NC} $1"; }
err()  { echo -e "${R}[x]${NC} $1"; }

TOTAL=0; PASS=0; FAIL=0; SKIP=0
FAILED_LIST=""
track() { TOTAL=$((TOTAL+1)); }
pass()  { PASS=$((PASS+1)); ok "$1"; }
skip()  { SKIP=$((SKIP+1)); ok "$1 (already installed)"; }
fail()  { FAIL=$((FAIL+1)); FAILED_LIST="${FAILED_LIST}\n  - $1"; warn "FAILED: $1"; }

install_go_tool() {
  local name="$1" pkg="$2"
  track
  if command -v "$name" &>/dev/null; then
    skip "$name"
    return
  fi
  info "Installing $name..."
  if go install "$pkg" 2>/dev/null; then
    if command -v "$name" &>/dev/null || [ -f "${GOPATH}/bin/$name" ] || [ -f "${HOME}/go/bin/$name" ]; then
      pass "$name"
    else
      fail "$name (compiled but not in PATH)"
    fi
  else
    fail "$name"
  fi
}

echo -e "${C}"
echo "========================================================"
echo "   BugHunter Pro v4.0 -- Full Tool Installer"
echo "   Made By KJI"
echo "========================================================"
echo -e "${NC}"

# -- 0. Root check --
if [ "$EUID" -ne 0 ]; then
  warn "Not running as root. Some installs may fail."
  warn "Recommended: sudo bash install.sh"
  echo ""
fi

# -- 1. Prerequisites & Go --
info "Step 1/9: System prerequisites..."
apt-get update -qq 2>/dev/null || sudo apt-get update -qq 2>/dev/null
PKGS="git curl wget unzip python3 python3-pip libpcap-dev build-essential dnsutils whois"
for pkg in $PKGS; do
  if dpkg -s "$pkg" &>/dev/null; then
    true
  else
    apt-get install -y -qq "$pkg" 2>/dev/null || sudo apt-get install -y -qq "$pkg" 2>/dev/null || warn "Could not install $pkg"
  fi
done
ok "Base packages checked"

if ! command -v go &>/dev/null; then
  info "Installing Go 1.23.0..."
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64)  GO_ARCH="amd64" ;;
    aarch64) GO_ARCH="arm64" ;;
    armv*)   GO_ARCH="armv6l" ;;
    *)       GO_ARCH="amd64" ;;
  esac
  GO_TAR="go1.23.0.linux-${GO_ARCH}.tar.gz"
  wget -q "https://go.dev/dl/${GO_TAR}" -O "/tmp/${GO_TAR}" || { err "Failed to download Go"; exit 1; }
  rm -rf /usr/local/go
  tar -C /usr/local -xzf "/tmp/${GO_TAR}"
  rm -f "/tmp/${GO_TAR}"
  ok "Go 1.23.0 installed"
else
  ok "Go already installed: $(go version | head -1)"
fi

export GOPATH="${GOPATH:-${HOME}/go}"
export PATH="${PATH}:/usr/local/go/bin:${GOPATH}/bin"

for RC_FILE in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
  if [ -f "$RC_FILE" ]; then
    grep -q 'go/bin' "$RC_FILE" 2>/dev/null || {
      echo '' >> "$RC_FILE"
      echo '# BugHunter Pro -- Go PATH' >> "$RC_FILE"
      echo 'export GOPATH="${GOPATH:-$HOME/go}"' >> "$RC_FILE"
      echo 'export PATH="$PATH:/usr/local/go/bin:$GOPATH/bin"' >> "$RC_FILE"
    }
  fi
done

if ! go version &>/dev/null; then
  err "Go installation broken. Cannot continue."
  exit 1
fi

echo ""

# -- 2. Go tools --
info "Step 2/9: Installing Go-based recon tools (this takes a while)..."
echo ""

# ProjectDiscovery suite
install_go_tool subfinder    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go_tool httpx        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
install_go_tool nuclei       "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
install_go_tool naabu        "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
install_go_tool dnsx         "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
install_go_tool katana       "github.com/projectdiscovery/katana/cmd/katana@latest"
install_go_tool asnmap       "github.com/projectdiscovery/asnmap/cmd/asnmap@latest"
install_go_tool interactsh-client "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest"

# Tomnomnom suite
install_go_tool assetfinder  "github.com/tomnomnom/assetfinder@latest"
install_go_tool waybackurls  "github.com/tomnomnom/waybackurls@latest"
install_go_tool unfurl       "github.com/tomnomnom/unfurl@latest"
install_go_tool httprobe     "github.com/tomnomnom/httprobe@latest"
install_go_tool gf           "github.com/tomnomnom/gf@latest"

# Fuzzing & crawling
install_go_tool ffuf         "github.com/ffuf/ffuf/v2@latest"
install_go_tool hakrawler    "github.com/hakluke/hakrawler@latest"
install_go_tool gau          "github.com/lc/gau/v2/cmd/gau@latest"
install_go_tool gauplus      "github.com/bp0lr/gauplus@latest"
install_go_tool kxss         "github.com/Emoe/kxss@latest"

# Scanners
install_go_tool dalfox       "github.com/hahwul/dalfox/v2@latest"
install_go_tool subzy        "github.com/PentestPad/subzy@latest"
install_go_tool jsluice      "github.com/BishopFox/jsluice/cmd/jsluice@latest"

# Misc recon
install_go_tool getJS        "github.com/003random/getJS@latest"
install_go_tool puredns      "github.com/d3mondev/puredns/v2@latest"
install_go_tool gotator      "github.com/Josue87/gotator@latest"
install_go_tool amass        "github.com/owasp-amass/amass/v4/...@master"
install_go_tool github-subdomains "github.com/gwen001/github-subdomains@latest"

# Git scanners
install_go_tool gitleaks     "github.com/zricethezav/gitleaks/v8@latest"

# Screenshots
install_go_tool gowitness    "github.com/sensepost/gowitness@latest"

echo ""

# -- 3. Kiterunner (needs special build) --
info "Step 3/9: Kiterunner (API route discovery)..."
track
if command -v kr &>/dev/null; then
  skip "kr (kiterunner)"
else
  info "Building kiterunner from source..."
  TMPKR=$(mktemp -d)
  if git clone --depth 1 https://github.com/assetnote/kiterunner.git "$TMPKR" 2>/dev/null && \
     cd "$TMPKR" && make build 2>/dev/null && \
     cp dist/kr "${GOPATH}/bin/kr" 2>/dev/null; then
    pass "kr (kiterunner)"
  else
    # Fallback: try go install
    if go install github.com/assetnote/kiterunner/cmd/kr@latest 2>/dev/null; then
      pass "kr (kiterunner via go install)"
    else
      fail "kr (kiterunner) -- install manually: https://github.com/assetnote/kiterunner"
    fi
  fi
  rm -rf "$TMPKR" 2>/dev/null
  cd - &>/dev/null || true
fi

# Kiterunner routes wordlist
if [ ! -d /opt/kiterunner ]; then
  mkdir -p /opt/kiterunner 2>/dev/null || sudo mkdir -p /opt/kiterunner 2>/dev/null
fi
if [ ! -f /opt/kiterunner/routes-large.kite ]; then
  info "Downloading kiterunner routes wordlist..."
  wget -q "https://wordlists-cdn.assetnote.io/data/kiterunner/routes-large.kite" \
    -O /opt/kiterunner/routes-large.kite 2>/dev/null && \
    ok "Kiterunner routes wordlist" || warn "Could not download kiterunner routes (non-critical)"
fi

echo ""

# -- 4. System packages (apt) --
info "Step 4/9: System packages (apt)..."
APT_TOOLS="nmap masscan jq wafw00f sqlmap awscli chromium-browser"
for pkg in $APT_TOOLS; do
  track
  if dpkg -s "$pkg" &>/dev/null || command -v "$pkg" &>/dev/null; then
    skip "$pkg"
  else
    info "Installing $pkg..."
    if apt-get install -y -qq "$pkg" 2>/dev/null || sudo apt-get install -y -qq "$pkg" 2>/dev/null; then
      pass "$pkg"
    else
      fail "$pkg"
    fi
  fi
done

echo ""

# -- 5. Python packages (pip3) --
info "Step 5/9: Python packages (pip3)..."

track
if command -v arjun &>/dev/null; then
  skip "arjun"
else
  info "Installing arjun..."
  if pip3 install arjun --break-system-packages -q 2>/dev/null || pip3 install arjun -q 2>/dev/null; then
    pass "arjun"
  else
    fail "arjun"
  fi
fi

track
if command -v altdns &>/dev/null; then
  skip "altdns"
else
  info "Installing altdns..."
  if pip3 install py-altdns --break-system-packages -q 2>/dev/null || pip3 install py-altdns -q 2>/dev/null; then
    pass "altdns"
  else
    fail "altdns"
  fi
fi

echo ""

# -- 6. TruffleHog --
info "Step 6/9: TruffleHog (secret scanner)..."
track
if command -v trufflehog &>/dev/null; then
  skip "trufflehog"
else
  info "Installing trufflehog..."
  if curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh \
    | sh -s -- -b /usr/local/bin 2>/dev/null; then
    pass "trufflehog"
  else
    fail "trufflehog"
  fi
fi

echo ""

# -- 7. Feroxbuster --
info "Step 7/9: Feroxbuster (directory fuzzer)..."
track
if command -v feroxbuster &>/dev/null; then
  skip "feroxbuster"
else
  info "Installing feroxbuster..."
  if curl -sL https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh \
    | bash -s "${GOPATH}/bin" 2>/dev/null; then
    pass "feroxbuster"
  else
    # Kali has it in apt
    if apt-get install -y -qq feroxbuster 2>/dev/null || sudo apt-get install -y -qq feroxbuster 2>/dev/null; then
      pass "feroxbuster (via apt)"
    else
      fail "feroxbuster"
    fi
  fi
fi

echo ""

# -- 8. LinkFinder + aquatone --
info "Step 8/9: LinkFinder + aquatone..."

track
if [ -f /opt/LinkFinder/linkfinder.py ]; then
  skip "LinkFinder"
else
  info "Installing LinkFinder..."
  rm -rf /opt/LinkFinder 2>/dev/null
  if git clone --depth 1 https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder 2>/dev/null; then
    pip3 install -r /opt/LinkFinder/requirements.txt --break-system-packages -q 2>/dev/null || \
    pip3 install -r /opt/LinkFinder/requirements.txt -q 2>/dev/null || true
    pass "LinkFinder"
  else
    fail "LinkFinder"
  fi
fi

track
if command -v aquatone &>/dev/null; then
  skip "aquatone"
else
  info "Installing aquatone..."
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64)  AQUA_ARCH="amd64" ;;
    aarch64) AQUA_ARCH="arm64" ;;
    *)       AQUA_ARCH="amd64" ;;
  esac
  AQUA_URL="https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_${AQUA_ARCH}_1.7.0.zip"
  if wget -q "$AQUA_URL" -O /tmp/aquatone.zip 2>/dev/null; then
    unzip -o /tmp/aquatone.zip -d /tmp/aquatone_extract 2>/dev/null
    if [ -f /tmp/aquatone_extract/aquatone ]; then
      mv /tmp/aquatone_extract/aquatone /usr/local/bin/aquatone 2>/dev/null || \
      sudo mv /tmp/aquatone_extract/aquatone /usr/local/bin/aquatone 2>/dev/null
      chmod +x /usr/local/bin/aquatone 2>/dev/null || sudo chmod +x /usr/local/bin/aquatone 2>/dev/null
      pass "aquatone"
    else
      fail "aquatone (zip extraction issue)"
    fi
    rm -rf /tmp/aquatone.zip /tmp/aquatone_extract 2>/dev/null
  else
    fail "aquatone (download failed -- gowitness is preferred alternative)"
  fi
fi

echo ""

# -- 9. Wordlists, resolvers, templates --
info "Step 9/9: Wordlists, resolvers & nuclei templates..."

track
if [ -d /opt/SecLists ]; then
  skip "SecLists"
else
  info "Cloning SecLists (~500MB)..."
  if git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists 2>/dev/null || \
     sudo git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists 2>/dev/null; then
    pass "SecLists"
  else
    fail "SecLists"
  fi
fi

track
RESOLVERS="/opt/resolvers.txt"
if [ -f "$RESOLVERS" ]; then
  skip "DNS resolvers"
else
  info "Downloading DNS resolvers..."
  if wget -q "https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt" -O "$RESOLVERS" 2>/dev/null || \
     sudo wget -q "https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt" -O "$RESOLVERS" 2>/dev/null; then
    pass "DNS resolvers"
  else
    fail "DNS resolvers"
  fi
fi

track
if command -v nuclei &>/dev/null; then
  info "Updating nuclei templates..."
  if nuclei -update-templates -silent 2>/dev/null; then
    pass "nuclei templates"
  else
    fail "nuclei templates (try: nuclei -update-templates)"
  fi
else
  warn "nuclei not installed -- skipping template update"
fi

# -- Final summary --
echo ""
echo -e "${C}========================================================${NC}"
echo -e "${W}  Installation Summary${NC}"
echo -e "${C}========================================================${NC}"
echo -e "  ${G}Installed : ${PASS}${NC}"
echo -e "  ${C}Skipped   : ${SKIP} (already present)${NC}"
echo -e "  ${R}Failed    : ${FAIL}${NC}"
echo -e "  Total     : ${TOTAL}"
echo -e "${C}========================================================${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then
  warn "Failed tools (non-critical -- script skips missing tools):"
  echo -e "$FAILED_LIST"
  echo ""
fi

# Verify critical tools
info "Verifying critical tools..."
CRITICAL="subfinder httpx nuclei dnsx katana gau waybackurls jsluice ffuf"
ALL_GOOD=true
for tool in $CRITICAL; do
  if command -v "$tool" &>/dev/null; then
    ok "$tool"
  else
    err "$tool -- MISSING (required)"
    ALL_GOOD=false
  fi
done

echo ""
if [ "$ALL_GOOD" = true ]; then
  echo -e "${G}All critical tools verified! Ready to hunt.${NC}"
else
  warn "Some critical tools missing. Run: python3 bughunter.py --check-tools"
fi

echo ""
echo -e "${C}Quick start:${NC}"
echo "  python3 bughunter.py example.com"
echo "  python3 bughunter.py -s scope.txt"
echo "  python3 bughunter.py example.com api.example.com"
echo "  python3 bughunter.py --check-tools"
echo ""
echo -e "${Y}Recommended -- set GitHub token for secret scanning:${NC}"
echo "  export GITHUB_TOKEN='ghp_your_token_here'"
echo "  echo 'export GITHUB_TOKEN=ghp_...' >> ~/.bashrc"
echo ""
echo -e "${G}Done! Reload your shell: source ~/.bashrc${NC}"
