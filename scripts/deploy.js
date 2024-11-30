const { ethers } = require("hardhat");

async function main() {
    // Step 1: Deploy SPARKToken
    console.log("Deploying SPARKToken...");
    const SPARKToken = await ethers.getContractFactory("SPARKToken");
    const initialSupply = ethers.parseEther("1000000"); // 1 million tokens
    const sparkToken = await SPARKToken.deploy(initialSupply);

    // Use 'target' instead of 'address'
    console.log("Deployed SPARKToken:", sparkToken);

    if (!sparkToken.target) {
        throw new Error("SPARKToken deployment failed; address is undefined.");
    }
    console.log(`SPARKToken deployed to: ${sparkToken.target}`);

    // Step 2: Deploy EnergyTrading with the SPARKToken address
    console.log("Deploying EnergyTrading...");
    const EnergyTrading = await ethers.getContractFactory("EnergyTrading");
    const energyTrading = await EnergyTrading.deploy(sparkToken.target);

    if (!energyTrading.target) {
        throw new Error("EnergyTrading deployment failed; address is undefined.");
    }
    console.log(`EnergyTrading deployed to: ${energyTrading.target}`);

    // Save deployment addresses to a JSON file for use in your app/tests
    const fs = require("fs");
    const deploymentData = {
        SPARKToken: sparkToken.target,
        EnergyTrading: energyTrading.target,
    };
    fs.writeFileSync("deployment.json", JSON.stringify(deploymentData, null, 2));
    console.log("Deployment information saved to deployment.json");
}

// Run the deployment
main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
