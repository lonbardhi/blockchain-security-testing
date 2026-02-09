# Brownie Basics - Setup, Deployment, and Simple Tests

This guide covers the fundamentals of using Brownie for blockchain development and testing, specifically tailored for our security testing framework.

## 📋 **Table of Contents**

1. [What is Brownie?](#what-is-brownie)
2. [Installation & Setup](#installation--setup)
3. [Project Structure](#project-structure)
4. [Basic Commands](#basic-commands)
5. [Contract Deployment](#contract-deployment)
6. [Writing Tests](#writing-tests)
7. [Running Tests](#running-tests)
8. [Network Management](#network-management)
9. [Account Management](#account-management)
10. [Debugging Tips](#debugging-tips)

## 🤔 **What is Brownie?**

Brownie is a Python-based development and testing framework for smart contracts targeting the Ethereum Virtual Machine (EVM).

**Key Features:**
- 🐍 **Python-native** - Write tests and scripts in Python
- 🔧 **Built-in testing** - Pytest integration for contract testing
- 🌐 **Network management** - Easy switching between testnets and mainnet
- 📊 **Gas profiling** - Built-in gas usage analysis
- 📝 **Console** - Interactive Python console for blockchain interaction

## 🚀 **Installation & Setup**

### **Prerequisites**
```bash
# Python 3.9+ required
python --version

# Node.js for Ganache
node --version
```

### **Install Brownie**
```bash
# Install via pip
pip install eth-brownie

# Verify installation
brownie --version
```

### **Install Ganache (Local Blockchain)**
```bash
# Install Ganache CLI
npm install -g ganache-cli

# Or use Ganache GUI (download from trufflesuite.com)
```

### **Initialize Brownie Project**
```bash
# Navigate to project directory
cd blockchain-security-testing

# Initialize Brownie project (if starting from scratch)
brownie init

# Our project is already initialized!
```

### **Project Dependencies**
```bash
# Install required packages
pip install -r requirements.txt

# Key dependencies include:
# - eth-brownie (Brownie framework)
# - pytest (Testing framework)
# - slither-analyzer (Static analysis)
# - hypothesis (Property-based testing)
```

## 📁 **Project Structure**

```
blockchain-security-testing/
├── contracts/              # Solidity smart contracts
│   ├── SimpleToken.sol
│   ├── VulnerableVault.sol
│   └── ...
├── tests/                  # Python test files
│   ├── test_security_comprehensive.py
│   └── ...
├── scripts/                # Deployment and utility scripts
│   ├── deploy_contracts.py
│   └── ...
├── interfaces/             # Interface files
├── reports/               # Test reports and artifacts
├── build/                # Compiled contract artifacts
├── brownie-config.yaml    # Brownie configuration
└── .env                 # Environment variables
```

### **Brownie Configuration (brownie-config.yaml)**
```yaml
# Project configuration
project_structure:
    contracts: contracts
    interfaces: interfaces
    scripts: scripts
    tests: tests

# Network configuration
networks:
    default: development
    development:
        cmd: ganache-cli
        cmd_settings:
            port: 8545
            gas_limit: 12000000
            accounts: 10
            mnemonic: brownie
            block_time: 0

# Compiler settings
dependencies:
  - OpenZeppelin/openzeppelin-contracts@4.8.0

compiler:
    solc:
        version: 0.8.19
        optimizer:
            enabled: true
            runs: 200
```

## ⚡ **Basic Commands**

### **Compilation**
```bash
# Compile all contracts
brownie compile

# Compile specific contract
brownie compile contracts/SimpleToken.sol

# Force recompilation
brownie compile --all
```

### **Console (Interactive Mode)**
```bash
# Start Brownie console
brownie console

# Console with specific network
brownie console --network development

# Console commands
>>> accounts        # Show available accounts
>>> network         # Show current network
>>> history         # Command history
>>> exit           # Exit console
```

### **Testing**
```bash
# Run all tests
brownie test

# Run specific test file
brownie test tests/test_security_comprehensive.py

# Run with verbose output
brownie test -v

# Run with coverage
brownie test --coverage

# Run specific test function
brownie test tests/test_security_comprehensive.py::TestSmartContractSecurity::test_vulnerable_vault_security
```

## 🏗️ **Contract Deployment**

### **Manual Deployment**
```python
# In Brownie console or script
from brownie import accounts, SimpleToken

# Get deployer account
deployer = accounts[0]
print(f"Deploying from: {deployer.address}")
print(f"Balance: {deployer.balance()} wei")

# Deploy contract
token = SimpleToken.deploy(
    "Security Test Token",  # name
    "SEC",                 # symbol
    1000000 * 10**18,     # initial supply
    {"from": deployer}
)

print(f"Token deployed at: {token.address}")
print(f"Total supply: {token.totalSupply()}")
```

### **Script Deployment**
```python
# scripts/deploy_contracts.py
from brownie import accounts, SimpleToken, VulnerableVault

def main():
    deployer = accounts[0]
    
    # Deploy SimpleToken
    token = SimpleToken.deploy(
        "Security Test Token",
        "SEC",
        1000000 * 10**18,
        {"from": deployer}
    )
    
    # Deploy VulnerableVault
    vault = VulnerableVault.deploy({"from": deployer})
    
    # Fund vault
    deployer.transfer(vault.address, "10 ether")
    
    return token, vault

# Run deployment script
brownie run scripts/deploy_contracts.py
```

### **Network Deployment**
```bash
# Deploy to development network (default)
brownie run scripts/deploy_contracts.py

# Deploy to specific network
brownie run scripts/deploy_contracts.py --network rinkeby

# Deploy to mainnet (be careful!)
brownie run scripts/deploy_contracts.py --network mainnet
```

## 🧪 **Writing Tests**

### **Basic Test Structure**
```python
# tests/test_simple_token.py
import pytest
from brownie import accounts, SimpleToken

def test_token_deployment():
    """Test basic token deployment"""
    # Arrange
    deployer = accounts[0]
    
    # Act
    token = SimpleToken.deploy(
        "Test Token",
        "TEST",
        1000000 * 10**18,
        {"from": deployer}
    )
    
    # Assert
    assert token.name() == "Test Token"
    assert token.symbol() == "TEST"
    assert token.totalSupply() == 1000000 * 10**18
    assert token.balanceOf(deployer) == 1000000 * 10**18

def test_token_transfer():
    """Test basic token transfer"""
    # Arrange
    deployer = accounts[0]
    recipient = accounts[1]
    token = SimpleToken.deploy("Test Token", "TEST", 1000000 * 10**18, {"from": deployer})
    
    # Act
    transfer_amount = 100 * 10**18
    token.transfer(recipient, transfer_amount, {"from": deployer})
    
    # Assert
    assert token.balanceOf(recipient) == transfer_amount
    assert token.balanceOf(deployer) == 1000000 * 10**18 - transfer_amount

def test_transfer_insufficient_balance():
    """Test transfer with insufficient balance"""
    # Arrange
    deployer = accounts[0]
    recipient = accounts[1]
    token = SimpleToken.deploy("Test Token", "TEST", 1000000 * 10**18, {"from": deployer})
    
    # Act & Assert
    with pytest.raises(Exception):
        token.transfer(recipient, 2000000 * 10**18, {"from": deployer})
```

### **Security Testing Example**
```python
# tests/test_vault_security.py
import pytest
from brownie import accounts, VulnerableVault, reverts

def test_vault_deposit_withdraw():
    """Test basic vault deposit and withdraw"""
    # Arrange
    deployer = accounts[0]
    user = accounts[1]
    vault = VulnerableVault.deploy({"from": deployer})
    
    # Fund vault
    deployer.transfer(vault.address, "10 ether")
    
    # Act - Deposit
    deposit_amount = "1 ether"
    vault.deposit({"from": user, "value": deposit_amount})
    
    # Assert
    assert vault.balances(user) == deposit_amount
    assert vault.balance() == "11 ether"
    
    # Act - Withdraw
    vault.withdraw("0.5 ether", {"from": user})
    
    # Assert
    assert vault.balances(user) == "0.5 ether"
    assert user.balance() == "999.5 ether"  # Assuming 1000 ether starting balance

def test_vault_reentrancy_attack():
    """Test reentrancy vulnerability"""
    # This would require a malicious contract
    # Simplified example showing the concept
    deployer = accounts[0]
    attacker = accounts[1]
    vault = VulnerableVault.deploy({"from": deployer})
    
    # Fund vault
    deployer.transfer(vault.address, "10 ether")
    
    # Attacker deposits
    vault.deposit({"from": attacker, "value": "1 ether"})
    
    # In a real test, you'd deploy a malicious contract here
    # that attempts reentrancy during withdrawal
```

### **Test Fixtures**
```python
# tests/conftest.py
import pytest
from brownie import accounts, SimpleToken, VulnerableVault

@pytest.fixture(scope="module")
def token():
    """Fixture providing a deployed token contract"""
    deployer = accounts[0]
    return SimpleToken.deploy(
        "Test Token",
        "TEST",
        1000000 * 10**18,
        {"from": deployer}
    )

@pytest.fixture(scope="module")
def vault():
    """Fixture providing a funded vault contract"""
    deployer = accounts[0]
    vault = VulnerableVault.deploy({"from": deployer})
    deployer.transfer(vault.address, "10 ether")
    return vault

@pytest.fixture
def user():
    """Fixture providing a test user account"""
    return accounts[1]

# Use fixtures in tests
def test_with_fixture(token, vault, user):
    """Test using fixtures"""
    assert token.name() == "Test Token"
    assert vault.balance() == "10 ether"
    assert user.balance() > 0
```

## 🏃 **Running Tests**

### **Basic Test Execution**
```bash
# Run all tests
brownie test

# Run specific test file
brownie test tests/test_simple_token.py

# Run specific test function
brownie test tests/test_simple_token.py::test_token_deployment

# Run with verbose output
brownie test -v

# Run with coverage report
brownie test --coverage

# Run with gas profiling
brownie test --gas
```

### **Test Markers**
```python
# tests/test_security.py
import pytest

@pytest.mark.security
def test_reentrancy():
    """Security test"""
    pass

@pytest.mark.access_control
def test_access_control():
    """Access control test"""
    pass

@pytest.mark.gas
def test_gas_optimization():
    """Gas optimization test"""
    pass

# Run tests with specific markers
brownie test -m security
brownie test -m "security or access_control"
```

### **Test Configuration**
```bash
# Run tests with specific network
brownie test --network development

# Run tests with timeout
brownie test --timeout 300

# Run tests in parallel
brownie test -n auto

# Generate HTML report
brownie test --html=reports/test_report.html
```

## 🌐 **Network Management**

### **Available Networks**
```bash
# List available networks
brownie networks list

# Development network (local Ganache)
brownie console --network development

# Testnet networks
brownie console --network rinkeby
brownie console --network goerli
brownie console --network sepolia

# Mainnet
brownie console --network mainnet
```

### **Network Configuration**
```yaml
# brownie-config.yaml
networks:
  development:
    cmd: ganache-cli
    cmd_settings:
      port: 8545
      gas_limit: 12000000
      accounts: 10
      mnemonic: brownie
      
  rinkeby:
    cmd: infura
    cmd_settings:
      infura_id: ${INFURA_ID}
      protocol: https
      
  mainnet:
    cmd: infura
    cmd_settings:
      infura_id: ${INFURA_ID}
      protocol: https
```

### **Environment Variables**
```bash
# .env file
INFURA_ID=your_infura_project_id
PRIVATE_KEY=your_private_key
ETHERSCAN_API_KEY=your_etherscan_api_key

# Load environment variables
export $(cat .env | xargs)
```

## 👥 **Account Management**

### **Local Accounts**
```python
# In Brownie console
>>> accounts
[<Account '0x...'>, <Account '0x...'>, ...]

>>> accounts[0]  # First account
<Account '0x...'>

>>> accounts[0].balance()
100000000000000000000

>>> accounts[0].address
'0x...'
```

### **Importing Accounts**
```python
# Import from private key
>>> accounts.add('your_private_key_here')
<Account '0x...'>

# Import from mnemonic
>>> accounts.from_mnemonic('your mnemonic phrase')
[<Account '0x...'>, <Account '0x...'>, ...]
```

### **Account Operations**
```python
# Get account balance
>>> accounts[0].balance()
100000000000000000000

# Transfer ETH
>>> accounts[0].transfer(accounts[1], "1 ether")

# Deploy contract from specific account
>>> token = SimpleToken.deploy("Test", "TEST", 1000000 * 10**18, {"from": accounts[1]})
```

## 🐛 **Debugging Tips**

### **Transaction Debugging**
```python
# Get transaction details
>>> tx = token.transfer(accounts[1], 100, {"from": accounts[0]})
>>> tx.info()
>>> tx.events
>>> tx.gas_used
>>> tx.gas_price

# Debug failed transaction
>>> tx = token.transfer(accounts[1], 1000000, {"from": accounts[0]})
>>> tx.error()
```

### **Console Debugging**
```python
# Interactive debugging
>>> token = SimpleToken.at('0x...')
>>> token.name()
'Test Token'

>>> token.balanceOf(accounts[0])
1000000 * 10**18

# Call view functions
>>> token.totalSupply()
1000000 * 10**18
```

### **Gas Analysis**
```python
# Gas profiling
brownie test --gas

# Gas optimization analysis
>>> tx = token.transfer(accounts[1], 100, {"from": accounts[0]})
>>> tx.gas_used
21000
```

### **Common Issues & Solutions**

**Issue: Contract not found**
```bash
# Solution: Compile contracts
brownie compile
```

**Issue: Account not found**
```bash
# Solution: Check network and accounts
brownie console
>>> accounts
```

**Issue: Insufficient funds**
```python
# Solution: Fund account
>>> accounts[0].transfer(accounts[1], "10 ether")
```

**Issue: Transaction reverted**
```python
# Solution: Check error message
>>> tx.error()
'revert: insufficient balance'
```

## 🎯 **Next Steps**

1. **Practice Basic Operations**
   - Deploy simple contracts
   - Write basic tests
   - Explore console commands

2. **Learn Security Testing**
   - Study vulnerable contracts
   - Write security tests
   - Use testing helpers

3. **Advanced Features**
   - Gas optimization
   - Network deployment
   - Integration testing

4. **Resources**
   - [Brownie Documentation](https://eth-brownie.readthedocs.io/)
   - [Solidity Documentation](https://docs.soliditylang.org/)
   - [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

---

This guide provides the foundation for using Brownie effectively in blockchain security testing. Practice these basics before moving to advanced security testing scenarios!
