"""
interact.py — Python client for CertificateRegistry smart contract
Compatible with web3.py v7
Run: python3 interact.py
Make sure: npx hardhat node is running in another terminal
"""

import json
import sys
from datetime import datetime

from web3 import Web3

# ── Config ─────────────────────────────────────────────────────────────────────
RPC_URL         = "http://127.0.0.1:8545"
DEPLOYMENT_FILE = "./deployment.json"

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_studentName", "type": "string"},
            {"internalType": "string", "name": "_rollNumber",  "type": "string"},
            {"internalType": "string", "name": "_degree",      "type": "string"},
            {"internalType": "string", "name": "_institution", "type": "string"},
        ],
        "name": "issueCertificate",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "_certHash", "type": "bytes32"}],
        "name": "getCertificate",
        "outputs": [
            {"internalType": "string",  "name": "studentName",  "type": "string"},
            {"internalType": "string",  "name": "rollNumber",   "type": "string"},
            {"internalType": "string",  "name": "degree",       "type": "string"},
            {"internalType": "string",  "name": "institution",  "type": "string"},
            {"internalType": "uint256", "name": "issueDate",    "type": "uint256"},
            {"internalType": "bool",    "name": "isValid",      "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_certHash", "type": "bytes32"},
            {"internalType": "string",  "name": "_reason",   "type": "string"},
        ],
        "name": "revokeCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getStats",
        "outputs": [
            {"internalType": "uint256", "name": "issued",   "type": "uint256"},
            {"internalType": "uint256", "name": "verified", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "_rollNumber", "type": "string"}],
        "name": "getStudentCertificates",
        "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def divider(char="═", width=60):
    print(char * width)

def banner():
    divider()
    print("  🎓  Certificate Verification System — Python Client")
    print("  🔗  Connected to: Hardhat Local Blockchain")
    divider()

def connect():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print(f"\n❌  Cannot connect to Hardhat node at {RPC_URL}")
        print("    Make sure Terminal 1 is running: npx hardhat node\n")
        sys.exit(1)
    print(f"\n✅  Connected to blockchain")
    print(f"    Chain ID  : {w3.eth.chain_id}")
    print(f"    Block No  : {w3.eth.block_number}")
    print(f"    Accounts  : {len(w3.eth.accounts)}")
    return w3

def load_contract(w3):
    try:
        with open(DEPLOYMENT_FILE) as f:
            deployment = json.load(f)
    except FileNotFoundError:
        print(f"\n❌  {DEPLOYMENT_FILE} not found.")
        print("    Run: npx hardhat run deploy.js --network localhost\n")
        sys.exit(1)

    address = deployment["contractAddress"]
    contract = w3.eth.contract(address=address, abi=CONTRACT_ABI)
    print(f"    Contract  : {address}\n")
    return contract, deployment, w3.eth.accounts[0]

def hash_to_bytes(hash_str):
    """Convert 0x... hex string to bytes32."""
    return bytes.fromhex(hash_str[2:] if hash_str.startswith("0x") else hash_str)

def bytes_to_hash(b):
    """Convert bytes32 to 0x... string."""
    return "0x" + b.hex()

def format_timestamp(ts):
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")


# ── Actions ────────────────────────────────────────────────────────────────────

def show_existing_certs(deployment):
    print("📋  Certificates issued during deployment:\n")
    for i, cert in enumerate(deployment.get("certificates", []), 1):
        short = cert["hash"][:20] + "..." + cert["hash"][-6:]
        print(f"  {i}. {cert['name']:<20}  {cert['roll']:<12}  {cert['degree']}")
        print(f"     Hash: {short}\n")

