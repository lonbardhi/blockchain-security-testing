// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title VulnerableVault
 * @dev A vault contract with intentional vulnerabilities for security testing
 * DO NOT USE IN PRODUCTION - FOR TESTING PURPOSES ONLY
 */
contract VulnerableVault {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public depositTimes;
    
    uint256 public totalDeposits;
    address public owner;
    bool public locked;
    
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier noReentrancy() {
        require(!locked, "Reentrancy detected");
        locked = true;
        _;
        locked = false;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Deposit funds into vault
     */
    function deposit() external payable {
        require(msg.value > 0, "Must deposit something");
        balances[msg.sender] += msg.value;
        totalDeposits += msg.value;
        depositTimes[msg.sender] = block.timestamp;
        emit Deposited(msg.sender, msg.value);
    }
    
    /**
     * @dev VULNERABLE: Withdraw function susceptible to reentrancy
     */
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(address(this).balance >= amount, "Insufficient vault balance");
        
        // VULNERABILITY: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
        totalDeposits -= amount;
        emit Withdrawn(msg.sender, amount);
    }
    
    /**
     * @dev SECURE: Withdraw function with reentrancy protection
     */
    function withdrawSecure(uint256 amount) external noReentrancy {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(address(this).balance >= amount, "Insufficient vault balance");
        
        // SECURE: State update before external call
        balances[msg.sender] -= amount;
        totalDeposits -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
    
    /**
     * @dev VULNERABLE: Integer overflow in bonus calculation
     */
    function calculateBonus(uint256 depositAmount) public pure returns (uint256) {
        // VULNERABILITY: Potential integer overflow
        return depositAmount * 110 / 100; // 10% bonus
    }
    
    /**
     * @dev VULNERABLE: Access control issue
     */
    function emergencyWithdraw() external {
        // VULNERABILITY: Anyone can call this function
        require(address(this).balance > 0, "No funds to withdraw");
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Transfer failed");
    }
    
    /**
     * @dev VULNERABLE: Unchecked return value
     */
    function transferOwnership(address newOwner) external {
        // VULNERABILITY: No validation of newOwner
        owner = newOwner;
    }
    
    /**
     * @dev VULNERABLE: Gas limit DoS
     */
    function distributeToAll(uint256 amount) external onlyOwner {
        address[] memory users = new address[](100);
        // VULNERABILITY: Unbounded loop can cause gas limit issues
        for (uint256 i = 0; i < users.length; i++) {
            if (balances[users[i]] > 0) {
                (bool success, ) = users[i].call{value: amount}("");
                // VULNERABILITY: Unchecked return value
            }
        }
    }
    
    /**
     * @dev VULNERABLE: Front-running susceptible
     */
    function placeBid(uint256 amount) external payable {
        // VULNERABILITY: No minimum bid protection
        require(msg.value == amount, "Incorrect amount");
        // Logic that can be front-run
    }
    
    /**
     * @dev VULNERABLE: Timestamp dependency
     */
    function isTimeLocked() external view returns (bool) {
        // VULNERABILITY: Relies on block.timestamp which can be manipulated
        return block.timestamp >= depositTimes[msg.sender] + 1 days;
    }
    
    /**
     * @dev VULNERABLE: Delegatecall to arbitrary address
     */
    function executeDelegate(address target, bytes calldata data) external onlyOwner {
        // VULNERABILITY: Arbitrary delegatecall can be dangerous
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegatecall failed");
    }
    
    receive() external payable {
        deposit();
    }
    
    fallback() external payable {
        deposit();
    }
}
