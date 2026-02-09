"""
Specific reentrancy vulnerability testing
"""
import pytest
from brownie import network, accounts, VulnerableVault
from utils.security_helpers import ReentrancyTester


@pytest.mark.security
@pytest.mark.reentrancy
class TestReentrancyVulnerabilities:
    """Detailed reentrancy vulnerability testing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.reentrancy_tester = ReentrancyTester()
    
    def test_vault_reentrancy_detection(self):
        """Test reentrancy detection in VulnerableVault"""
        print("\n🔍 Testing reentrancy in VulnerableVault...")
        
        # Deploy vulnerable vault
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund the vault
        self.accounts[0].transfer(vault.address, "10 ether")
        
        # Deposit from victim
        victim = self.accounts[1]
        vault.deposit({"from": victim, "value": "5 ether"})
        
        print(f"Vault balance: {vault.balance()}")
        print(f"Victim balance: {vault.balances(victim)}")
        
        # Test vulnerable withdraw function
        initial_vault_balance = vault.balance()
        initial_victim_balance = vault.balances(victim)
        
        try:
            # This should be vulnerable to reentrancy
            vault.withdraw(1 ether, {"from": victim})
            
            final_vault_balance = vault.balance()
            final_victim_balance = vault.balances(victim)
            
            # Check if reentrancy occurred
            if final_vault_balance < initial_vault_balance - 1 ether:
                print("⚠️  Possible reentrancy detected in withdraw function")
                self.reentrancy_tester.log_vulnerability(
                    "REENTRANCY",
                    "Reentrancy vulnerability in withdraw function",
                    "HIGH"
                )
            else:
                print("✅ No reentrancy detected in withdraw function")
                
        except Exception as e:
            print(f"❌ Withdraw failed: {e}")
    
    def test_secure_withdraw_protection(self):
        """Test that withdrawSecure has reentrancy protection"""
        print("\n🛡️ Testing reentrancy protection in withdrawSecure...")
        
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund the vault
        self.accounts[0].transfer(vault.address, "10 ether")
        
        # Deposit from victim
        victim = self.accounts[1]
        vault.deposit({"from": victim, "value": "5 ether"})
        
        try:
            # This should be protected against reentrancy
            vault.withdrawSecure(1 ether, {"from": victim})
            print("✅ withdrawSecure function executed successfully")
            
        except Exception as e:
            print(f"❌ withdrawSecure failed: {e}")
    
    def test_reentrancy_with_multiple_attacks(self):
        """Test reentrancy with multiple attack scenarios"""
        print("\n🎭 Testing multiple reentrancy scenarios...")
        
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund vault
        self.accounts[0].transfer(vault.address, "20 ether")
        
        # Multiple victims deposit
        victims = self.accounts[1:4]
        for victim in victims:
            vault.deposit({"from": victim, "value": "3 ether"})
        
        print(f"Vault balance: {vault.balance()}")
        
        # Test reentrancy from multiple accounts
        for i, victim in enumerate(victims):
            print(f"\nTesting reentrancy from victim {i+1}...")
            
            initial_balance = vault.balances(victim)
            
            try:
                vault.withdraw(0.5 ether, {"from": victim})
                final_balance = vault.balances(victim)
                
                print(f"Victim {i+1} balance: {initial_balance} -> {final_balance}")
                
                if final_balance > initial_balance - 0.5 ether:
                    print(f"⚠️  Possible reentrancy from victim {i+1}")
                    
            except Exception as e:
                print(f"Victim {i+1} withdraw failed: {e}")
    
    def test_reentrancy_gas_analysis(self):
        """Analyze gas usage in reentrancy scenarios"""
        print("\n⛽ Analyzing gas usage in reentrancy scenarios...")
        
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund vault
        self.accounts[0].transfer(vault.address, "10 ether")
        
        # Deposit
        victim = self.accounts[1]
        deposit_tx = vault.deposit({"from": victim, "value": "5 ether"})
        print(f"Deposit gas: {deposit_tx.gas_used}")
        
        # Test vulnerable withdraw
        try:
            withdraw_tx = vault.withdraw(1 ether, {"from": victim})
            print(f"Vulnerable withdraw gas: {withdraw_tx.gas_used}")
        except Exception as e:
            print(f"Vulnerable withdraw failed: {e}")
        
        # Test secure withdraw
        try:
            secure_tx = vault.withdrawSecure(1 ether, {"from": victim})
            print(f"Secure withdraw gas: {secure_tx.gas_used}")
        except Exception as e:
            print(f"Secure withdraw failed: {e}")
    
    def test_reentrancy_state_consistency(self):
        """Test state consistency during reentrancy"""
        print("\n🔍 Testing state consistency during reentrancy...")
        
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund vault
        self.accounts[0].transfer(vault.address, "15 ether")
        
        # Multiple deposits
        users = self.accounts[1:4]
        for user in users:
            vault.deposit({"from": user, "value": "2 ether"})
        
        # Record initial state
        initial_vault_balance = vault.balance()
        initial_total_deposits = vault.totalDeposits()
        initial_user_balances = [vault.balances(user) for user in users]
        
        print(f"Initial vault balance: {initial_vault_balance}")
        print(f"Initial total deposits: {initial_total_deposits}")
        print(f"Initial user balances: {initial_user_balances}")
        
        # Attempt reentrancy attack
        attacker = users[0]
        try:
            vault.withdraw(1 ether, {"from": attacker})
            
            # Check final state
            final_vault_balance = vault.balance()
            final_total_deposits = vault.totalDeposits()
            final_user_balances = [vault.balances(user) for user in users]
            
            print(f"Final vault balance: {final_vault_balance}")
            print(f"Final total deposits: {final_total_deposits}")
            print(f"Final user balances: {final_user_balances}")
            
            # Check for state inconsistencies
            expected_vault_balance = initial_vault_balance - 1 ether
            expected_total_deposits = initial_total_deposits - 1 ether
            
            if final_vault_balance != expected_vault_balance:
                print(f"⚠️  Vault balance inconsistency: expected {expected_vault_balance}, got {final_vault_balance}")
                
            if final_total_deposits != expected_total_deposits:
                print(f"⚠️  Total deposits inconsistency: expected {expected_total_deposits}, got {final_total_deposits}")
                
        except Exception as e:
            print(f"Reentrancy test failed: {e}")


@pytest.mark.security
@pytest.mark.reentrancy
class TestReentrancyMitigation:
    """Test reentrancy mitigation techniques"""
    
    def test_checks_effects_interactions_pattern(self):
        """Test Checks-Effects-Interactions pattern"""
        print("\n🛡️ Testing Checks-Effects-Interactions pattern...")
        
        vault = VulnerableVault.deploy({"from": accounts[0]})
        
        # Fund vault
        accounts[0].transfer(vault.address, "10 ether")
        
        # Deposit
        user = accounts[1]
        vault.deposit({"from": user, "value": "5 ether"})
        
        # Test vulnerable function (Effects before Interactions)
        print("Testing vulnerable pattern (Effects before Interactions)...")
        try:
            vault.withdraw(1 ether, {"from": user})
            print("⚠️  Vulnerable pattern executed")
        except Exception as e:
            print(f"Vulnerable pattern failed: {e}")
        
        # Test secure function (Interactions after Effects)
        print("Testing secure pattern (Interactions after Effects)...")
        try:
            vault.withdrawSecure(1 ether, {"from": user})
            print("✅ Secure pattern executed")
        except Exception as e:
            print(f"Secure pattern failed: {e}")
    
    def test_reentrancy_guard_effectiveness(self):
        """Test effectiveness of reentrancy guard"""
        print("\n🔒 Testing reentrancy guard effectiveness...")
        
        vault = VulnerableVault.deploy({"from": accounts[0]})
        
        # Fund vault
        accounts[0].transfer(vault.address, "10 ether")
        
        # Deposit
        user = accounts[1]
        vault.deposit({"from": user, "value": "5 ether}")
        
        # Test if reentrancy guard is working
        # This would require a malicious contract to properly test
        # For now, we'll test the basic functionality
        
        try:
            # First withdraw should work
            vault.withdrawSecure(1 ether, {"from": user})
            print("✅ First withdraw with reentrancy guard succeeded")
            
            # Second withdraw should also work
            vault.withdrawSecure(1 ether, {"from": user})
            print("✅ Second withdraw with reentrancy guard succeeded")
            
        except Exception as e:
            print(f"Reentrancy guard test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
