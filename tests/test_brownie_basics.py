"""
Brownie Basics Tests - Simple examples for learning
Run with: brownie test tests/test_brownie_basics.py
"""

import pytest
from brownie import accounts, SimpleToken, VulnerableVault, reverts


class TestBrownieBasics:
    """Test class demonstrating Brownie basics"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Fixture providing a deployed token contract"""
        deployer = accounts[0]
        return SimpleToken.deploy(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            {"from": deployer}
        )
    
    @pytest.fixture(scope="class")
    def vault(self):
        """Fixture providing a funded vault contract"""
        deployer = accounts[0]
        vault = VulnerableVault.deploy({"from": deployer})
        deployer.transfer(vault.address, "10 ether")
        return vault
    
    @pytest.fixture
    def user(self):
        """Fixture providing a test user account"""
        return accounts[1]
    
    @pytest.fixture
    def another_user(self):
        """Fixture providing another test user account"""
        return accounts[2]
    
    def test_token_deployment(self, token):
        """Test basic token deployment"""
        # Assert basic token properties
        assert token.name() == "Test Token"
        assert token.symbol() == "TEST"
        assert token.totalSupply() == 1000000 * 10**18
        
        # Assert deployer owns all tokens initially
        deployer = accounts[0]
        assert token.balanceOf(deployer) == 1000000 * 10**18
    
    def test_vault_deployment(self, vault):
        """Test basic vault deployment"""
        # Assert vault properties
        assert vault.owner() == accounts[0].address
        assert vault.balance() == "10 ether"
        assert vault.totalDeposits() == 0  # No deposits yet
    
    def test_token_transfer(self, token, user, another_user):
        """Test basic token transfer"""
        deployer = accounts[0]
        transfer_amount = 1000 * 10**18
        
        # Transfer from deployer to user
        token.transfer(user, transfer_amount, {"from": deployer})
        
        # Assert balances
        assert token.balanceOf(user) == transfer_amount
        assert token.balanceOf(deployer) == 1000000 * 10**18 - transfer_amount
        
        # Transfer from user to another_user
        transfer_amount2 = 500 * 10**18
        token.transfer(another_user, transfer_amount2, {"from": user})
        
        # Assert new balances
        assert token.balanceOf(user) == transfer_amount - transfer_amount2
        assert token.balanceOf(another_user) == transfer_amount2
    
    def test_vault_deposit_withdraw(self, vault, user):
        """Test basic vault deposit and withdraw"""
        deposit_amount = "2 ether"
        
        # Deposit
        vault.deposit({"from": user, "value": deposit_amount})
        
        # Assert deposit
        assert vault.balances(user) == deposit_amount
        assert vault.balance() == "12 ether"  # 10 + 2
        assert vault.totalDeposits() == deposit_amount
        
        # Withdraw
        withdraw_amount = "1 ether"
        vault.withdraw(withdraw_amount, {"from": user})
        
        # Assert withdrawal
        assert vault.balances(user) == "1 ether"
        assert vault.balance() == "11 ether"  # 12 - 1
    
    def test_insufficient_balance_transfer(self, token, user):
        """Test transfer with insufficient balance"""
        # User has no tokens initially
        with reverts():
            token.transfer(accounts[0], 100 * 10**18, {"from": user})
    
    def test_insufficient_vault_withdraw(self, vault, user):
        """Test vault withdraw with insufficient balance"""
        # User has no vault balance initially
        with reverts():
            vault.withdraw("1 ether", {"from": user})
    
    def test_zero_transfer(self, token, user):
        """Test zero token transfer"""
        deployer = accounts[0]
        
        # Zero transfer should work
        token.transfer(user, 0, {"from": deployer})
        assert token.balanceOf(user) == 0
    
    def test_transaction_gas_analysis(self, token, user):
        """Test transaction gas usage"""
        deployer = accounts[0]
        transfer_amount = 100 * 10**18
        
        # Perform transfer and check gas
        tx = token.transfer(user, transfer_amount, {"from": deployer})
        
        # Assert transaction properties
        assert tx.gas_used > 0
        assert tx.gas_price > 0
        assert tx.cost() > 0
        assert tx.status == 1  # Success
        
        # Check events
        assert "Transfer" in tx.events
        assert tx.events["Transfer"]["from"] == deployer.address
        assert tx.events["Transfer"]["to"] == user.address
        assert tx.events["Transfer"]["value"] == transfer_amount
    
    def test_token_approval(self, token, user, another_user):
        """Test token approval and transferFrom"""
        deployer = accounts[0]
        approval_amount = 500 * 10**18
        
        # Approve user to spend deployer's tokens
        token.approve(user, approval_amount, {"from": deployer})
        
        # Check allowance
        assert token.allowance(deployer, user) == approval_amount
        
        # Transfer from deployer to another_user using approval
        transfer_amount = 300 * 10**18
        token.transferFrom(deployer, another_user, transfer_amount, {"from": user})
        
        # Assert balances and allowance
        assert token.balanceOf(another_user) == transfer_amount
        assert token.allowance(deployer, user) == approval_amount - transfer_amount
    
    def test_vault_bonus_calculation(self, vault, user):
        """Test vault bonus calculation (vulnerable to overflow)"""
        deposit_amount = "1 ether"
        
        # Deposit
        vault.deposit({"from": user, "value": deposit_amount})
        
        # Calculate bonus
        bonus = vault.calculateBonus(deposit_amount)
        expected_bonus = deposit_amount * 110 // 100  # 10% bonus
        
        assert bonus == expected_bonus
    
    def test_multiple_users(self, token):
        """Test operations with multiple users"""
        deployer = accounts[0]
        users = accounts[1:5]  # Get 4 users
        
        # Transfer tokens to each user
        for i, user in enumerate(users):
            amount = (i + 1) * 100 * 10**18
            token.transfer(user, amount, {"from": deployer})
        
        # Verify all balances
        for i, user in enumerate(users):
            expected_balance = (i + 1) * 100 * 10**18
            assert token.balanceOf(user) == expected_balance
    
    def test_contract_state_persistence(self, token, vault):
        """Test that contract state persists across transactions"""
        deployer = accounts[0]
        user = accounts[1]
        
        # Initial state
        initial_token_supply = token.totalSupply()
        initial_vault_balance = vault.balance()
        
        # Perform operations
        token.transfer(user, 100 * 10**18, {"from": deployer})
        vault.deposit({"from": user, "value": "1 ether"})
        
        # Verify state changes
        assert token.totalSupply() == initial_token_supply  # Transfer doesn't change supply
        assert vault.balance() == initial_vault_balance + "1 ether"
        assert token.balanceOf(user) == 100 * 10**18
        assert vault.balances(user) == "1 ether"


