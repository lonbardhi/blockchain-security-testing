# Getting Started with Blockchain Security Testing

This guide will help you set up and start using the blockchain security testing framework.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
   ```bash
   # Check Python version
   python --version
   ```

2. **Node.js** (for Ganache)
   ```bash
   # Install Node.js
   # Visit https://nodejs.org/ and download the latest version
   ```

3. **Git**
   ```bash
   # Check Git installation
   git --version
   ```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/blockchain-security-testing.git
   cd blockchain-security-testing
   ```

2. **Create virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Brownie**
   ```bash
   pip install eth-brownie
   ```

5. **Install Ganache**
   ```bash
   # Install Ganache CLI
   npm install -g ganache-cli
   
   # Or use Ganache GUI
   # Download from https://trufflesuite.com/ganache
   ```

### Setup

1. **Initialize Brownie project**
   ```bash
   brownie init
   ```

2. **Start local blockchain**
   ```bash
   # Start Ganache
   ganache-cli
   
   # Or use Ganache GUI and note the RPC server port
   ```

3. **Deploy contracts**
   ```bash
   # Deploy all test contracts
   brownie run scripts/deploy_contracts.py
   ```

4. **Run security tests**
   ```bash
   # Run comprehensive security tests
   brownie test tests/test_security_comprehensive.py
   
   # Run reentrancy-specific tests
   brownie test tests/test_reentrancy_specific.py
   
   # Run all security tests
   python scripts/run_security_tests.py
   ```

## 📁 Project Structure

```
blockchain-security-testing/
├── contracts/              # Smart contracts
│   ├── SimpleToken.sol      # ERC20 token with security features
│   ├── VulnerableVault.sol  # Intentionally vulnerable contract
│   └── DeFiPool.sol        # DeFi liquidity pool
├── tests/                  # Security test suites
│   ├── test_security_comprehensive.py  # Comprehensive security tests
│   └── test_reentrancy_specific.py    # Reentrancy-specific tests
├── scripts/                # Utility scripts
│   ├── deploy_contracts.py  # Contract deployment
│   └── run_security_tests.py # Test runner
├── utils/                  # Testing utilities
│   └── security_helpers.py  # Security testing helpers
├── reports/                # Test reports and analysis
├── docs/                   # Documentation
├── brownie-config.yaml      # Brownie configuration
└── requirements.txt        # Python dependencies
```

## 🧪 Running Tests

### Basic Test Commands

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

### Security Test Categories

1. **Reentrancy Testing**
   ```bash
   brownie test -m reentrancy
   ```

2. **Access Control Testing**
   ```bash
   brownie test -m access_control
   ```

3. **Gas Optimization Testing**
   ```bash
   brownie test -m gas
   ```

4. **Integration Testing**
   ```bash
   brownie test -m integration
   ```

### Running Security Analysis

```bash
# Run comprehensive security analysis
python scripts/run_security_tests.py

# Run Slither static analysis
slither contracts/ --json reports/slither_report.json

# Generate HTML reports
brownie test --html=reports/security_report.html --self-contained-html
```

## 📊 Understanding Reports

### Test Reports

After running tests, you'll find several reports in the `reports/` directory:

1. **comprehensive_security_report.json** - Detailed JSON report
2. **security_report.md** - Human-readable markdown report
3. **slither_report.json** - Static analysis results
4. **security_report.html** - Visual HTML report

### Vulnerability Severity Levels

- **HIGH** - Critical security issues that must be fixed before deployment
- **MEDIUM** - Important security issues that should be addressed
- **LOW** - Minor security improvements

### Report Analysis

```python
# Example: Analyze security report
import json

with open('reports/comprehensive_security_report.json', 'r') as f:
    report = json.load(f)

print(f"Total vulnerabilities: {report['summary']['total_vulnerabilities']}")
print(f"Risk level: {report['summary']['risk_level']}")

for vuln in report['vulnerabilities']:
    if vuln['severity'] == 'HIGH':
        print(f"CRITICAL: {vuln['type']} - {vuln['description']}")
```

## 🔧 Customization

### Adding New Contracts

1. **Create contract file** in `contracts/`
2. **Deploy contract** in `scripts/deploy_contracts.py`
3. **Add tests** in `tests/`
4. **Update test configuration** in test files

### Adding New Security Tests

1. **Create test class** inheriting from `SecurityTester`
2. **Implement test methods** for specific vulnerabilities
3. **Add to test suite** in `test_security_comprehensive.py`

Example:
```python
from utils.security_helpers import SecurityTester

class CustomSecurityTester(SecurityTester):
    def test_custom_vulnerability(self, contract):
        # Your custom test logic
        pass
```

### Configuration

Edit `brownie-config.yaml` to customize:
- Network settings
- Compiler versions
- Test markers
- Gas limits
- Dependencies

## 🚨 Common Issues

### Installation Problems

**Issue**: Brownie installation fails
```bash
# Solution: Install specific version
pip install eth-brownie==1.20.3
```

**Issue**: Slither not found
```bash
# Solution: Install Slither
pip install slither-analyzer
```

### Network Issues

**Issue**: Can't connect to local blockchain
```bash
# Solution: Check Ganache is running
ganache-cli --port 8545

# Or update brownie-config.yaml with correct port
```

**Issue**: Account balance insufficient
```bash
# Solution: Check account balances in Brownie console
brownie console
>>> accounts[0].balance()
```

### Test Failures

**Issue**: Tests timeout
```bash
# Solution: Increase timeout
brownie test --timeout=300
```

**Issue**: Gas limit exceeded
```bash
# Solution: Increase gas limit in brownie-config.yaml
```

## 📚 Learning Resources

### Documentation

- [Brownie Documentation](https://eth-brownie.readthedocs.io/)
- [Solidity Security Considerations](https://docs.soliditylang.org/en/latest/security-considerations.html)
- [ConsenSys Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)

### Security Research

- [Smart Contract Weakness Classification](https://swcregistry.io/)
- [OpenZeppelin Security Audits](https://docs.openzeppelin.com/contracts/4.x/audits)
- [Immunefi Bug Bounty](https://immunefi.com/)

### Tutorials

- [Ethereum Development with Brownie](https://docs.brownie.io/tutorials/)
- [Smart Contract Security Testing](https://www.youtube.com/watch?v=8NqGwz3J7qE)
- [DeFi Security Best Practices](https://docs.aave.com/developers/guides/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your security tests or contracts
4. Ensure all tests pass
5. Submit a pull request

## 🆘 Support

If you encounter issues:

1. Check the [Common Issues](#-common-issues) section
2. Search existing [GitHub Issues](https://github.com/your-username/blockchain-security-testing/issues)
3. Create a new issue with detailed information
4. Join the community discussion

---

Happy security testing! 🛡️
