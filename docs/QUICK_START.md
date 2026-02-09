# Quick Start Guide - Brownie Basics

This guide gets you up and running with Brownie in 10 minutes!

## 🚀 **5-Minute Setup**

### **1. Install Dependencies**
```bash
# Install Python 3.9+ (if not already installed)
python --version

# Install Brownie
pip install eth-brownie

# Install Node.js for Ganache
# Download from: https://nodejs.org/

# Install Ganache CLI
npm install -g ganache-cli

# Install project dependencies
cd blockchain-security-testing
pip install -r requirements.txt
```

### **2. Start Local Blockchain**
```bash
# Start Ganache (in separate terminal)
ganache-cli

# Or use Ganache GUI and note the RPC server port
```

### **3. Verify Setup**
```bash
# Check Brownie installation
brownie --version

# Check available accounts
brownie console
>>> accounts
>>> exit
```

## 🧪 **Your First Test (2 Minutes)**

### **Run Basic Tests**
```bash
# Run the basics tutorial
brownie test tests/test_brownie_basics.py -v

# Run specific test
brownie test tests/test_brownie_basics.py::TestBrownieBasics::test_token_deployment
```

### **Expected Output**
```
============================= test session starts =============================
collected 13 items

tests/test_brownie_basics.py::TestBrownieBasics::test_token_deployment PASSED
tests/test_brownie_basics.py::TestBrownieBasics::test_vault_deployment PASSED
tests/test_brownie_basics.py::TestBrownieBasics::test_token_transfer PASSED
...
============================== 13 passed in 15.23s ==============================
```

## 🎯 **Interactive Tutorial (3 Minutes)**

### **Start Brownie Console**
```bash
brownie console
```

### **Run These Commands**
```python
# 1. Check accounts
>>> accounts
[<Account '0x...'>, <Account '0x...'>, ...]

# 2. Deploy a token
>>> token = SimpleToken.deploy("My Token", "MTK", 1000000 * 10**18, {"from": accounts[0]})
Transaction sent: 0x...
  Gas price: 0.0 gwei   Gas limit: 12000000   Gas used: 1234567
  SimpleToken deployed at: 0x...

# 3. Check token info
>>> token.name()
'My Token'
>>> token.totalSupply()
1000000000000000000000000

# 4. Transfer tokens
>>> token.transfer(accounts[1], 100 * 10**18, {"from": accounts[0]})
Transaction sent: 0x...

# 5. Check balances
>>> token.balanceOf(accounts[0])
999900000000000000000000
>>> token.balanceOf(accounts[1])
100000000000000000000

# 6. Exit
>>> exit
```

## 📝 **Your First Test Script**

Create a simple test file `my_first_test.py`:

```python
# my_first_test.py
import pytest
from brownie import accounts, SimpleToken

def test_my_first_token():
    # Deploy token
    token = SimpleToken.deploy(
        "My First Token",
        "MFT",
        1000 * 10**18,
        {"from": accounts[0]}
    )
    
    # Test basic properties
    assert token.name() == "My First Token"
    assert token.symbol() == "MFT"
    assert token.totalSupply() == 1000 * 10**18
    
    # Test transfer
    token.transfer(accounts[1], 100 * 10**18, {"from": accounts[0]})
    assert token.balanceOf(accounts[1]) == 100 * 10**18
    
    print("✅ My first test passed!")
```

Run your test:
```bash
brownie test my_first_test.py
```

## 🔧 **Common Commands**

### **Compilation**
```bash
# Compile contracts
brownie compile

# Force recompile
brownie compile --all
```

### **Testing**
```bash
# Run all tests
brownie test

# Run with verbose output
brownie test -v

# Run with coverage
brownie test --coverage

# Run specific test file
brownie test tests/test_brownie_basics.py
```

### **Console**
```bash
# Start console
brownie console

# Console with specific network
brownie console --network development
```

### **Scripts**
```bash
# Run deployment script
brownie run scripts/deploy_contracts.py

# Run tutorial
brownie run tutorials/01_brownie_basics.py
```