class TestBrownieAdvanced:
    """Advanced Brownie features demonstration"""
    
    def test_network_info(self):
        """Test getting network information"""
        from brownie import network
        
        # Should be running on development network
        assert network.show_active() == "development"
        
        # Should have gas limit
        assert network.gas_limit() > 0
    
    def test_account_operations(self):
        """Test account operations"""
        # Should have multiple accounts
        assert len(accounts) >= 10
        
        # First account should have ETH
        assert accounts[0].balance() > 0
        
        # Account addresses should be valid
        for account in accounts[:5]:
            assert account.address.startswith("0x")
            assert len(account.address) == 42
    
    def test_contract_interaction_patterns(self):
        """Test different contract interaction patterns"""
        deployer = accounts[0]
        user = accounts[1]
        
        # Deploy contract
        token = SimpleToken.deploy("Pattern Test", "PAT", 1000000 * 10**18, {"from": deployer})
        
        # Pattern 1: Direct call
        token.transfer(user, 100 * 10**18, {"from": deployer})
        
        # Pattern 2: Using contract.at() (for existing contracts)
        token_at = SimpleToken.at(token.address)
        assert token_at.balanceOf(user) == 100 * 10**18
        
        # Pattern 3: View functions (no transaction)
        total_supply = token.totalSupply()
        assert total_supply == 1000000 * 10**18
        
        # Pattern 4: Batch operations
        users = accounts[1:4]
        for i, user in enumerate(users):
            token.transfer(user, (i + 1) * 50 * 10**18, {"from": deployer})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
