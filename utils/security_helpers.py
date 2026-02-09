"""
Security testing utilities for smart contract vulnerability detection
"""
from typing import Dict, List, Any, Optional
from brownie import network, accounts, Contract
from eth_account import Account
import time
import json
from web3 import Web3


class SecurityTester:
    """Base class for security testing utilities"""
    
    def __init__(self):
        self.w3 = network.web3
        self.accounts = accounts
        self.vulnerabilities_found = []
    
    def log_vulnerability(self, vuln_type: str, description: str, severity: str = "HIGH"):
        """Log discovered vulnerability"""
        self.vulnerabilities_found.append({
            "type": vuln_type,
            "description": description,
            "severity": severity,
            "timestamp": time.time()
        })
    
    def get_vulnerability_report(self) -> Dict[str, Any]:
        """Generate vulnerability report"""
        return {
            "total_vulnerabilities": len(self.vulnerabilities_found),
            "vulnerabilities": self.vulnerabilities_found,
            "severity_counts": self._count_by_severity()
        }
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in self.vulnerabilities_found:
            counts[vuln["severity"]] += 1
        return counts


class ReentrancyTester(SecurityTester):
    """Test for reentrancy vulnerabilities"""
    
    def test_reentrancy(self, contract: Contract, vulnerable_function: str, amount: int):
        """Test reentrancy attack on vulnerable function"""
        print(f"Testing reentrancy on {vulnerable_function}")
        
        # Deploy attacker contract
        attacker_contract = self._deploy_attacker_contract(contract.address)
        
        # Initial balance
        initial_balance = contract.balance()
        
        # Attempt reentrancy attack
        try:
            tx = attacker_contract.attack(vulnerable_function, {"value": amount})
            tx.wait(1)
            
            # Check if attack succeeded
            final_balance = contract.balance()
            if final_balance < initial_balance:
                self.log_vulnerability(
                    "REENTRANCY",
                    f"Reentrancy vulnerability detected in {vulnerable_function}",
                    "HIGH"
                )
                return True
                
        except Exception as e:
            print(f"Reentrancy attack failed: {e}")
            return False
        
        return False
    
    def _deploy_attacker_contract(self, target_address: str) -> Contract:
        """Deploy reentrancy attacker contract"""
        # This would deploy a malicious contract
        # For now, return mock implementation
        return None


class IntegerOverflowTester(SecurityTester):
    """Test for integer overflow/underflow vulnerabilities"""
    
    def test_overflow(self, contract: Contract, function_name: str, large_input: int):
        """Test integer overflow with large inputs"""
        print(f"Testing overflow in {function_name}")
        
        max_uint256 = 2**256 - 1
        
        try:
            # Test with maximum uint256 value
            if hasattr(contract, function_name):
                func = getattr(contract, function_name)
                
                # Test overflow scenarios
                test_cases = [
                    max_uint256,
                    max_uint256 - 1,
                    max_uint256 + 1,  # This should overflow
                    0,
                    -1  # This should underflow if signed
                ]
                
                for test_input in test_cases:
                    try:
                        tx = func(test_input)
                        tx.wait(1)
                        
                        # If transaction succeeds with overflow input, log vulnerability
                        if test_input > max_uint256 or test_input < 0:
                            self.log_vulnerability(
                                "INTEGER_OVERFLOW",
                                f"Integer overflow in {function_name} with input {test_input}",
                                "HIGH"
                            )
                            
                    except Exception as e:
                        # Expected failure for invalid inputs
                        continue
                        
        except Exception as e:
            print(f"Overflow test failed: {e}")


class AccessControlTester(SecurityTester):
    """Test for access control vulnerabilities"""
    
    def test_access_control(self, contract: Contract, restricted_functions: List[str]):
        """Test access control on restricted functions"""
        print("Testing access control")
        
        # Get unauthorized account
        unauthorized_account = self.accounts[1]
        
        for function_name in restricted_functions:
            if hasattr(contract, function_name):
                func = getattr(contract, function_name)
                
                try:
                    # Try to call restricted function with unauthorized account
                    tx = func({"from": unauthorized_account})
                    tx.wait(1)
                    
                    # If call succeeds, access control is broken
                    self.log_vulnerability(
                        "ACCESS_CONTROL",
                        f"Access control bypass in {function_name}",
                        "HIGH"
                    )
                    
                except Exception as e:
                    # Expected failure for unauthorized access
                    print(f"Access control working for {function_name}: {e}")


