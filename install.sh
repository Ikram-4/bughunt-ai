#!/usr/bin/env bash
set -euo pipefail

# BugHunter Pro — Combined Edition Installer
# Based on Claude Bug Bounty + BugHunter Pro v4.0

BOLD="\033[1m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; CYAN="\033[0;36m"; RED="\033[0;31m"; NC="\033[0m"
ok()  { echo -e "${GREEN}${BOLD}[+]${NC} $1"; }
info() { echo -e "${CYAN}${BOLD}[*]${NC} $1"; }
warn() { echo -e "${YELLOW}${BOLD}[!]${NC} $1"; }

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STANDALONE=false

# Parse args
for arg in "$@"; do
    case "$arg" in
        --agent|--standalone) STANDALONE=true ;;
        --help)
            echo "Usage: ./install.sh [--agent|--standalone]"
            echo "  --agent|--standalone  Install as system-wide 'bughunter-pro' command"
            exit 0
            ;;
    esac
done

echo -e "${CYAN}
██████╗ ██╗   ██╗ ██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
██╔══██╗██║   ██║██╔════╝ ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██████╔╝██║   ██║██║  ███╗███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██╗██║   ██║██║   ██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
${NC}"
echo -e "${BOLD}  BugHunter Pro — Combined Edition${NC}"
echo -e "${BOLD}  AI-Powered Bug Bounty — Recon to Report${NC}\n"

info "Installing BugHunter Pro..."

# Python deps
info "Installing Python dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install --quiet requests 2>/dev/null || true
    pip3 install --quiet pytest 2>/dev/null || true
    pip3 install --quiet ollama 2>/dev/null || true
    info "Python packages installed"
else
    warn "pip3 not found — install python3-pip"
fi

# Default wordlists
WORDLIST_DIR="$REPO_DIR/wordlists"
mkdir -p "$WORDLIST_DIR"
if [ ! -f "$WORDLIST_DIR/common.txt" ]; then
    info "Downloading default wordlists..."
    curl -sL "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" -o "$WORDLIST_DIR/common.txt" 2>/dev/null && ok "common.txt" || warn "Failed to download wordlists"
fi
if [ ! -f "$WORDLIST_DIR/api-endpoints.txt" ]; then
    curl -sL "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/api/api-endpoints.txt" -o "$WORDLIST_DIR/api-endpoints.txt" 2>/dev/null && ok "api-endpoints.txt" || true
fi

# Standalone mode: create symlink
if [ "$STANDALONE" = true ]; then
    info "Installing as system-wide 'bughunter-pro' command..."
    INSTALL_DIR="/usr/local/bin"
    if [ ! -w "$INSTALL_DIR" ]; then
        INSTALL_DIR="$HOME/.local/bin"
        mkdir -p "$INSTALL_DIR"
    fi
    REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
    cat > "$INSTALL_DIR/bughunter-pro" << SCRIPT
#!/usr/bin/env bash
REPO_DIR="$REPO_ROOT"
exec python3 "\$REPO_DIR/engine.py" "\$@"
SCRIPT
    chmod +x "$INSTALL_DIR/bughunter-pro"
    ok "'bughunter-pro' command installed to $INSTALL_DIR"
    ok "Run: bughunter-pro setup"
    ok "Run: bughunter-pro recon target.com"
    ok "Run: bughunter-pro deep target.com   (all 13 phases)"
fi

# Summary
ok "BugHunter Pro installation complete!"
echo ""
echo -e "  ${CYAN}Quick Start:${NC}"
echo "  ────────────"
echo "  bughunter-pro setup               Configure AI provider"
echo "  bughunter-pro recon target.com    Recon (phases 1-7)"
echo "  bughunter-pro deep target.com     Deep recon (all 13 phases)"
echo "  bughunter-pro js target.com       JS deep recon only"
echo "  bughunter-pro validate \"finding\"  Validate a finding"
echo "  bughunter-pro report              Generate report"
echo ""
echo -e "  ${YELLOW}Install external tools for full functionality:${NC}"
echo "  ./install_tools.sh"
echo ""
echo -e "  ${YELLOW}Documentation:${NC}"
echo "  cat README.md"
echo "  cat docs/TUTORIAL.md"
