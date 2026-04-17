#!/bin/bash
# start.sh — Start the full CertChain stack
# Usage: bash start.sh

set -e
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     CertChain — Full Stack Startup           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Check if hardhat node is already running
if curl -s http://127.0.0.1:8545 > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Hardhat node already running${NC}"
else
  echo -e "${BLUE}▶ Starting Hardhat node in background...${NC}"
  npx hardhat node > /tmp/hardhat.log 2>&1 &
  HARDHAT_PID=$!
  echo -e "   PID: $HARDHAT_PID"
  sleep 3

  # Deploy contract
  echo -e "${BLUE}▶ Deploying smart contract...${NC}"
  npx hardhat run scripts/deploy.js --network localhost
  echo ""
fi

# Check deployment.json exists
if [ ! -f deployment.json ]; then
  echo -e "${YELLOW}▶ No deployment found. Deploying...${NC}"
  npx hardhat run scripts/deploy.js --network localhost
fi

# Install Flask if needed
echo -e "${BLUE}▶ Checking Python dependencies...${NC}"
pip install flask flask-cors web3 --break-system-packages -q
echo -e "${GREEN}✅ Dependencies ready${NC}"

# Copy backend files if not present
mkdir -p backend
[ -f backend/server.py ]     || cp server.py backend/     2>/dev/null || true
[ -f backend/blockchain.py ] || cp blockchain.py backend/ 2>/dev/null || true

# Start Flask backend
echo ""
echo -e "${BLUE}▶ Starting Flask API server on port 5000...${NC}"
cd backend
python3 server.py &
FLASK_PID=$!
cd ..
sleep 2

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  CertChain is LIVE!                      ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║  🌐 Frontend : open frontend/index.html      ║${NC}"
echo -e "${GREEN}║  📊 Dashboard: open frontend/dashboard.html  ║${NC}"
echo -e "${GREEN}║  🔗 API      : http://localhost:5000/api     ║${NC}"
echo -e "${GREEN}║  ⛓️  Chain    : http://localhost:8545         ║${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Open browser
sleep 1
xdg-open frontend/index.html 2>/dev/null || firefox frontend/index.html 2>/dev/null || true

# Wait
wait $FLASK_PID