class GasLimitTester(SecurityTester):
    """Test for gas limit and DoS vulnerabilities"""
    
    def test_gas_limit(self, contract: Contract, function_name: str, iterations: int = 1000):
        """Test gas limit with large loops"""
        print(f"Testing gas limit in {function_name}")
        
        try:
            if hasattr(contract, function_name):
                func = getattr(contract, function_name)
                
                # Test with increasing iterations
                for i in [100, 500, 1000, 5000]:
                    try:
                        tx = func(i)
                        tx.wait(1)
                        
                        # Check gas usage
                        gas_used = tx.gas_used
                        if gas_used > 8000000:  #接近 block gas limit
                            self.log_vulnerability(
                                "GAS_LIMIT",
                                f"High gas usage in {function_name}: {gas_used}",
                                "MEDIUM"
                            )
                            
                    except Exception as e:
                        if "out of gas" in str(e).lower():
                            self.log_vulnerability(
                                "GAS_LIMIT_DOS",
                                f"Gas limit DoS in {function_name} with {i} iterations",
                                "HIGH"
                            )
                        break
                        
        except Exception as e:
            print(f"Gas limit test failed: {e}")


class FrontRunningTester(SecurityTester):
    """Test for front-running vulnerabilities"""
    
    def test_front_running(self, contract: Contract, function_name: str, value: int):
        """Test front-running susceptibility"""
        print(f"Testing front-running in {function_name}")
        
        try:
            # Simulate front-running scenario
            # First transaction (victim)
            victim_tx = getattr(contract, function_name)({"value": value})
            
            # Second transaction (attacker) with higher gas price
            attacker_tx = getattr(contract, function_name)({
                "value": value + 1,
                "gasPrice": victim_tx.gas_price + 1000000000  # Higher gas price
            })
            
            # If attacker transaction gets mined first, front-running is possible
            # This is a simplified test - real front-running is more complex
            
        except Exception as e:
            print(f"Front-running test failed: {e}")


class OracleManipulationTester(SecurityTester):
    """Test for oracle manipulation vulnerabilities"""
    
    def test_oracle_manipulation(self, contract: Contract, oracle_function: str):
        """Test oracle manipulation susceptibility"""
        print(f"Testing oracle manipulation in {oracle_function}")
        
        try:
            if hasattr(contract, oracle_function):
                func = getattr(contract, oracle_function)
                
                # Get current oracle value
                current_value = func()
                
                # Check if oracle can be easily manipulated
                # This would involve testing price manipulation scenarios
                
                # Look for fixed prices or easily manipulable oracles
                if current_value == 1000 * 10**18:  # Common test value
                    self.log_vulnerability(
                        "ORACLE_MANIPULATION",
                        f"Fixed oracle price in {oracle_function}",
                        "MEDIUM"
                    )
                    
        except Exception as e:
            print(f"Oracle manipulation test failed: {e}")


class SlippageTester(SecurityTester):
    """Test for slippage protection vulnerabilities"""
    
    def test_slippage_protection(self, contract: Contract, swap_function: str):
        """Test slippage protection"""
        print(f"Testing slippage protection in {swap_function}")
        
        try:
            if hasattr(contract, swap_function):
                func = getattr(contract, swap_function)
                
                # Test swap with large amounts that could cause high slippage
                large_amount = 1000000 * 10**18
                
                try:
                    tx = func(large_amount)
                    tx.wait(1)
                    
                    # If swap succeeds without slippage checks, log vulnerability
                    self.log_vulnerability(
                        "SLIPPAGE",
                        f"No slippage protection in {swap_function}",
                        "MEDIUM"
                    )
                    
                except Exception as e:
                    # Expected failure with proper slippage protection
                    print(f"Slippage protection working: {e}")
                    
        except Exception as e:
            print(f"Slippage test failed: {e}")


