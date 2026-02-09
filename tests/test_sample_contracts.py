"""
Comprehensive security tests for sample contracts
"""
import pytest
from brownie import network, accounts, AuctionContract, NFTMarketplace, TokenSale, SecureVault
from utils.security_helpers import SecurityTestSuite
import json


@pytest.mark.security
class TestAuctionContractSecurity:
    """Security tests for AuctionContract"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.security_suite = SecurityTestSuite()
    
    def test_auction_reentrancy_vulnerability(self):
        """Test reentrancy vulnerability in bid function"""
        print("\n🔍 Testing AuctionContract reentrancy...")
        
        # Deploy auction contract
        auction = AuctionContract.deploy({"from": self.accounts[0]})
        
        # Create auction
        auction_id = auction.createAuction(
            "Test Auction",
            1000,  # 1000 blocks duration
            0.1 ether,  # Min bid increment
            {"from": self.accounts[0]}
        )
        
        # Fund auction contract
        self.accounts[0].transfer(auction.address, "10 ether")
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["bid"],
            "overflow_functions": ["withdraw"],
            "restricted_functions": ["endAuction"],
            "gas_functions": ["refundAllBidders"],
            "oracle_functions": [],
            "swap_functions": [],
            "flash_loan_functions": [],
            "amount": 1 ether,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(auction, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report
        with open("reports/auction_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ AuctionContract security tests completed")
    
    def test_auction_access_control(self):
        """Test access control vulnerabilities"""
        print("\n🔒 Testing AuctionContract access control...")
        
        auction = AuctionContract.deploy({"from": self.accounts[0]})
        
        # Create auction
        auction_id = auction.createAuction(
            "Test Auction",
            1000,
            0.1 ether,
            {"from": self.accounts[0]}
        )
        
        # Test unauthorized auction ending
        try:
            auction.endAuction(auction_id, {"from": self.accounts[1]})
            print("⚠️  Access control bypass detected in endAuction")
        except Exception as e:
            print(f"✅ Access control working: {e}")
        
        # Test secure auction ending
        try:
            auction.endAuctionSecure(auction_id, {"from": self.accounts[0]})
            print("✅ Secure endAuction works")
        except Exception as e:
            print(f"❌ Secure endAuction failed: {e}")
    
    def test_auction_front_running(self):
        """Test front-running susceptibility"""
        print("\n🏃 Testing AuctionContract front-running...")
        
        auction = AuctionContract.deploy({"from": self.accounts[0]})
        
        # Create auction
        auction_id = auction.createAuction(
            "Test Auction",
            1000,
            0.1 ether,
            {"from": self.accounts[0]}
        )
        
        # Test front-running scenario
        try:
            # Place bid with minimum gas (vulnerable)
            auction.placeBidWithMinGas(auction_id, 1 ether, {"from": self.accounts[1]})
            print("⚠️  Front-running vulnerability detected")
        except Exception as e:
            print(f"✅ Front-running protection working: {e}")


@pytest.mark.security
class TestNFTMarketplaceSecurity:
    """Security tests for NFTMarketplace"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.security_suite = SecurityTestSuite()
    
    def test_nft_marketplace_reentrancy(self):
        """Test reentrancy in NFT marketplace"""
        print("\n🔍 Testing NFTMarketplace reentrancy...")
        
        # Deploy NFT marketplace
        marketplace = NFTMarketplace.deploy({"from": self.accounts[0]})
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["makeOffer", "acceptOffer"],
            "overflow_functions": ["withdrawOffer"],
            "restricted_functions": ["cancelListing", "updateMarketplaceFee"],
            "gas_functions": ["batchCancelListings"],
            "oracle_functions": ["getNFTPrice"],
            "swap_functions": ["buyNow"],
            "flash_loan_functions": [],
            "amount": 1 ether,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(marketplace, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report
        with open("reports/nft_marketplace_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ NFTMarketplace security tests completed")
    
    def test_nft_marketplace_access_control(self):
        """Test access control in NFT marketplace"""
        print("\n🔒 Testing NFTMarketplace access control...")
        
        marketplace = NFTMarketplace.deploy({"from": self.accounts[0]})
        
        # Create listing
        listing_id = marketplace.createListing(
            self.accounts[1],  # Mock NFT contract
            1,  # Token ID
            1 ether,  # Price
            86400,  # Duration (1 day)
            {"from": self.accounts[1]}
        )
        
        # Test unauthorized cancellation
        try:
            marketplace.cancelListing(listing_id, {"from": self.accounts[2]})
            print("⚠️  Access control bypass detected in cancelListing")
        except Exception as e:
            print(f"✅ Access control working: {e}")
        
        # Test unauthorized fee update
        try:
            marketplace.updateMarketplaceFee(5000, {"from": self.accounts[1]})  # 50%
            print("⚠️  Access control bypass detected in updateMarketplaceFee")
        except Exception as e:
            print(f"✅ Access control working: {e}")
    
    def test_nft_marketplace_slippage(self):
        """Test slippage protection"""
        print("\n💰 Testing NFTMarketplace slippage protection...")
        
        marketplace = NFTMarketplace.deploy({"from": self.accounts[0]})
        
        # Create listing
        listing_id = marketplace.createListing(
            self.accounts[1],
            1,
            1 ether,
            86400,
            {"from": self.accounts[1]}
        )
        
        # Test buy now with overpayment (vulnerable to slippage)
        try:
            marketplace.buyNow(listing_id, {"from": self.accounts[2], "value": 5 ether})
            print("⚠️  Slippage vulnerability detected - user overpaid")
        except Exception as e:
            print(f"✅ Slippage protection working: {e}")


@pytest.mark.security
class TestTokenSaleSecurity:
    """Security tests for TokenSale"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.security_suite = SecurityTestSuite()
    
    def test_token_sale_reentrancy(self):
        """Test reentrancy in token sale"""
        print("\n🔍 Testing TokenSale reentrancy...")
        
        # Deploy token sale
        token_sale = TokenSale.deploy(
            self.accounts[1],  # Mock token address
            self.accounts[0],  # Wallet
            block.timestamp + 3600,  # Start in 1 hour
            86400,  # 24 hour duration
            {"from": self.accounts[0]}
        )
        
        # Create sale tier
        token_sale.createSaleTier(
            1,  # Tier ID
            1000,  # Rate (1000 tokens per ETH)
            0.1 ether,  # Min purchase
            10 ether,  # Max purchase
            100 ether,  # Hard cap
            {"from": self.accounts[0]}
        )
        
        # Start sale
        token_sale.startSale({"from": self.accounts[0]})
        
        # Test configuration
        test_config = {
            "reentrancy_functions": ["buyTokens", "claimTokens"],
            "overflow_functions": ["calculateTokenAmount"],
            "restricted_functions": ["startSale", "updateSaleTimes", "updateWallet"],
            "gas_functions": ["batchDistributeTokens"],
            "oracle_functions": ["getTokenPriceInUSD"],
            "swap_functions": ["buyExactTokens"],
            "flash_loan_functions": [],
            "amount": 1 ether,
            "large_input": 2**256 - 1
        }
        
        # Run security tests
        results = self.security_suite.run_all_tests(token_sale, test_config)
        
        # Generate report
        report = self.security_suite.generate_report(results)
        print(report)
        
        # Save report
        with open("reports/token_sale_security_report.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ TokenSale security tests completed")
    
    def test_token_sale_overflow(self):
        """Test integer overflow in token sale"""
        print("\n🔢 Testing TokenSale integer overflow...")
        
        token_sale = TokenSale.deploy(
            self.accounts[1],
            self.accounts[0],
            block.timestamp + 3600,
            86400,
            {"from": self.accounts[0]}
        )
        
        # Test overflow in rate calculation
        try:
            large_amount = 2**256 - 1
            result = token_sale.calculateTokenAmount(large_amount, 1000)
            print(f"⚠️  Overflow possible: {result}")
        except Exception as e:
            print(f"✅ Overflow protection working: {e}")
    
    def test_token_sale_front_running(self):
        """Test front-running in token sale"""
        print("\n🏃 Testing TokenSale front-running...")
        
        token_sale = TokenSale.deploy(
            self.accounts[1],
            self.accounts[0],
            block.timestamp + 3600,
            86400,
            {"from": self.accounts[0]}
        )
        
        token_sale.createSaleTier(
            1,
            1000,
            0.1 ether,
            10 ether,
            100 ether,
            {"from": self.accounts[0]}
        )
        
        token_sale.startSale({"from": self.accounts[0]})
        
        # Test front-running scenario
        try:
            token_sale.buyWithMinGas(1, {"from": self.accounts[1], "value": 1 ether})
            print("⚠️  Front-running vulnerability detected")
        except Exception as e:
            print(f"✅ Front-running protection working: {e}")


@pytest.mark.security
class TestSecureVaultComparison:
    """Compare SecureVault with VulnerableVault"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.accounts = accounts
        self.security_suite = SecurityTestSuite()
    
    def test_secure_vs_vulnerable_reentrancy(self):
        """Compare reentrancy protection between SecureVault and VulnerableVault"""
        print("\n🔒 Comparing reentrancy protection...")
        
        # Deploy both vaults
        vulnerable_vault = VulnerableVault.deploy({"from": self.accounts[0]})
        secure_vault = SecureVault.deploy({"from": self.accounts[0]})
        
        # Fund both vaults
        self.accounts[0].transfer(vulnerable_vault.address, "10 ether")
        self.accounts[0].transfer(secure_vault.address, "10 ether")
        
        # Make deposits
        vulnerable_vault.deposit({"from": self.accounts[1], "value": "5 ether"})
        secure_vault.deposit({"from": self.accounts[1], "value": "5 ether"})
        
        print(f"Vulnerable vault balance: {vulnerable_vault.balance()}")
        print(f"Secure vault balance: {secure_vault.balance()}")
        print(f"Vulnerable user balance: {vulnerable_vault.balances(self.accounts[1])}")
        print(f"Secure user balance: {secure_vault.balances(self.accounts[1])}")
        
        # Test withdrawals
        try:
            # Vulnerable vault withdrawal
            vulnerable_vault.withdraw(1 ether, {"from": self.accounts[1]})
            print("⚠️  VulnerableVault withdrawal succeeded (may be vulnerable)")
        except Exception as e:
            print(f"✅ VulnerableVault withdrawal failed: {e}")
        
        try:
            # Secure vault withdrawal
            secure_vault.withdraw(1 ether, {"from": self.accounts[1]})
            print("✅ SecureVault withdrawal succeeded")
        except Exception as e:
            print(f"❌ SecureVault withdrawal failed: {e}")
    
    def test_secure_vs_vulnerable_overflow(self):
        """Compare overflow protection"""
        print("\n🔢 Comparing overflow protection...")
        
        vulnerable_vault = VulnerableVault.deploy({"from": self.accounts[0]})
        secure_vault = SecureVault.deploy({"from": self.accounts[0]})
        
        # Test overflow scenarios
        try:
            # Vulnerable vault
            result = vulnerable_vault.calculateBonus(2**256 - 1)
            print(f"⚠️  VulnerableVault overflow result: {result}")
        except Exception as e:
            print(f"✅ VulnerableVault overflow protection: {e}")
        
        try:
            # Secure vault
            result = secure_vault.calculateBonus(2**256 - 1)
            print(f"✅ SecureVault overflow protection: {result}")
        except Exception as e:
            print(f"❌ SecureVault overflow failed: {e}")
    
    def test_secure_vs_vulnerable_access_control(self):
        """Compare access control mechanisms"""
        print("\n🔒 Comparing access control...")
        
        vulnerable_vault = VulnerableVault.deploy({"from": self.accounts[0]})
        secure_vault = SecureVault.deploy({"from": self.accounts[0]})
        
        # Test unauthorized access
        try:
            # Vulnerable vault - anyone can call emergencyWithdraw
            vulnerable_vault.emergencyWithdraw({"from": self.accounts[1]})
            print("⚠️  VulnerableVault access control bypass detected")
        except Exception as e:
            print(f"✅ VulnerableVault access control working: {e}")
        
        try:
            # Secure vault - emergency withdraw should work for user
            secure_vault.emergencyWithdraw(1 ether, {"from": self.accounts[1]})
            print("✅ SecureVault emergency withdraw works")
        except Exception as e:
            print(f"❌ SecureVault emergency withdraw failed: {e}")


@pytest.mark.security
@pytest.mark.integration
class TestSampleContractsIntegration:
    """Integration tests for sample contracts"""
    
    def test_complete_attack_scenario(self):
        """Test complete attack scenario across multiple contracts"""
        print("\n🎭 Testing complete attack scenario...")
        
        # Deploy contracts
        auction = AuctionContract.deploy({"from": accounts[0]})
        marketplace = NFTMarketplace.deploy({"from": accounts[0]})
        token_sale = TokenSale.deploy(
            accounts[1],
            accounts[0],
            block.timestamp + 3600,
            86400,
            {"from": accounts[0]}
        )
        
        # Setup attack scenario
        attacker = accounts[1]
        victim = accounts[2]
        
        # 1. Create auction
        auction_id = auction.createAuction(
            "Valuable NFT",
            1000,
            0.1 ether,
            {"from": victim}
        )
        
        # 2. Start token sale
        token_sale.createSaleTier(1, 1000, 0.1 ether, 10 ether, 100 ether, {"from": accounts[0]})
        token_sale.startSale({"from": accounts[0]})
        
        # 3. Create NFT listing
        listing_id = marketplace.createListing(
            accounts[1],
            1,
            5 ether,
            86400,
            {"from": victim}
        )
        
        print(f"Attack setup complete:")
        print(f"- Auction ID: {auction_id}")
        print(f"- Token sale active: {token_sale.saleActive()}")
        print(f"- NFT listing ID: {listing_id}")
        
        # 4. Execute coordinated attacks
        try:
            # Front-run auction bid
            auction.placeBidWithMinGas(auction_id, 2 ether, {"from": attacker, "gasPrice": 100 gwei})
            
            # Manipulate token sale
            token_sale.buyWithMinGas(1, {"from": attacker, "gasPrice": 100 gwei})
            
            # Exploit NFT marketplace
            marketplace.buyNow(listing_id, {"from": attacker, "value": 10 ether})
            
            print("⚠️  Coordinated attack executed")
            
        except Exception as e:
            print(f"Attack failed: {e}")
        
        # 5. Analyze results
        print(f"Final state analysis:")
        print(f"- Auction highest bid: {auction.auctions(auction_id)[5]}")
        print(f"- Token sale total raised: {token_sale.totalRaised()}")
        print(f"- NFT listing active: {marketplace.listings(listing_id)[4]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
