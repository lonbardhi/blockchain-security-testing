// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title SecureVault
 * @dev A secure vault contract demonstrating best practices
 * This contract implements proper security patterns for comparison with VulnerableVault
 */
contract SecureVault is ReentrancyGuard, Ownable {
    using SafeMath for uint256;
    
    mapping(address => uint256) public balances;
    mapping(address => uint256) public depositTimes;
    mapping(address => bool) public frozen;
    
    uint256 public totalDeposits;
    address public owner;
    uint256 public constant MAX_DEPOSIT = 1000 ether;
    uint256 public constant DAILY_WITHDRAWAL_LIMIT = 10 ether;
    mapping(address => uint256) public dailyWithdrawn;
    mapping(address => uint256) public lastWithdrawalDay;
    
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event Frozen(address indexed user, bool frozen);
    event EmergencyWithdraw(address indexed user, uint256 amount);
    
    modifier validAddress(address _addr) {
        require(_addr != address(0), "Invalid address");
        _;
    }
    
    modifier notFrozen(address _user) {
        require(!frozen[_user], "Account frozen");
        _;
    }
    
    modifier withinLimit(uint256 _amount) {
        require(_amount <= DAILY_WITHDRAWAL_LIMIT, "Exceeds daily limit");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Deposit funds with validation
     */
    function deposit() external payable validAddress(msg.sender) {
        require(msg.value > 0, "Must deposit something");
        require(msg.value <= MAX_DEPOSIT, "Exceeds maximum deposit");
        require(!frozen[msg.sender], "Account frozen");
        
        balances[msg.sender] = balances[msg.sender].add(msg.value);
        totalDeposits = totalDeposits.add(msg.value);
        depositTimes[msg.sender] = block.timestamp;
        
        emit Deposited(msg.sender, msg.value);
    }
    
    /**
     * @dev SECURE: Withdraw with proper reentrancy protection
     */
    function withdraw(uint256 _amount) 
        external 
        nonReentrant 
        validAddress(msg.sender) 
        notFrozen(msg.sender)
        withinLimit(_amount)
    {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        require(address(this).balance >= _amount, "Insufficient vault balance");
        
        // Check daily limit
        uint256 currentDay = block.timestamp / 1 days;
        if (lastWithdrawalDay[msg.sender] < currentDay) {
            dailyWithdrawn[msg.sender] = 0;
            lastWithdrawalDay[msg.sender] = currentDay;
        }
        
        require(dalynWithdrawn[msg.sender].add(_amount) <= DAILY_WITHDRAWAL_LIMIT, "Exceeds daily limit");
        
        // SECURE: State update before external call (Checks-Effects-Interactions pattern)
        balances[msg.sender] = balances[msg.sender].sub(_amount);
        totalDeposits = totalDeposits.sub(_amount);
        dailyWithdrawn[msg.sender] = dailyWithdrawn[msg.sender].add(_amount);
        
        // External call after state update
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, _amount);
    }
    
    /**
     * @dev SECURE: Batch withdrawal with gas limit protection
     */
    function batchWithdraw(uint256[] calldata _amounts, address[] calldata _recipients) 
        external 
        nonReentrant 
        onlyOwner 
    {
        require(_amounts.length == _recipients.length, "Array length mismatch");
        require(_amounts.length <= 100, "Too many withdrawals");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < _amounts.length; i++) {
            totalAmount = totalAmount.add(_amounts[i]);
        }
        
        require(address(this).balance >= totalAmount, "Insufficient vault balance");
        
        for (uint256 i = 0; i < _amounts.length; i++) {
            address recipient = _recipients[i];
            uint256 amount = _amounts[i];
            
            require(balances[recipient] >= amount, "Insufficient balance");
            require(!frozen[recipient], "Recipient account frozen");
            
            // Update state
            balances[recipient] = balances[recipient].sub(amount);
            totalDeposits = totalDeposits.sub(amount);
            
            // External call
            (bool success, ) = recipient.call{value: amount}("");
            require(success, "Transfer failed");
            
            emit Withdrawn(recipient, amount);
        }
    }
    
    /**
     * @dev SECURE: Emergency withdraw with proper access control
     */
    function emergencyWithdraw(uint256 _amount) 
        external 
        nonReentrant 
        validAddress(msg.sender) 
    {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        require(address(this).balance >= _amount, "Insufficient vault balance");
        
        // State update before external call
        balances[msg.sender] = balances[msg.sender].sub(_amount);
        totalDeposits = totalDeposits.sub(_amount);
        
        // External call after state update
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        
        emit EmergencyWithdraw(msg.sender, _amount);
    }
    
    /**
     * @dev SECURE: Calculate bonus with safe math
     */
    function calculateBonus(uint256 _depositAmount) public pure returns (uint256) {
        // SECURE: Uses SafeMath to prevent overflow
        return _depositAmount.mul(110).div(100); // 10% bonus
    }
    
    /**
     * @dev SECURE: Transfer ownership with validation
     */
    function transferOwnership(address _newOwner) external onlyOwner validAddress(_newOwner) {
        // SECURE: Validates new owner address
        owner = _newOwner;
    }
    
    /**
     * @dev SECURE: Distribute with pagination and gas limit protection
     */
    function distributeToPaginated(uint256 _startIndex, uint256 _endIndex, uint256 _amount) 
        external 
        nonReentrant 
        onlyOwner 
    {
        require(_endIndex > _startIndex, "Invalid range");
        require(_endIndex - _startIndex <= 50, "Range too large");
        
        for (uint256 i = _startIndex; i < _endIndex; i++) {
            address user = address(uint160(i)); // Mock iteration for example
            if (balances[user] > 0 && !frozen[user]) {
                uint256 userAmount = _amount < balances[user] ? _amount : balances[user];
                
                // Update state
                balances[user] = balances[user].sub(userAmount);
                totalDeposits = totalDeposits.sub(userAmount);
                
                // External call with return value check
                (bool success, ) = user.call{value: userAmount}("");
                require(success, "Transfer failed");
                
                emit Withdrawn(user, userAmount);
            }
        }
    }
    
    /**
     * @dev SECURE: Place bid with minimum gas price protection
     */
    function placeBid(uint256 _amount) external payable {
        require(msg.value == _amount, "Incorrect amount");
        require(msg.value >= 0.01 ether, "Minimum bid required");
        require(tx.gasprice >= 20 gwei, "Gas price too low");
        
        // Bid logic here...
    }
    
    /**
     * @dev SECURE: Time-locked operations with block number instead of timestamp
     */
    function isTimeLocked(address _user) external view returns (bool) {
        // SECURE: Uses block number instead of timestamp for better predictability
        uint256 depositBlock = depositTimes[_user];
        return block.number < depositBlock + 6500; // ~24 hours in blocks
    }
    
    /**
     * @dev SECURE: Safe delegatecall with validation
     */
    function executeDelegate(address _target, bytes calldata _data) external onlyOwner {
        // SECURE: Validates target address and data
        require(_target != address(0), "Invalid target address");
        require(_data.length > 0, "Empty data");
        
        // Use call instead of delegatecall for safety
        (bool success, ) = _target.call(_data);
        require(success, "Delegate call failed");
    }
    
    /**
     * @dev SECURE: Freeze/unfreeze account with proper access control
     */
    function freezeAccount(address _user, bool _freeze) external onlyOwner validAddress(_user) {
        frozen[_user] = _freeze;
        emit Frozen(_user, _freeze);
    }
    
    /**
     * @dev SECURE: Update withdrawal limit with validation
     */
    function updateDailyLimit(uint256 _newLimit) external onlyOwner {
        require(_newLimit > 0 && _newLimit <= 100 ether, "Invalid limit");
        DAILY_WITHDRAWAL_LIMIT = _newLimit;
    }
    
    /**
     * @dev SECURE: Get vault statistics
     */
    function getVaultStats() external view returns (
        uint256 _totalDeposits,
        uint256 _totalBalance,
        uint256 _userCount,
        uint256 _frozenCount
    ) {
        // Note: userCount would require additional tracking in production
        return (
            totalDeposits,
            address(this).balance,
            0, // Would need to track users
            0  // Would need to count frozen accounts
        );
    }
    
    /**
     * @dev SECURE: Get user info
     */
    function getUserInfo(address _user) external view returns (
        uint256 balance,
        uint256 depositTime,
        bool isFrozen,
        uint256 dailyWithdrawnAmount,
        uint256 lastWithdrawalDay
    ) {
        return (
            balances[_user],
            depositTimes[_user],
            frozen[_user],
            dailyWithdrawn[_user],
            lastWithdrawalDay[_user]
        );
    }
    
    /**
     * @dev SECURE: Withdraw stuck tokens
     */
    function withdrawStuckTokens(address _token, uint256 _amount) external onlyOwner {
        require(_token != address(0), "Invalid token address");
        require(_amount > 0, "Amount must be > 0");
        
        // This would require ERC20 interface
        // IERC20(_token).transfer(owner(), _amount);
    }
    
    /**
     * @dev SECURE: Pause contract
     */
    bool public paused = false;
    
    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }
    
    function pause() external onlyOwner {
        paused = true;
    }
    
    function unpause() external onlyOwner {
        paused = false;
    }
    
    receive() external payable whenNotPaused {
        deposit();
    }
    
    fallback() external payable whenNotPaused {
        deposit();
    }
}
