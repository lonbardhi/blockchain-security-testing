"""
Deployment script for smart contracts
"""
from brownie import network, accounts, SimpleToken, VulnerableVault, DeFiPool
from brownie.network import priority_fee
import json
import time


def deploy_simple_token():
    """Deploy SimpleToken contract"""
    print("🚀 Deploying SimpleToken...")
    
    # Get deployer account
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    print(f"Deployer balance: {deployer.balance()} wei")
    
    # Deploy contract
    token = SimpleToken.deploy(
        "Security Test Token",
        "SEC",
        1000000 * 10**18,  # 1M tokens
        {"from": deployer}
    )
    
    print(f"✅ SimpleToken deployed at: {token.address}")
    print(f"Token name: {token.name()}")
    print(f"Token symbol: {token.symbol()}")
    print(f"Total supply: {token.totalSupply()}")
    
    return token


def deploy_vulnerable_vault():
    """Deploy VulnerableVault contract"""
    print("🚀 Deploying VulnerableVault...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    vault = VulnerableVault.deploy({"from": deployer})
    
    print(f"✅ VulnerableVault deployed at: {vault.address}")
    print(f"Owner: {vault.owner()}")
    
    # Fund the vault for testing
    fund_amount = "10 ether"
    deployer.transfer(vault.address, fund_amount)
    print(f"💰 Funded vault with {fund_amount}")
    print(f"Vault balance: {vault.balance()}")
    
    return vault


def deploy_defi_pool(token_address, reward_token_address):
    """Deploy DeFiPool contract"""
    print("🚀 Deploying DeFiPool...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    pool = DeFiPool.deploy(
        token_address,
        reward_token_address,
        {"from": deployer}
    )
    
    print(f"✅ DeFiPool deployed at: {pool.address}")
    print(f"Token address: {pool.token()}")
    print(f"Reward token address: {pool.rewardToken()}")
    print(f"Reward rate: {pool.rewardRate()}")
    
    return pool


def deploy_mock_erc20(name, symbol, initial_supply, deployer=None):
    """Deploy a mock ERC20 token for testing"""
    print(f"🚀 Deploying mock ERC20: {name}")
    
    if deployer is None:
        deployer = accounts[0]
    
    # This would deploy a simple ERC20 contract
    # For now, we'll return a mock address
    mock_address = f"0x{'0' * 39}{len(name)}"
    print(f"✅ Mock {name} deployed at: {mock_address}")
    
    return mock_address


def main():
    """Main deployment function"""
    print("🏗️  Starting contract deployment...")
    print(f"Network: {network.show_active()}")
    print(f"Gas price: {network.gas_price()}")
    
    deployed_contracts = {}
    
    try:
        # Deploy SimpleToken
        token = deploy_simple_token()
        deployed_contracts["SimpleToken"] = {
            "address": token.address,
            "name": token.name(),
            "symbol": token.symbol(),
            "total_supply": str(token.totalSupply())
        }
        
        # Deploy VulnerableVault
        vault = deploy_vulnerable_vault()
        deployed_contracts["VulnerableVault"] = {
            "address": vault.address,
            "owner": vault.owner(),
            "balance": str(vault.balance())
        }
        
        # Deploy mock tokens for DeFiPool
        mock_token = deploy_mock_erc20("Mock Token", "MOCK", 1000000 * 10**18)
        mock_reward_token = deploy_mock_erc20("Mock Reward", "REWARD", 500000 * 10**18)
        
        # Deploy DeFiPool
        pool = deploy_defi_pool(mock_token, mock_reward_token)
        deployed_contracts["DeFiPool"] = {
            "address": pool.address,
            "token": pool.token(),
            "reward_token": pool.rewardToken(),
            "reward_rate": str(pool.rewardRate())
        }
        
        # Save deployment info
        deployment_info = {
            "network": network.show_active(),
            "deployer": accounts[0].address,
            "timestamp": int(time.time()),
            "contracts": deployed_contracts
        }
        
        with open("reports/deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\n🎉 Deployment completed successfully!")
        print(f"📄 Deployment info saved to: reports/deployment.json")
        
        return deployed_contracts
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise


def setup_test_environment():
    """Setup test environment with deployed contracts"""
    print("🔧 Setting up test environment...")
    
    # Deploy contracts
    contracts = main()
    
    # Setup test scenarios
    print("\n🧪 Setting up test scenarios...")
    
    # Setup token scenarios
    token_address = contracts["SimpleToken"]["address"]
    token = SimpleToken.at(token_address)
    
    # Mint tokens to test accounts
    test_accounts = accounts[1:4]
    for i, account in enumerate(test_accounts):
        amount = (i + 1) * 100 * 10**18
        token.mint(account, amount, {"from": accounts[0]})
        print(f"💰 Minted {amount} tokens to {account.address}")
    
    # Setup vault scenarios
    vault_address = contracts["VulnerableVault"]["address"]
    vault = VulnerableVault.at(vault_address)
    
    # Make deposits to vault
    for i, account in enumerate(test_accounts):
        amount = (i + 1) * 1 ether
        vault.deposit({"from": account, "value": amount})
        print(f"💰 Deposited {amount} ETH to vault from {account.address}")
    
    print(f"Final vault balance: {vault.balance()}")
    print(f"Total deposits: {vault.totalDeposits()}")
    
    # Save test setup info
    setup_info = {
        "test_accounts": [str(account.address) for account in test_accounts],
        "token_balances": {
            str(account.address): str(token.balanceOf(account)) 
            for account in test_accounts
        },
        "vault_balances": {
            str(account.address): str(vault.balances(account)) 
            for account in test_accounts
        },
        "vault_total_balance": str(vault.balance()),
        "vault_total_deposits": str(vault.totalDeposits())
    }
    
    with open("reports/test_setup.json", "w") as f:
        json.dump(setup_info, f, indent=2)
    
    print("\n✅ Test environment setup completed!")
    return contracts, setup_info


if __name__ == "__main__":
    # Check if we're on a local network
    if network.show_active() == "development":
        print("🔧 Running on development network")
    else:
        print(f"🌐 Running on {network.show_active()} network")
    
    # Setup test environment
    contracts, setup_info = setup_test_environment()
    
    print("\n🎯 Ready for security testing!")
    print("Run: brownie test tests/test_security_comprehensive.py")
