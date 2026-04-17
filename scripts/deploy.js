// scripts/deploy.js
// Run with: npx hardhat run scripts/deploy.js --network localhost

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("=================================================");
  console.log("  Deploying Certificate Registry Smart Contract");
  console.log("=================================================\n");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying with account: ${deployer.address}`);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`Account balance: ${ethers.formatEther(balance)} ETH\n`);

  // Deploy contract
  console.log("Deploying CertificateRegistry...");
  const CertificateRegistry = await ethers.getContractFactory("CertificateRegistry");
  const registry = await CertificateRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log(`✅ Contract deployed at: ${contractAddress}\n`);

  // Demo: Issue sample certificates
  console.log("Issuing sample certificates...\n");

  const sampleCerts = [
    { name: "Arjun Sharma",    roll: "CS2021001", degree: "B.Tech Computer Science",    inst: "XYZ Institute of Technology" },
    { name: "Priya Kaur",      roll: "CS2021002", degree: "B.Tech Information Technology", inst: "XYZ Institute of Technology" },
    { name: "Rahul Verma",     roll: "EC2021003", degree: "B.Tech Electronics",          inst: "XYZ Institute of Technology" },
    { name: "Sneha Patel",     roll: "ME2021004", degree: "B.Tech Mechanical Engineering", inst: "XYZ Institute of Technology" },
    { name: "Vikram Singh",    roll: "CS2020005", degree: "M.Tech AI & ML",              inst: "XYZ Institute of Technology" },
  ];

  const deployedData = {
    contractAddress,
    deployer: deployer.address,
    certificates: [],
    deployedAt: new Date().toISOString(),
    network: "localhost"
  };

  for (const cert of sampleCerts) {
    const tx = await registry.issueCertificate(
      cert.name, cert.roll, cert.degree, cert.inst
    );
    const receipt = await tx.wait();

    // Extract certHash from emitted event
    const event = receipt.logs
      .map(log => { try { return registry.interface.parseLog(log); } catch { return null; } })
      .find(e => e && e.name === "CertificateIssued");

    const certHash = event ? event.args.certHash : "N/A";

    console.log(`✅ Issued: ${cert.name} (${cert.roll})`);
    console.log(`   Hash: ${certHash}\n`);

    deployedData.certificates.push({
      ...cert,
      hash: certHash,
      issuedAt: new Date().toISOString()
    });
  }

  // Save deployment info to JSON (used by frontend and Python scripts)
  fs.writeFileSync(
    "./deployment.json",
    JSON.stringify(deployedData, null, 2)
  );
  console.log("📁 Deployment info saved to deployment.json");

  // Print stats
  const [issued, verified] = await registry.getStats();
  console.log(`\n📊 Total Certificates Issued: ${issued}`);
  console.log(`📊 Total Verifications Done: ${verified}`);
  console.log("\n=================================================");
  console.log("  Deployment Complete! ✅");
  console.log("=================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
