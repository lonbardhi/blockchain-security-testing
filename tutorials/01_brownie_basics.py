"""
Brownie Basics Tutorial - Step-by-Step Examples
Run this script in Brownie console: brownie run tutorials/01_brownie_basics.py
"""

from brownie import accounts, network, SimpleToken, VulnerableVault
import json


def demo_basics():
    """Demonstrate Brownie basics"""
    print("🎓 Brownie Basics Tutorial")
    print("=" * 50)
    
    # 1. Account Management
    print("\n1️⃣ Account Management")
    print("-" * 30)
    
    # Show available accounts
    print(f"Available accounts: {len(accounts)}")
    print(f"First account: {accounts[0].address}")
    print(f"Account balance: {accounts[0].balance() / 1e18} ETH")
    
    # Show network info
    print(f"Current network: {network.show_active()}")
    
    return accounts[0]


def demo_contract_deployment(deployer):
    """Demonstrate contract deployment"""
    print("\n2️⃣ Contract Deployment")
    print("-" * 30)
    
    # Deploy SimpleToken
    print("🚀 Deploying SimpleToken...")
    token = SimpleToken.deploy(
        "Tutorial Token",
        "TUT",
        1000000 * 10**18,  # 1 million tokens
        {"from": deployer}
    )
    
    print(f"✅ Token deployed at: {token.address}")
    print(f"Token name: {token.name()}")
    print(f"Token symbol: {token.symbol()}")
    print(f"Total supply: {token.totalSupply() / 1e18} TUT")
    print(f"Deployer balance: {token.balanceOf(deployer) / 1e18} TUT")
    
    # Deploy VulnerableVault
    print("\n🚀 Deploying VulnerableVault...")
    vault = VulnerableVault.deploy({"from": deployer})
    
    print(f"✅ Vault deployed at: {vault.address}")
    print(f"Vault owner: {vault.owner()}")
    print(f"Vault balance: {vault.balance() / 1e18} ETH")
    
    # Fund vault for testing
    fund_amount = "10 ether"
    deployer.transfer(vault.address, fund_amount)
    print(f"💰 Funded vault with {fund_amount}")
    print(f"Vault balance: {vault.balance() / 1e18} ETH")
    
    return token, vault


def demo_basic_operations(token, vault, deployer):
    """Demonstrate basic contract operations"""
    print("\n3️⃣ Basic Contract Operations")
    print("-" * 30)
    
    # Get test accounts
    user1 = accounts[1]
    user2 = accounts[2]
    
    print(f"User1: {user1.address}")
    print(f"User2: {user2.address}")
    
    # Token operations
    print("\n🪙 Token Operations:")
    
    # Transfer tokens to user1
    transfer_amount = 1000 * 10**18  # 1000 tokens
    tx = token.transfer(user1, transfer_amount, {"from": deployer})
    
    print(f"✅ Transferred {transfer_amount / 1e18} TUT to User1")
    print(f"User1 balance: {token.balanceOf(user1) / 1e18} TUT")
    print(f"Transaction gas used: {tx.gas_used}")
    
    # User1 transfers to user2
    transfer_amount2 = 500 * 10**18  # 500 tokens
    tx2 = token.transfer(user2, transfer_amount2, {"from": user1})
    
    print(f"✅ User1 transferred {transfer_amount2 / 1e18} TUT to User2")
    print(f"User1 balance: {token.balanceOf(user1) / 1e18} TUT")
    print(f"User2 balance: {token.balanceOf(user2) / 1e18} TUT")
    print(f"Transaction gas used: {tx2.gas_used}")
    
    # Vault operations
    print("\n🏦 Vault Operations:")
    
    # User1 deposits to vault
    deposit_amount = "2 ether"
    tx3 = vault.deposit({"from": user1, "value": deposit_amount})
    
    print(f"✅ User1 deposited {deposit_amount} ETH to vault")
    print(f"User1 vault balance: {vault.balances(user1) / 1e18} ETH")
    print(f"Vault total balance: {vault.balance() / 1e18} ETH")
    print(f"Transaction gas used: {tx3.gas_used}")
    
    # User1 withdraws from vault
    withdraw_amount = "1 ether"
    tx4 = vault.withdraw(withdraw_amount, {"from": user1})
    
    print(f"✅ User1 withdrew {withdraw_amount} ETH from vault")
    print(f"User1 vault balance: {vault.balances(user1) / 1e18} ETH")
    print(f"User1 wallet balance: {user1.balance() / 1e18} ETH")
    print(f"Transaction gas used: {tx4.gas_used}")
    
    return user1, user2