def verify_certificate(contract, cert_hash_str):
    print(f"\n🔍  Verifying certificate...")
    print(f"    Hash: {cert_hash_str[:20]}...{cert_hash_str[-6:]}\n")
    try:
        cert_bytes = hash_to_bytes(cert_hash_str)
        result = contract.functions.getCertificate(cert_bytes).call()
        name, roll, degree, institution, issue_date, is_valid = result

        status = "✅  VALID" if is_valid else "❌  REVOKED"
        print(f"    Status      : {status}")
        print(f"    Student     : {name}")
        print(f"    Roll No     : {roll}")
        print(f"    Degree      : {degree}")
        print(f"    Institution : {institution}")
        print(f"    Issued On   : {format_timestamp(issue_date)}")
        return True
    except Exception as e:
        if "Certificate does not exist" in str(e) or "execution reverted" in str(e):
            print("    ❌  INVALID — Certificate NOT found on blockchain")
            print("        This document may be FRAUDULENT.")
        else:
            print(f"    Error: {e}")
        return False

def issue_new_certificate(contract, account, name, roll, degree, inst):
    print(f"\n📜  Issuing certificate for {name}...")
    try:
        tx_hash = contract.functions.issueCertificate(
            name, roll, degree, inst
        ).transact({"from": account})

        receipt = contract.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"    ✅  Transaction confirmed!")
        print(f"    Block     : #{receipt['blockNumber']}")
        print(f"    Gas Used  : {receipt['gasUsed']}")
        print(f"    TX Hash   : {tx_hash.hex()[:20]}...")
        return True
    except Exception as e:
        print(f"    ❌  Failed: {e}")
        return False

def get_stats(contract):
    issued, verified = contract.functions.getStats().call()
    print(f"\n📊  Blockchain Statistics:")
    print(f"    Total Issued    : {issued}")
    print(f"    Total Verified  : {verified}")

def revoke_certificate(contract, account, cert_hash_str, reason):
    print(f"\n🚫  Revoking certificate...")
    try:
        cert_bytes = hash_to_bytes(cert_hash_str)
        tx_hash = contract.functions.revokeCertificate(
            cert_bytes, reason
        ).transact({"from": account})
        contract.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"    ✅  Certificate revoked. Reason: {reason}")
    except Exception as e:
        print(f"    ❌  Failed: {e}")


# ── Main Demo ──────────────────────────────────────────────────────────────────

def main():
    banner()

    # Connect
    w3        = connect()
    contract, deployment, admin = load_contract(w3)

    # Show existing certs from deployment
    show_existing_certs(deployment)

    # ── Demo 1: Verify a REAL certificate ──
    divider("─")
    print("DEMO 1 — Verify a REAL certificate (from deployment)")
    divider("─")
    real_hash = deployment["certificates"][0]["hash"]
    verify_certificate(contract, real_hash)

    # ── Demo 2: Verify a FAKE certificate ──
    print()
    divider("─")
    print("DEMO 2 — Verify a FAKE / tampered certificate")
    divider("─")
    fake_hash = "0x" + "deadbeef" * 8
    verify_certificate(contract, fake_hash)

    # ── Demo 3: Issue a NEW certificate ──
    print()
    divider("─")
    print("DEMO 3 — Issue a NEW certificate on-chain")
    divider("─")
    issue_new_certificate(
        contract, admin,
        name   = "Manpreet Kaur",
        roll   = "CS2022010",
        degree = "B.Tech Computer Science",
        inst   = "XYZ Institute of Technology"
    )

    # ── Demo 4: Verify all existing certs ──
    print()
    divider("─")
    print("DEMO 4 — Verify ALL deployed certificates")
    divider("─")
    for cert in deployment["certificates"]:
        name  = cert["name"]
        hsh   = cert["hash"]
        short = hsh[:14] + "..." + hsh[-6:]
        try:
            cb     = hash_to_bytes(hsh)
            result = contract.functions.getCertificate(cb).call()
            status = "✅ VALID" if result[5] else "❌ REVOKED"
        except Exception:
            status = "❌ NOT FOUND"
        print(f"  {status}  {name:<22}  {short}")

    # ── Stats ──
    print()
    get_stats(contract)

    print()
    divider()
    print("  All demos complete! Blockchain is fully functional. 🚀")
    divider()


if __name__ == "__main__":
    main()