## 🎪 **Try These Examples**

### **Example 1: Token Operations**
```python
# In brownie console
>>> token = SimpleToken.deploy("Demo", "DEMO", 1000000 * 10**18, {"from": accounts[0]})
>>> token.transfer(accounts[1], 500 * 10**18, {"from": accounts[0]})
>>> token.balanceOf(accounts[1])
500000000000000000000
```

### **Example 2: Vault Operations**
```python
# In brownie console
>>> vault = VulnerableVault.deploy({"from": accounts[0]})
>>> accounts[0].transfer(vault.address, "5 ether")
>>> vault.deposit({"from": accounts[1], "value": "1 ether"})
>>> vault.balances(accounts[1])
1000000000000000000
```

### **Example 3: Transaction Analysis**
```python
# In brownie console
>>> tx = token.transfer(accounts[1], 100 * 10**18, {"from": accounts[0]})
>>> tx.gas_used
21000
>>> tx.events
{'Transfer': {'from': '0x...', 'to': '0x...', 'value': 100000000000000000000}}
```

## 🐛 **Troubleshooting**

### **Issue: "brownie: command not found"**
```bash
# Solution: Install Brownie
pip install eth-brownie

# Or add to PATH if installed globally
export PATH=$PATH:~/.local/bin
```

### **Issue: "Account not found"**
```bash
# Solution: Start Ganache
ganache-cli

# Or check if Ganache is running on correct port
brownie console --network development
```

### **Issue: "Contract not found"**
```bash
# Solution: Compile contracts
brownie compile

# Check compiled contracts
ls build/contracts/
```

### **Issue: "Insufficient funds"**
```bash
# Solution: Check account balance
brownie console
>>> accounts[0].balance()

# If balance is 0, restart Ganache
```

### **Issue: "Transaction reverted"**
```bash
# Solution: Check error message
>>> tx = token.transfer(accounts[1], 1000000 * 10**18, {"from": accounts[1]})
>>> tx.error()
'revert: insufficient balance'
```

## 📚 **Next Steps**

### **Learn Security Testing**
```bash
# Run security tests
brownie test tests/test_sample_contracts.py

# Study vulnerable contracts
cat contracts/VulnerableVault.sol
```

### **Explore Advanced Features**
```bash
# Gas profiling
brownie test --gas

# Network deployment
brownie run scripts/deploy_contracts.py --network rinkeby

# Interactive debugging
brownie console --network development
```

### **Read Documentation**
- [Brownie Documentation](https://eth-brownie.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Project README](../README.md)

## 🎯 **10-Minute Challenge**

Try to complete this challenge:

1. **Deploy a token** with your name and symbol
2. **Transfer 100 tokens** to accounts[1]
3. **Approve accounts[1]** to spend 50 tokens
4. **TransferFrom 25 tokens** from accounts[0] to accounts[2]
5. **Write a test** that verifies all balances

**Solution:**
```python
def test_challenge():
    # 1. Deploy token
    token = SimpleToken.deploy("Your Name", "YN", 1000 * 10**18, {"from": accounts[0]})
    
    # 2. Transfer to accounts[1]
    token.transfer(accounts[1], 100 * 10**18, {"from": accounts[0]})
    
    # 3. Approve accounts[1]
    token.approve(accounts[1], 50 * 10**18, {"from": accounts[0]})
    
    # 4. TransferFrom to accounts[2]
    token.transferFrom(accounts[0], accounts[2], 25 * 10**18, {"from": accounts[1]})
    
    # 5. Verify balances
    assert token.balanceOf(accounts[0]) == 925 * 10**18  # 1000 - 100 - 25
    assert token.balanceOf(accounts[1]) == 100 * 10**18
    assert token.balanceOf(accounts[2]) == 25 * 10**18
    assert token.allowance(accounts[0], accounts[1]) == 25 * 10**18  # 50 - 25
```

Run your solution:
```bash
brownie test your_challenge_test.py
```

---

🎉 **Congratulations!** You've completed the Brownie basics quick start. Now you're ready to explore blockchain security testing!