def demo_error_handling(token, user1, user2):
    """Demonstrate error handling"""
    print("\n4️⃣ Error Handling")
    print("-" * 30)
    
    print("🧪 Testing error conditions...")
    
    # Test insufficient balance transfer
    try:
        # Try to transfer more than user2 has
        large_amount = 10000 * 10**18  # 10,000 tokens
        token.transfer(user1, large_amount, {"from": user2})
        print("❌ Transfer should have failed!")
    except Exception as e:
        print(f"✅ Transfer correctly failed: {e}")
    
    # Test vault withdrawal with insufficient balance
    try:
        # Try to withdraw more than user1 has in vault
        large_withdraw = "10 ether"
        vault.withdraw(large_withdraw, {"from": user1})
        print("❌ Withdrawal should have failed!")
    except Exception as e:
        print(f"✅ Withdrawal correctly failed: {e}")
    
    # Test zero transfer
    try:
        token.transfer(user2, 0, {"from": user1})
        print("✅ Zero transfer succeeded")
    except Exception as e:
        print(f"❌ Zero transfer failed: {e}")


def demo_transaction_analysis():
    """Demonstrate transaction analysis"""
    print("\n5️⃣ Transaction Analysis")
    print("-" * 30)
    
    deployer = accounts[0]
    user1 = accounts[1]
    
    # Deploy fresh token for analysis
    token = SimpleToken.deploy("Analysis Token", "ANA", 1000000 * 10**18, {"from": deployer})
    
    # Perform transaction
    transfer_amount = 100 * 10**18
    tx = token.transfer(user1, transfer_amount, {"from": deployer})
    
    print("📊 Transaction Analysis:")
    print(f"Transaction hash: {tx.txid}")
    print(f"Block number: {tx.block_number}")
    print(f"Gas used: {tx.gas_used}")
    print(f"Gas price: {tx.gas_price / 1e9} gwei")
    print(f"Transaction cost: {tx.cost() / 1e18} ETH")
    
    # Show events
    print("\n📝 Events emitted:")
    for event in tx.events:
        print(f"  - {event['name']}: {event}")
    
    # Show contract state changes
    print(f"\n📈 State Changes:")
    print(f"  - Deployer token balance: {token.balanceOf(deployer) / 1e18} ANA")
    print(f"  - User1 token balance: {token.balanceOf(user1) / 1e18} ANA")


def demo_gas_analysis():
    """Demonstrate gas analysis"""
    print("\n6️⃣ Gas Analysis")
    print("-" * 30)
    
    deployer = accounts[0]
    
    # Deploy contracts
    token = SimpleToken.deploy("Gas Test Token", "GAS", 1000000 * 10**18, {"from": deployer})
    vault = VulnerableVault.deploy({"from": deployer})
    
    print("⛽ Gas Usage Analysis:")
    
    # Token operations gas usage
    transfer_tx = token.transfer(accounts[1], 100 * 10**18, {"from": deployer})
    approve_tx = token.approve(accounts[1], 1000 * 10**18, {"from": deployer})
    
    print(f"  - Token transfer: {transfer_tx.gas_used} gas")
    print(f"  - Token approve: {approve_tx.gas_used} gas")
    
    # Vault operations gas usage
    deployer.transfer(vault.address, "5 ether")
    deposit_tx = vault.deposit({"from": accounts[1], "value": "1 ether"})
    withdraw_tx = vault.withdraw("0.5 ether", {"from": accounts[1]})
    
    print(f"  - Vault deposit: {deposit_tx.gas_used} gas")
    print(f"  - Vault withdraw: {withdraw_tx.gas_used} gas")
    
    # Contract deployment gas usage
    print(f"  - Token deployment: {token.tx.gas_used} gas")
    print(f"  - Vault deployment: {vault.tx.gas_used} gas")


