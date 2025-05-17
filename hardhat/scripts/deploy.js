async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying with:", deployer.address);
  
    const Voting = await ethers.getContractFactory("SimpleVoting");
    const contract = await Voting.deploy();  
  
    await contract.waitForDeployment();
  
    console.log("Contract deployed at:", await contract.getAddress());
  }
  
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
  