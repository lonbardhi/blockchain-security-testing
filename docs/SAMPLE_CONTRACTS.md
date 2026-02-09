# Sample Contracts for Security Testing

This document describes the sample contracts added to the blockchain security testing framework, each designed to demonstrate specific vulnerability patterns.

## 📋 **Contract Overview**

### **1. AuctionContract.sol**
**Purpose**: Auction platform with multiple security vulnerabilities
**Vulnerabilities**:
- ✅ **Reentrancy** - `bid()` function calls external contracts before state update
- ✅ **Access Control** - `endAuction()` can be called by anyone
- ✅ **Integer Overflow** - `withdraw()` function vulnerable to overflow
- ✅ **Front-running** - `placeBidWithMinGas()` lacks gas price protection
- ✅ **Timestamp Dependency** - `isAuctionActive()` uses manipulable timestamp
- ✅ **Gas Limit DoS** - `refundAllBidders()` has unbounded loop
- ✅ **Delegatecall** - `executeDelegate()` allows arbitrary delegatecall

**Secure Version**: `endAuctionSecure()` and `bidSecure()` demonstrate proper protection

### **2. NFTMarketplace.sol**
**Purpose**: NFT marketplace with comprehensive security issues
**Vulnerabilities**:
- ✅ **Reentrancy** - `makeOffer()` and `acceptOffer()` vulnerable
- ✅ **Access Control** - `cancelListing()` and `updateMarketplaceFee()` lack proper checks
- ✅ **Integer Overflow** - `withdrawOffer()` vulnerable to overflow
- ✅ **Front-running** - `acceptBestOffer()` lacks gas price protection
- ✅ **Oracle Manipulation** - `getNFTPrice()` returns fixed price
- ✅ **Slippage** - `buyNow()` has no slippage protection
- ✅ **Gas Limit DoS** - `batchCancelListings()` has unbounded loop

**Secure Version**: `acceptOfferSecure()` demonstrates proper Checks-Effects-Interactions pattern

### **3. TokenSale.sol**
**Purpose**: Token sale contract with multiple vulnerability patterns
**Vulnerabilities**:
- ✅ **Reentrancy** - `buyTokens()` and `claimTokens()` vulnerable
- ✅ **Access Control** - `startSale()` and `updateWallet()` lack proper checks
- ✅ **Integer Overflow** - `calculateTokenAmount()` vulnerable to overflow
- ✅ **Front-running** - `buyWithMinGas()` lacks gas price protection
- ✅ **Gas Limit DoS** - `batchDistributeTokens()` has unbounded loop
- ✅ **Oracle Manipulation** - `getTokenPriceInUSD()` returns fixed price
- ✅ **Slippage** - `buyExactTokens()` has no slippage protection

**Secure Version**: `buyTokensSecure()` and `claimTokensSecure()` demonstrate proper protection

### **4. SecureVault.sol**
**Purpose**: Secure vault demonstrating best practices and proper security patterns
**Security Features**:
- ✅ **Reentrancy Protection** - Uses `nonReentrant` modifier
- ✅ **Safe Math** - Uses OpenZeppelin's SafeMath
- ✅ **Access Control** - Proper `onlyOwner` and validation
- ✅ **Input Validation** - Address validation and amount limits
- ✅ **Gas Limit Protection** - Pagination in batch operations
- ✅ **Rate Limiting** - Daily withdrawal limits
- ✅ **Emergency Controls** - Proper pause/unpause mechanisms
- ✅ **Event Logging** - Comprehensive event emission

**Pattern**: Implements Checks-Effects-Interactions pattern consistently

## 🔍 **Testing Scenarios**

### **Reentrancy Testing**
```python
# Test vulnerable vs secure implementations
vulnerable_vault.withdraw(1 ether)  # Vulnerable
secure_vault.withdraw(1 ether)       # Secure
```

### **Access Control Testing**
```python
# Test unauthorized access
auction.endAuction(auction_id, {"from": attacker})  # Should fail
auction.endAuctionSecure(auction_id, {"from": owner})  # Should succeed
```

### **Integer Overflow Testing**
```python
# Test with maximum values
max_amount = 2**256 - 1
token_sale.calculateTokenAmount(max_amount, 1000)  # Test overflow
```

### **Front-running Testing**
```python
# Test front-running susceptibility
auction.placeBidWithMinGas(auction_id, 2 ether, {"from": attacker})
# Can be front-run by bots with higher gas prices
```

## 🎯 **Learning Objectives**

### **1. Vulnerability Recognition**
- Identify common attack vectors
- Understand vulnerable code patterns
- Learn to spot security issues in code

### **2. Secure Pattern Implementation**
- Study secure implementations
- Understand protection mechanisms
- Learn best practices

### **3. Comparative Analysis**
- Compare vulnerable vs secure code
- Understand impact of security measures
- Learn trade-offs and considerations

### **4. Testing Methodology**
- Develop systematic testing approach
- Create comprehensive test suites
- Learn to validate security measures

## 🛠️ **Usage Examples**

### **Deploy All Contracts**
```bash
brownie run scripts/deploy_contracts.py
```

### **Run Security Tests**
```bash
brownie test tests/test_sample_contracts.py
```

### **Compare Vulnerable vs Secure**
```python
# Test both implementations
vulnerable_result = vulnerable_vault.withdraw(1 ether)
secure_result = secure_vault.withdraw(1 ether)

# Analyze differences
```

### **Specific Vulnerability Testing**
```bash
# Test reentrancy only
brownie test tests/test_sample_contracts.py::TestAuctionContractSecurity::test_auction_reentrancy_vulnerability

# Test access control only
brownie test tests/test_sample_contracts.py::TestNFTMarketplaceSecurity::test_nft_marketplace_access_control

# Test overflow only
brownie test tests/test_sample_contracts.py::TestTokenSaleSecurity::test_token_sale_overflow
```

## 📊 **Security Categories Covered**

### **Critical Vulnerabilities**
1. **Reentrancy** - External calls before state updates
2. **Access Control** - Unauthorized function execution
3. **Integer Overflow/Underflow** - Arithmetic boundary issues

### **Advanced Vulnerabilities**
1. **Front-running** - Transaction ordering attacks
2. **Gas Limit DoS** - Unbounded operations
3. **Oracle Manipulation** - Price feed manipulation
4. **Slippage** - Price impact protection

### **Best Practices**
1. **Checks-Effects-Interactions** - Proper state management
2. **Safe Math Operations** - Overflow protection
3. **Access Control Patterns** - Proper authorization
4. **Gas Optimization** - Efficient contract design

## 🎪 **Advanced Testing Scenarios**

### **Coordinated Attacks**
```python
# Test multi-contract attack scenarios
def test_complete_attack_scenario():
    # 1. Deploy multiple contracts
    # 2. Setup attack vectors
    # 3. Execute coordinated attacks
    # 4. Analyze cross-contract impacts
```

### **Economic Attacks**
```python
# Test economic manipulation
def test_economic_attacks():
    # 1. Price manipulation
    # 2. Liquidity attacks
    # 3. MEV extraction
    # 4. Economic impact analysis
```

## 📚 **Further Learning**

### **Security Research**
- [Smart Contract Weakness Classification](https://swcregistry.io/)
- [ConsenSys Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [OpenZeppelin Security Guides](https://docs.openzeppelin.com/contracts/4.x/security)

### **Advanced Topics**
- Formal verification methods
- Zero-knowledge proofs
- Layer 2 security considerations
- Cross-chain bridge security

---

These sample contracts provide a comprehensive foundation for learning blockchain security through practical, hands-on testing of real vulnerability patterns.
