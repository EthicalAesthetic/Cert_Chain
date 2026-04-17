# 🔗 CertChain — Blockchain-Based Academic Certificate Verification System

> Issue tamper-proof academic certificates on the Ethereum blockchain and verify authenticity in milliseconds. No central authority. No forgery. Forever on-chain.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Smart Contract](#smart-contract)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)
- [Important Note](#important-note)

---

## Overview

CertChain solves the problem of academic certificate fraud by storing certificates as cryptographic hashes on an Ethereum-compatible blockchain. Once issued, a certificate cannot be altered, deleted, or forged.

**Key Features:**
- 📜 Issue certificates on-chain with a unique keccak256 hash
- 🔍 Verify any certificate instantly using its hash
- 🚫 Revoke fraudulent or expired certificates
- 📊 Live analytics dashboard with real-time blockchain data
- 🐍 Python + Flask REST API backend
- 🌐 Clean HTML/JS frontend — no frameworks needed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Smart Contract | Solidity 0.8.19 |
| Blockchain Network | Hardhat (Local Ethereum) |
| Backend API | Python Flask + web3.py v7 |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Analytics | Chart.js |
| Hashing | keccak256 (SHA-3) |
| Node Runtime | Node.js v18+ |

---

## Project Structure

```
blockchain/
│
├── contracts/
│   └── CertificateRegistry.sol     # Core Solidity smart contract
│
├── backend/
│   ├── server.py                   # Flask REST API (6 endpoints)
│   ├── blockchain.py               # web3.py blockchain connector
│   └── requirements.txt            # Python dependencies
│
├── frontend/
│   ├── index.html                  # Main app (Issue + Verify + Records)
│   └── dashboard.html              # Live analytics dashboard
│
├── scripts/
│   └── deploy.js                   # Hardhat deploy + sample cert issuance
│
├── hardhat.config.js               # Hardhat configuration
├── package.json                    # Node.js dependencies
└── deployment.json                 # Auto-generated: contract address + cert records
```

---

## Prerequisites

Make sure you have the following installed:

```bash
# Node.js v18+
node --version   # should show v18.x.x or higher

# Python 3.10+
python3 --version

# npm
npm --version
```

---

## Installation

### 1. Clone / set up the project folder

```bash
mkdir ~/blockchain && cd ~/blockchain
# Place all project files here
```

### 2. Install Node.js dependencies

```bash
npm install
```

### 3. Install Python dependencies

```bash
pip install flask flask-cors web3 --break-system-packages
```

---

## Running the Project

You need **3 terminals** running simultaneously.

### Terminal 1 — Start the Blockchain Node

```bash
cd ~/blockchain
npx hardhat node
```

Keep this running. It starts a local Ethereum network at `http://127.0.0.1:8545` with 20 test accounts loaded with 10,000 ETH each.

### Terminal 2 — Deploy Contract + Start API

```bash
cd ~/blockchain

# Deploy the smart contract and issue 5 sample certificates
npx hardhat run scripts/deploy.js --network localhost

# Start the Flask backend API
python3 backend/server.py
```

The API runs at `http://localhost:5000`.

### Terminal 3 — Serve the Frontend

```bash
cd ~/blockchain
python3 -m http.server 8080 --directory frontend
```

Now open your browser:
- **Main App:** http://localhost:8080/index.html
- **Dashboard:** http://localhost:8080/dashboard.html

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Blockchain connection status + stats |
| GET | `/api/certificates` | List all issued certificates |
| POST | `/api/certificates/issue` | Issue a new certificate on-chain |
| GET | `/api/certificates/verify/:hash` | Verify a certificate by hash |
| POST | `/api/certificates/revoke` | Revoke a certificate |
| GET | `/api/stats` | Live blockchain statistics |

### Example — Issue a Certificate

```bash
curl -X POST http://localhost:5000/api/certificates/issue \
  -H "Content-Type: application/json" \
  -d '{
    "studentName": "Arjun Sharma",
    "rollNumber": "CS2021001",
    "degree": "B.Tech Computer Science",
    "institution": "XYZ Institute of Technology"
  }'
```

### Example — Verify a Certificate

```bash
curl http://localhost:5000/api/certificates/verify/0xbb212cd185800067de5bcb7891f8aeff51a04ab3759ae219b532f37dd7e3ea1b
```

---

## Smart Contract

**File:** `contracts/CertificateRegistry.sol`

### Key Functions

| Function | Access | Description |
|---|---|---|
| `issueCertificate()` | Admin only | Generates keccak256 hash, stores certificate on-chain |
| `getCertificate(hash)` | Public | Returns full certificate details |
| `verifyCertificate(hash)` | Public | Returns validity status |
| `revokeCertificate(hash, reason)` | Admin only | Sets isValid = false |
| `getStats()` | Public | Returns totalIssued and totalVerified |
| `getStudentCertificates(roll)` | Public | Returns all certificate hashes for a roll number |

### Certificate Hash Generation

```solidity
bytes32 certHash = keccak256(abi.encodePacked(
    _studentName,
    _rollNumber,
    _degree,
    _institution,
    block.timestamp,
    block.number
));
```

The hash is unique to each certificate — any change in any field produces a completely different hash.

---

## How It Works

```
1. ISSUE
   Admin fills form → POST /api/certificates/issue
   → Flask calls contract.issueCertificate() via web3.py
   → Hardhat mines a new block
   → keccak256 hash stored immutably on-chain
   → Hash returned to frontend

2. VERIFY
   User pastes hash → GET /api/certificates/verify/:hash
   → Flask calls contract.getCertificate() via web3.py
   → If exists: returns name, degree, date, isValid ✅
   → If not exists: "NOT FOUND — may be FRAUDULENT" ❌

3. REVOKE
   Admin sends hash + reason → POST /api/certificates/revoke
   → contract.revokeCertificate() sets isValid = false
   → Future verifications show "REVOKED"
```

---

## Important Note

⚠️ **Every time you restart `npx hardhat node`, you must redeploy the contract:**

```bash
npx hardhat run scripts/deploy.js --network localhost
```

This is because Hardhat starts a fresh blockchain on every restart. In production on a real network (Ethereum mainnet or testnet), this would not be needed — the contract lives permanently on-chain.

---

## Sample Certificate Hashes (after deployment)

After running `deploy.js`, check `deployment.json` for the actual hashes. Example:

```
Arjun Sharma  (CS2021001) → 0xbb212cd185800067de5bcb7891f8aeff51a04ab3759ae219b532f37dd7e3ea1b
Priya Kaur    (CS2021002) → 0xefba9329fe486ccd590ec539f9102828ecce01f0699f6fb7d87c8273e06274a7
Rahul Verma   (EC2021003) → 0xfe9c5398cddb940edde99b3ddd82bf703c92498e99c0c8d2221922d0305afe81
Sneha Patel   (ME2021004) → 0x2a6676edb6a11db72276452e104215bcf71951f7cd016505d59df0ebbaed8858
Vikram Singh  (CS2020005) → 0x3465d89ed6d7bfbc354069297f66f0a1f9a13753dfe3acbb55772ee1c24a3068
```

Use any of these in the Verify tab to see a ✅ VALID result.

---

## License

MIT License — Free to use for academic purposes.

---

*Built with ❤️ using Solidity, Hardhat, Flask, and web3.py*