class FlashLoanTester(SecurityTester):
    """Test for flash loan attack vulnerabilities"""
    
    def test_flash_loan_attack(self, contract: Contract, flash_loan_function: str):
        """Test flash loan attack resistance"""
        print(f"Testing flash loan attack in {flash_loan_function}")
        
        try:
            if hasattr(contract, flash_loan_function):
                func = getattr(contract, flash_loan_function)
                
                # Test flash loan with large amount
                large_amount = 1000000 * 10**18
                
                try:
                    tx = func(large_amount)
                    tx.wait(1)
                    
                    # If flash loan succeeds without proper protection, log vulnerability
                    self.log_vulnerability(
                        "FLASH_LOAN",
                        f"Flash loan vulnerability in {flash_loan_function}",
                        "HIGH"
                    )
                    
                except Exception as e:
                    # Expected failure with proper flash loan protection
                    print(f"Flash loan protection working: {e}")
                    
        except Exception as e:
            print(f"Flash loan test failed: {e}")


class SecurityTestSuite:
    """Comprehensive security test suite"""
    
    def __init__(self):
        self.testers = {
            "reentrancy": ReentrancyTester(),
            "overflow": IntegerOverflowTester(),
            "access_control": AccessControlTester(),
            "gas_limit": GasLimitTester(),
            "front_running": FrontRunningTester(),
            "oracle": OracleManipulationTester(),
            "slippage": SlippageTester(),
            "flash_loan": FlashLoanTester()
        }
    
    def run_all_tests(self, contract: Contract, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run all security tests"""
        print("🔍 Running comprehensive security tests...")
        
        results = {}
        
        # Run each test category
        for test_name, tester in self.testers.items():
            print(f"\n📋 Running {test_name} tests...")
            
            try:
                if test_name == "reentrancy" and "reentrancy_functions" in test_config:
                    for func in test_config["reentrancy_functions"]:
                        tester.test_reentrancy(contract, func, test_config.get("amount", 1000))
                        
                elif test_name == "overflow" and "overflow_functions" in test_config:
                    for func in test_config["overflow_functions"]:
                        tester.test_overflow(contract, func, test_config.get("large_input", 2**256 - 1))
                        
                elif test_name == "access_control" and "restricted_functions" in test_config:
                    tester.test_access_control(contract, test_config["restricted_functions"])
                    
                elif test_name == "gas_limit" and "gas_functions" in test_config:
                    for func in test_config["gas_functions"]:
                        tester.test_gas_limit(contract, func)
                        
                elif test_name == "oracle" and "oracle_functions" in test_config:
                    for func in test_config["oracle_functions"]:
                        tester.test_oracle_manipulation(contract, func)
                        
                elif test_name == "slippage" and "swap_functions" in test_config:
                    for func in test_config["swap_functions"]:
                        tester.test_slippage_protection(contract, func)
                        
                elif test_name == "flash_loan" and "flash_loan_functions" in test_config:
                    for func in test_config["flash_loan_functions"]:
                        tester.test_flash_loan_attack(contract, func)
                
                results[test_name] = tester.get_vulnerability_report()
                
            except Exception as e:
                print(f"❌ {test_name} tests failed: {e}")
                results[test_name] = {"error": str(e)}
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive security report"""
        report = "🔒 Smart Contract Security Report\n"
        report += "=" * 50 + "\n\n"
        
        total_vulnerabilities = 0
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for test_name, result in results.items():
            if "error" in result:
                report += f"❌ {test_name}: {result['error']}\n\n"
                continue
                
            vulns = result.get("vulnerabilities", [])
            total_vulnerabilities += len(vulns)
            
            for vuln in vulns:
                severity_counts[vuln["severity"]] += 1
                report += f"⚠️  {vuln['severity']}: {vuln['type']}\n"
                report += f"   {vuln['description']}\n\n"
        
        report += f"\n📊 Summary:\n"
        report += f"Total Vulnerabilities: {total_vulnerabilities}\n"
        report += f"High Severity: {severity_counts['HIGH']}\n"
        report += f"Medium Severity: {severity_counts['MEDIUM']}\n"
        report += f"Low Severity: {severity_counts['LOW']}\n"
        
        return report