def demo_testing_patterns():
    """Demonstrate testing patterns"""
    print("\n7️⃣ Testing Patterns")
    print("-" * 30)
    
    deployer = accounts[0]
    user1 = accounts[1]
    
    # Deploy token
    token = SimpleToken.deploy("Test Token", "TEST", 1000000 * 10**18, {"from": deployer})
    
    print("🧪 Testing Pattern Examples:")
    
    # Pattern 1: Arrange-Act-Assert
    print("\n  Pattern 1: Arrange-Act-Assert")
    
    # Arrange
    initial_balance = token.balanceOf(user1)
    transfer_amount = 100 * 10**18
    
    # Act
    token.transfer(user1, transfer_amount, {"from": deployer})
    
    # Assert
    final_balance = token.balanceOf(user1)
    assert final_balance == initial_balance + transfer_amount
    print(f"    ✅ Balance assertion passed: {final_balance / 1e18} TEST")
    
    # Pattern 2: Error testing
    print("\n  Pattern 2: Error Testing")
    
    try:
        token.transfer(user1, 2000000 * 10**18, {"from": user1})  # Too much
        print("    ❌ Should have failed!")
    except Exception:
        print("    ✅ Error correctly caught")
    
    # Pattern 3: State comparison
    print("\n  Pattern 3: State Comparison")
    
    total_supply_before = token.totalSupply()
    token.burn(1000 * 10**18, {"from": deployer})
    total_supply_after = token.totalSupply()
    
    assert total_supply_after == total_supply_before - 1000 * 10**18
    print(f"    ✅ Supply reduction verified: {total_supply_after / 1e18} TEST")


def save_tutorial_results(results):
    """Save tutorial results to file"""
    print("\n💾 Saving tutorial results...")
    
    with open("reports/tutorial_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved to reports/tutorial_results.json")


def main():
    """Main tutorial function"""
    print("🎓 Starting Brownie Basics Tutorial")
    print("=" * 60)
    
    results = {}
    
    try:
        # 1. Account Management
        deployer = demo_basics()
        results["deployer"] = deployer.address
        
        # 2. Contract Deployment
        token, vault = demo_contract_deployment(deployer)
        results["token_address"] = token.address
        results["vault_address"] = vault.address
        
        # 3. Basic Operations
        user1, user2 = demo_basic_operations(token, vault, deployer)
        results["user1"] = user1.address
        results["user2"] = user2.address
        
        # 4. Error Handling
        demo_error_handling(token, user1, user2)
        
        # 5. Transaction Analysis
        demo_transaction_analysis()
        
        # 6. Gas Analysis
        demo_gas_analysis()
        
        # 7. Testing Patterns
        demo_testing_patterns()
        
        # Save results
        results["status"] = "completed"
        results["timestamp"] = str(network.chain)
        save_tutorial_results(results)
        
        print("\n🎉 Tutorial completed successfully!")
        print("=" * 60)
        print("📚 Next steps:")
        print("  1. Study the vulnerable contracts")
        print("  2. Run security tests: brownie test tests/test_sample_contracts.py")
        print("  3. Try writing your own tests")
        print("  4. Explore advanced features")
        
    except Exception as e:
        print(f"\n❌ Tutorial failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        save_tutorial_results(results)
        raise


if __name__ == "__main__":
    main()
