"""
Comprehensive security testing suite for smart contracts
"""
import pytest
from brownie import network, accounts, SimpleToken, VulnerableVault, DeFiPool
from utils.security_helpers import SecurityTestSuite
import json


@pytest.mark.security
class TestSmartContractSecurity:
    """Comprehensive security tests for smart contracts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.security_suite = SecurityTestSuite()
        
    def test_vulnerable_vault_security(self):
        """Test security of VulnerableVault contract"""
        print("\n🔍 Testing VulnerableVault security...")
        
        # Deploy vulnerable vault
        vault = VulnerableVault.deploy({"from": self.accounts[0]})
        
        # Fund the vault
        self.accounts[0].transfer(vault.address, "10 ether")
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["withdraw"],
            "overflow_functions": ["calculateBonus"],
            "restricted_functions": ["emergencyWithdraw", "transferOwnership"],
            "gas_functions": ["distributeToAll"],
            "oracle_functions": ["getTokenPrice"],
            "swap_functions": ["placeBid"],
            "flash_loan_functions": [],
            "amount": 1000,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(vault, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report to file
        with open("reports/vault_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Verify vulnerabilities were found (this contract is intentionally vulnerable)
        total_vulns = sum(
            len(result.get("vulnerabilities", [])) 
            for result in results.values() 
            if "vulnerabilities" in result
        )
        
        assert total_vulns > 0, "Expected vulnerabilities not found in VulnerableVault"
        print(f"✅ Found {total_vulns} vulnerabilities in VulnerableVault")
    
    def test_simple_token_security(self):
        """Test security of SimpleToken contract"""
        print("\n🔍 Testing SimpleToken security...")
        
        # Deploy token
        token = SimpleToken.deploy(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            {"from": self.accounts[0]}
        )
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["burn"],
            "overflow_functions": [],
            "restricted_functions": ["mint", "setBlacklist", "pause"],
            "gas_functions": [],
            "oracle_functions": [],
            "swap_functions": [],
            "flash_loan_functions": [],
            "amount": 1000,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(token, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report to file
        with open("reports/token_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # SimpleToken should have fewer vulnerabilities than VulnerableVault
        total_vulns = sum(
            len(result.get("vulnerabilities", [])) 
            for result in results.values() 
            if "vulnerabilities" in result
        )
        
        print(f"✅ Found {total_vulns} vulnerabilities in SimpleToken")
    
    def test_defi_pool_security(self):
        """Test security of DeFiPool contract"""
        print("\n🔍 Testing DeFiPool security...")
        
        # Deploy mock tokens for testing
        # Note: This would need actual ERC20 token contracts
        # For now, we'll test with mock addresses
        
        # Deploy DeFi pool
        pool = DeFiPool.deploy(
            self.accounts[1],  # Mock token address
            self.accounts[2],  # Mock reward token address
            {"from": self.accounts[0]}
        )
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["stake", "withdraw", "claimRewards"],
            "overflow_functions": [],
            "restricted_functions": ["updateRewardRate", "withdrawStuckTokens"],
            "gas_functions": [],
            "oracle_functions": ["getTokenPrice"],
            "swap_functions": ["swap"],
            "flash_loan_functions": ["flashLoan"],
            "amount": 1000,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(pool, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report to file
        with open("reports/defi_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        total_vulns = sum(
            len(result.get("vulnerabilities", [])) 
            for result in results.values() 
            if "vulnerabilities" in result
        )
        
        print(f"✅ Found {total_vulns} vulnerabilities in DeFiPool")


@pytest.mark.security
@pytest.mark.reentrancy
class TestReentrancyAttacks:
    """Specific tests for reentrancy vulnerabilities"""
    
    def test_vault_reentrancy_attack(self):
        """Test reentrancy attack on VulnerableVault"""
        vault = VulnerableVault.deploy({"from": accounts[0]})
        
        # Deposit funds
        vault.deposit({"from": accounts[0], "value": "5 ether"})
        
        # Deploy attacker contract (simplified test)
        # In real implementation, this would deploy a malicious contract
        
        # Test vulnerable withdraw function
        initial_balance = vault.balance()
        
        try:
            # This should fail due to reentrancy protection in secure version
            vault.withdrawSecure(1 ether, {"from": accounts[0]})
            print("✅ Secure withdraw function works correctly")
        except Exception as e:
            print(f"❌ Secure withdraw failed: {e}")
        
        # Test vulnerable withdraw function
        try:
            vault.withdraw(1 ether, {"from": accounts[0]})
            print("⚠️  Vulnerable withdraw function succeeded (expected)")
        except Exception as e:
            print(f"✅ Vulnerable withdraw failed: {e}")


@pytest.mark.security
@pytest.mark.gas
class TestGasOptimization:
    """Tests for gas optimization and DoS vulnerabilities"""
    
    def test_gas_consumption(self):
        """Test gas consumption patterns"""
        vault = VulnerableVault.deploy({"from": accounts[0]})
        
        # Test gas consumption of different functions
        functions_to_test = [
            ("deposit", {}),
            ("withdraw", {}),
            ("emergencyWithdraw", {}),
            ("transferOwnership", {"newOwner": accounts[1]})
        ]
        
        gas_results = {}
        
        for func_name, params in functions_to_test:
            try:
                if hasattr(vault, func_name):
                    func = getattr(vault, func_name)
                    
                    if func_name == "deposit":
                        tx = func({"from": accounts[0], "value": "1 ether"})
                    else:
                        tx = func(params, {"from": accounts[0]})
                    
                    gas_results[func_name] = tx.gas_used
                    print(f"⛽ {func_name}: {tx.gas_used} gas")
                    
            except Exception as e:
                print(f"❌ {func_name} failed: {e}")
        
        # Check for excessive gas usage
        high_gas_threshold = 100000
        for func_name, gas_used in gas_results.items():
            if gas_used > high_gas_threshold:
                print(f"⚠️  High gas usage in {func_name}: {gas_used}")


@pytest.mark.security
@pytest.mark.access_control
class TestAccessControl:
    """Tests for access control vulnerabilities"""
    
    def test_unauthorized_access(self):
        """Test unauthorized access to restricted functions"""
        vault = VulnerableVault.deploy({"from": accounts[0]})
        
        restricted_functions = [
            ("transferOwnership", {"newOwner": accounts[1]}),
            ("distributeToAll", {"amount": 100}),
        ]
        
        for func_name, params in restricted_functions:
            try:
                if hasattr(vault, func_name):
                    func = getattr(vault, func_name)
                    
                    # Try to call with unauthorized account
                    tx = func(params, {"from": accounts[1]})
                    tx.wait(1)
                    
                    print(f"❌ Access control bypass in {func_name}")
                    
            except Exception as e:
                print(f"✅ Access control working in {func_name}: {e}")


@pytest.mark.security
@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security scenarios"""
    
    def test_complete_attack_scenario(self):
        """Test complete attack scenario combining multiple vulnerabilities"""
        print("\n🎭 Testing complete attack scenario...")
        
        # Setup
        vault = VulnerableVault.deploy({"from": accounts[0]})
        attacker = accounts[1]
        victim = accounts[2]
        
        # Initial deposits
        vault.deposit({"from": victim, "value": "10 ether"})
        vault.deposit({"from": attacker, "value": "1 ether"})
        
        print(f"Vault balance: {vault.balance()}")
        print(f"Victim balance: {vault.balances(victim)}")
        print(f"Attacker balance: {vault.balances(attacker)}")
        
        # Attack scenario: Combine multiple vulnerabilities
        try:
            # 1. Attempt reentrancy attack
            print("🎯 Attempting reentrancy attack...")
            vault.withdraw(0.5 ether, {"from": attacker})
            
            # 2. Attempt emergency withdraw (if accessible)
            print("🎯 Attempting emergency withdraw...")
            vault.emergencyWithdraw({"from": attacker})
            
            # 3. Attempt ownership transfer
            print("🎯 Attempting ownership transfer...")
            vault.transferOwnership(attacker, {"from": attacker})
            
        except Exception as e:
            print(f"Attack failed: {e}")
        
        # Final state
        print(f"Final vault balance: {vault.balance()}")
        print(f"Final victim balance: {vault.balances(victim)}")
        print(f"Final attacker balance: {vault.balances(attacker)}")
        print(f"Final owner: {vault.owner()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
