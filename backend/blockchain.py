"""
blockchain.py — web3.py v7 connector for CertificateRegistry
"""

import json
import os
from datetime import datetime
from web3 import Web3

DEPLOYMENT_FILE = os.path.join(os.path.dirname(__file__), "../deployment.json")
RPC_URL = "http://127.0.0.1:8545"

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
    {
        "inputs": [],
        "name": "admin",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class BlockchainClient:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {RPC_URL}")

        with open(DEPLOYMENT_FILE) as f:
            deployment = json.load(f)

        self.contract_address = deployment["contractAddress"]
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=CONTRACT_ABI
        )
        self.admin = self.w3.eth.accounts[0]

    def _hash_to_bytes(self, hash_str):
        h = hash_str[2:] if hash_str.startswith("0x") else hash_str
        return bytes.fromhex(h)

    def _bytes_to_hash(self, b):
        return "0x" + (b.hex() if isinstance(b, (bytes, bytearray)) else bytes(b).hex())

    def issue_certificate(self, name, roll, degree, institution):
        # Write on-chain
        tx_hash = self.contract.functions.issueCertificate(
            name, roll, degree, institution
        ).transact({"from": self.admin, "gas": 500000})

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # PRIMARY: get hash from raw topic[1] (certHash is first indexed param)
        cert_hash = None
        try:
            raw_topic = receipt["logs"][0]["topics"][1]
            cert_hash = "0x" + bytes(raw_topic).hex()
            print(f"[DEBUG] hash from topic: {cert_hash}")
        except Exception as e:
            print(f"[DEBUG] topic failed: {e}")

        # FALLBACK: use getStudentCertificates to find the latest hash for this roll
        if not cert_hash or cert_hash == "0x" + "0" * 64:
            try:
                hashes = self.contract.functions.getStudentCertificates(roll).call()
                if hashes:
                    cert_hash = self._bytes_to_hash(hashes[-1])
                    print(f"[DEBUG] hash from getStudentCertificates: {cert_hash}")
            except Exception as e:
                print(f"[DEBUG] fallback failed: {e}")

        return {
            "certHash": cert_hash or "0x" + "0" * 64,
            "transactionHash": "0x" + bytes(receipt["transactionHash"]).hex(),
            "blockNumber": receipt["blockNumber"],
            "gasUsed": receipt["gasUsed"],
        }

    def get_certificate(self, cert_hash):
        cert_bytes = self._hash_to_bytes(cert_hash)
        result = self.contract.functions.getCertificate(cert_bytes).call()
        name, roll, degree, inst, issue_ts, is_valid = result
        return {
            "studentName": name,
            "rollNumber": roll,
            "degree": degree,
            "institution": inst,
            "issueDate": datetime.fromtimestamp(int(issue_ts)).strftime("%Y-%m-%d %H:%M:%S"),
            "isValid": is_valid,
        }

    def revoke_certificate(self, cert_hash, reason):
        cert_bytes = self._hash_to_bytes(cert_hash)
        tx_hash = self.contract.functions.revokeCertificate(
            cert_bytes, reason
        ).transact({"from": self.admin, "gas": 100000})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_stats(self):
        return self.contract.functions.getStats().call()

    def get_student_certificates(self, roll_number):
        result = self.contract.functions.getStudentCertificates(roll_number).call()
        return [self._bytes_to_hash(h) for h in result]