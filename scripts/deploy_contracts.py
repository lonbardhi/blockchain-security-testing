"""
Deployment script for smart contracts
"""
from brownie import network, accounts, SimpleToken, VulnerableVault, DeFiPool, AuctionContract, NFTMarketplace, TokenSale, SecureVault
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
    
    # Fund vault for testing
    fund_amount = "10 ether"
    deployer.transfer(vault.address, fund_amount)
    print(f"💰 Funded vault with {fund_amount}")
    print(f"Vault balance: {vault.balance()}")
    
    return vault


def deploy_secure_vault():
    """Deploy SecureVault contract"""
    print("🚀 Deploying SecureVault...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    vault = SecureVault.deploy({"from": deployer})
    
    print(f"✅ SecureVault deployed at: {vault.address}")
    print(f"Owner: {vault.owner()}")
    
    # Fund vault for testing
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


def deploy_auction_contract():
    """Deploy AuctionContract"""
    print("🚀 Deploying AuctionContract...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    auction = AuctionContract.deploy({"from": deployer})
    
    print(f"✅ AuctionContract deployed at: {auction.address}")
    print(f"Next auction ID: {auction.nextAuctionId()}")
    
    # Fund contract for testing
    fund_amount = "5 ether"
    deployer.transfer(auction.address, fund_amount)
    print(f"💰 Funded auction contract with {fund_amount}")
    print(f"Contract balance: {auction.address.balance()}")
    
    return auction


def deploy_nft_marketplace():
    """Deploy NFTMarketplace"""
    print("🚀 Deploying NFTMarketplace...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    marketplace = NFTMarketplace.deploy({"from": deployer})
    
    print(f"✅ NFTMarketplace deployed at: {marketplace.address}")
    print(f"Marketplace fee: {marketplace.marketplaceFee()}")
    
    return marketplace


def deploy_token_sale():
    """Deploy TokenSale"""
    print("🚀 Deploying TokenSale...")
    
    deployer = accounts[0]
    print(f"Deploying from: {deployer.address}")
    
    # Deploy contract
    token_sale = TokenSale.deploy(
        accounts[1],  # Mock token address
        accounts[0],  # Wallet
        block.timestamp + 3600,  # Start in 1 hour
        86400,  # 24 hour duration
        {"from": deployer}
    )
    
    print(f"✅ TokenSale deployed at: {token_sale.address}")
    print(f"Token address: {token_sale.token()}")
    print(f"Wallet: {token_sale.wallet()}")
    print(f"Sale start time: {token_sale.saleStartTime()}")
    print(f"Sale end time: {token_sale.saleEndTime()}")
    
    # Create sale tier
    token_sale.createSaleTier(
        1,  # Tier ID
        1000,  # Rate (1000 tokens per ETH)
        0.1 ether,  # Min purchase
        10 ether,  # Max purchase
        100 ether,  # Hard cap
        {"from": deployer}
    )
    
    # Start sale
    token_sale.startSale({"from": deployer})
    print("✅ Token sale started")
    
    return token_sale


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
        vulnerable_vault = deploy_vulnerable_vault()
        deployed_contracts["VulnerableVault"] = {
            "address": vulnerable_vault.address,
            "owner": vulnerable_vault.owner(),
            "balance": str(vulnerable_vault.balance())
        }
        
        # Deploy SecureVault
        secure_vault = deploy_secure_vault()
        deployed_contracts["SecureVault"] = {
            "address": secure_vault.address,
            "owner": secure_vault.owner(),
            "balance": str(secure_vault.balance())
        }
        
        # Deploy AuctionContract
        auction = deploy_auction_contract()
        deployed_contracts["AuctionContract"] = {
            "address": auction.address,
            "next_auction_id": str(auction.nextAuctionId())
        }
        
        # Deploy NFTMarketplace
        marketplace = deploy_nft_marketplace()
        deployed_contracts["NFTMarketplace"] = {
            "address": marketplace.address,
            "marketplace_fee": str(marketplace.marketplaceFee())
        }
        
        # Deploy TokenSale
        token_sale = deploy_token_sale()
        deployed_contracts["TokenSale"] = {
            "address": token_sale.address,
            "token": token_sale.token(),
            "wallet": token_sale.wallet(),
            "sale_active": token_sale.saleActive()
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
    vulnerable_vault_address = contracts["VulnerableVault"]["address"]
    vulnerable_vault = VulnerableVault.at(vulnerable_vault_address)
    
    secure_vault_address = contracts["SecureVault"]["address"]
    secure_vault = SecureVault.at(secure_vault_address)
    
    # Make deposits to vaults
    for i, account in enumerate(test_accounts):
        amount = (i + 1) * 1 ether
        
        # Deposit to vulnerable vault
        vulnerable_vault.deposit({"from": account, "value": amount})
        print(f"💰 Deposited {amount} ETH to vulnerable vault from {account.address}")
        
        # Deposit to secure vault
        secure_vault.deposit({"from": account, "value": amount})
        print(f"💰 Deposited {amount} ETH to secure vault from {account.address}")
    
    print(f"Final vulnerable vault balance: {vulnerable_vault.balance()}")
    print(f"Final secure vault balance: {secure_vault.balance()}")
    
    # Setup auction scenarios
    auction_address = contracts["AuctionContract"]["address"]
    auction = AuctionContract.at(auction_address)
    
    # Create test auctions
    for i, account in enumerate(test_accounts):
        auction_id = auction.createAuction(
            f"Test Auction {i+1}",
            1000,  # 1000 blocks duration
            0.1 ether,  # Min bid increment
            {"from": account}
        )
        print(f"🏛️ Created auction {auction_id} by {account.address}")
    
    # Save test setup info
    setup_info = {
        "test_accounts": [str(account.address) for account in test_accounts],
        "token_balances": {
            str(account.address): str(token.balanceOf(account)) 
            for account in test_accounts
        },
        "vulnerable_vault_balances": {
            str(account.address): str(vulnerable_vault.balances(account)) 
            for account in test_accounts
        },
        "secure_vault_balances": {
            str(account.address): str(secure_vault.balances(account)) 
            for account in test_accounts
        },
        "vulnerable_vault_total_balance": str(vulnerable_vault.balance()),
        "secure_vault_total_balance": str(secure_vault.balance()),
        "auctions_created": len(test_accounts)
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
    print("Run: brownie test tests/test_sample_contracts.py")
