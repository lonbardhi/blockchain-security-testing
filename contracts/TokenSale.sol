// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TokenSale
 * @dev Token sale contract with multiple security vulnerabilities for testing
 * DO NOT USE IN PRODUCTION - FOR TESTING PURPOSES ONLY
 */
contract TokenSale is ReentrancyGuard, Ownable {
    struct SaleTier {
        uint256 rate;
        uint256 minPurchase;
        uint256 maxPurchase;
        uint256 totalSold;
        uint256 hardCap;
        bool active;
    }
    
    IERC20 public token;
    address payable public wallet;
    
    mapping(uint256 => SaleTier) public saleTiers;
    mapping(address => uint256) public contributions;
    mapping(address => uint256) public tokenBalances;
    
    uint256 public totalRaised;
    uint256 public totalTokensSold;
    uint256 public saleStartTime;
    uint256 public saleEndTime;
    uint256 public constant MAX_CONTRIBUTION = 1000 ether;
    
    bool public saleActive;
    bool public emergencyPaused;
    
    event TokensPurchased(address indexed buyer, uint256 ethAmount, uint256 tokenAmount, uint256 tierId);
    event SaleStarted(uint256 startTime, uint256 endTime);
    event SaleEnded(uint256 totalRaised, uint256 totalSold);
    event EmergencyPause(bool paused);
    
    constructor(
        address _token,
        address payable _wallet,
        uint256 _startTime,
        uint256 _duration
    ) {
        token = IERC20(_token);
        wallet = _wallet;
        saleStartTime = _startTime;
        saleEndTime = _startTime + _duration;
        saleActive = false;
        emergencyPaused = false;
    }
    
    /**
     * @dev Create sale tier
     */
    function createSaleTier(
        uint256 _tierId,
        uint256 _rate,
        uint256 _minPurchase,
        uint256 _maxPurchase,
        uint256 _hardCap
    ) external onlyOwner {
        require(_rate > 0, "Rate must be > 0");
        require(_minPurchase > 0, "Min purchase must be > 0");
        require(_maxPurchase >= _minPurchase, "Max must be >= min");
        require(_hardCap > 0, "Hard cap must be > 0");
        
        SaleTier storage tier = saleTiers[_tierId];
        tier.rate = _rate;
        tier.minPurchase = _minPurchase;
        tier.maxPurchase = _maxPurchase;
        tier.totalSold = 0;
        tier.hardCap = _hardCap;
        tier.active = true;
    }
    
    /**
     * @dev VULNERABLE: Buy tokens with reentrancy and access control issues
     */
    function buyTokens(uint256 _tierId) external payable {
        require(saleActive && !emergencyPaused, "Sale not active");
        require(block.timestamp >= saleStartTime, "Sale not started");
        require(block.timestamp <= saleEndTime, "Sale ended");
        require(msg.value > 0, "Must send ETH");
        
        SaleTier storage tier = saleTiers[_tierId];
        require(tier.active, "Tier not active");
        require(msg.value >= tier.minPurchase, "Below minimum purchase");
        require(msg.value <= tier.maxPurchase, "Above maximum purchase");
        require(contributions[msg.sender] + msg.value <= MAX_CONTRIBUTION, "Exceeds max contribution");
        require(tier.totalSold + msg.value <= tier.hardCap, "Tier hard cap reached");
        
        uint256 tokenAmount = (msg.value * tier.rate) / 1 ether;
        
        // VULNERABILITY: External call before state update
        (bool success, ) = wallet.call{value: msg.value}("");
        require(success, "Payment to wallet failed");
        
        // Update state after external call
        contributions[msg.sender] += msg.value;
        tokenBalances[msg.sender] += tokenAmount;
        totalRaised += msg.value;
        totalTokensSold += tokenAmount;
        tier.totalSold += msg.value;
        
        emit TokensPurchased(msg.sender, msg.value, tokenAmount, _tierId);
    }
    
    /**
     * @dev SECURE: Buy tokens with proper protections
     */
    function buyTokensSecure(uint256 _tierId) external payable nonReentrant {
        require(saleActive && !emergencyPaused, "Sale not active");
        require(block.timestamp >= saleStartTime, "Sale not started");
        require(block.timestamp <= saleEndTime, "Sale ended");
        require(msg.value > 0, "Must send ETH");
        
        SaleTier storage tier = saleTiers[_tierId];
        require(tier.active, "Tier not active");
        require(msg.value >= tier.minPurchase, "Below minimum purchase");
        require(msg.value <= tier.maxPurchase, "Above maximum purchase");
        require(contributions[msg.sender] + msg.value <= MAX_CONTRIBUTION, "Exceeds max contribution");
        require(tier.totalSold + msg.value <= tier.hardCap, "Tier hard cap reached");
        
        uint256 tokenAmount = (msg.value * tier.rate) / 1 ether;
        
        // SECURE: State update before external call
        contributions[msg.sender] += msg.value;
        tokenBalances[msg.sender] += tokenAmount;
        totalRaised += msg.value;
        totalTokensSold += tokenAmount;
        tier.totalSold += msg.value;
        
        // External call after state update
        (bool success, ) = wallet.call{value: msg.value}("");
        require(success, "Payment to wallet failed");
        
        emit TokensPurchased(msg.sender, msg.value, tokenAmount, _tierId);
    }
    
    /**
     * @dev VULNERABLE: Claim tokens with reentrancy
     */
    function claimTokens() external {
        require(tokenBalances[msg.sender] > 0, "No tokens to claim");
        require(block.timestamp > saleEndTime, "Sale not ended");
        
        uint256 amount = tokenBalances[msg.sender];
        
        // VULNERABILITY: External call before state update
        require(token.transfer(msg.sender, amount), "Token transfer failed");
        
        // Update state after external call
        tokenBalances[msg.sender] = 0;
    }
    
    /**
     * @dev SECURE: Claim tokens with proper protections
     */
    function claimTokensSecure() external nonReentrant {
        require(tokenBalances[msg.sender] > 0, "No tokens to claim");
        require(block.timestamp > saleEndTime, "Sale not ended");
        
        uint256 amount = tokenBalances[msg.sender];
        tokenBalances[msg.sender] = 0;
        
        require(token.transfer(msg.sender, amount), "Token transfer failed");
    }
    
    /**
     * @dev VULNERABLE: Start sale with access control issue
     */
    function startSale() external {
        // VULNERABILITY: Anyone can start sale
        // Should require: msg.sender == owner
        require(!saleActive, "Sale already active");
        require(block.timestamp >= saleStartTime, "Sale time not reached");
        
        saleActive = true;
        emit SaleStarted(saleStartTime, saleEndTime);
    }
    
    /**
     * @dev VULNERABLE: Emergency functions with no proper validation
     */
    function emergencyPauseSale() external {
        // VULNERABILITY: Anyone can pause sale
        emergencyPaused = true;
        emit EmergencyPause(true);
    }
    
    function emergencyUnpauseSale() external onlyOwner {
        emergencyPaused = false;
        emit EmergencyPause(false);
    }
    
    /**
     * @dev VULNERABLE: Update sale parameters without validation
     */
    function updateSaleTimes(uint256 _newStartTime, uint256 _newEndTime) external {
        // VULNERABILITY: No access control
        // Should require: msg.sender == owner
        require(_newEndTime > _newStartTime, "Invalid time range");
        
        saleStartTime = _newStartTime;
        saleEndTime = _newEndTime;
    }
    
    /**
     * @dev VULNERABLE: Update wallet without validation
     */
    function updateWallet(address payable _newWallet) external {
        // VULNERABILITY: No access control
        // Should require: msg.sender == owner
        require(_newWallet != address(0), "Invalid wallet address");
        wallet = _newWallet;
    }
    
    /**
     * @dev VULNERABLE: Integer overflow in rate calculation
     */
    function calculateTokenAmount(uint256 _ethAmount, uint256 _rate) public pure returns (uint256) {
        // VULNERABILITY: Potential integer overflow
        return (_ethAmount * _rate) / 1 ether;
    }
    
    /**
     * @dev VULNERABLE: Front-running susceptible
     */
    function buyWithMinGas(uint256 _tierId) external payable {
        // VULNERABILITY: No minimum gas price protection
        // Can be front-run by bots
        
        SaleTier storage tier = saleTiers[_tierId];
        require(tier.active, "Tier not active");
        require(msg.value >= tier.minPurchase, "Below minimum purchase");
        
        uint256 tokenAmount = (msg.value * tier.rate) / 1 ether;
        
        contributions[msg.sender] += msg.value;
        tokenBalances[msg.sender] += tokenAmount;
        totalRaised += msg.value;
        totalTokensSold += tokenAmount;
        tier.totalSold += msg.value;
        
        (bool success, ) = wallet.call{value: msg.value}("");
        require(success, "Payment to wallet failed");
        
        emit TokensPurchased(msg.sender, msg.value, tokenAmount, _tierId);
    }
    
    /**
     * @dev VULNERABLE: Gas limit DoS
     */
    function batchDistributeTokens(address[] calldata _recipients) external onlyOwner {
        // VULNERABILITY: Unbounded loop can cause gas limit issues
        for (uint256 i = 0; i < _recipients.length; i++) {
            address recipient = _recipients[i];
            uint256 amount = tokenBalances[recipient];
            
            if (amount > 0) {
                tokenBalances[recipient] = 0;
                (bool success, ) = token.transfer(recipient, amount);
                // VULNERABILITY: Unchecked return value
            }
        }
    }
    
    /**
     * @dev VULNERABLE: Oracle manipulation
     */
    function getTokenPriceInUSD() external view returns (uint256) {
        // VULNERABILITY: Fixed price oracle that can be manipulated
        // Should use proper price oracle like Chainlink
        return 2000 * 10**8; // Fixed $2000
    }
    
    /**
     * @dev VULNERABLE: Slippage protection missing
     */
    function buyExactTokens(uint256 _tokenAmount, uint256 _tierId) external payable {
        SaleTier storage tier = saleTiers[_tierId];
        require(tier.active, "Tier not active");
        
        uint256 requiredEth = (_tokenAmount * 1 ether) / tier.rate;
        
        // VULNERABILITY: No slippage protection
        // User might pay much more than intended
        require(msg.value >= requiredEth, "Insufficient ETH");
        
        uint256 actualTokens = (msg.value * tier.rate) / 1 ether;
        
        contributions[msg.sender] += msg.value;
        tokenBalances[msg.sender] += actualTokens;
        totalRaised += msg.value;
        totalTokensSold += actualTokens;
        tier.totalSold += msg.value;
        
        (bool success, ) = wallet.call{value: msg.value}("");
        require(success, "Payment to wallet failed");
        
        emit TokensPurchased(msg.sender, msg.value, actualTokens, _tierId);
    }
    
    /**
     * @dev VULNERABLE: Delegatecall to arbitrary address
     */
    function executeDelegate(address _target, bytes calldata _data) external onlyOwner {
        // VULNERABILITY: Arbitrary delegatecall can be dangerous
        (bool success, ) = _target.delegatecall(_data);
        require(success, "Delegatecall failed");
    }
    
    /**
     * @dev Get sale statistics
     */
    function getSaleStats() external view returns (
        uint256 _totalRaised,
        uint256 _totalTokensSold,
        uint256 _saleStartTime,
        uint256 _saleEndTime,
        bool _saleActive,
        bool _emergencyPaused
    ) {
        return (
            totalRaised,
            totalTokensSold,
            saleStartTime,
            saleEndTime,
            saleActive,
            emergencyPaused
        );
    }
    
    /**
     * @dev Get user contribution and token balance
     */
    function getUserInfo(address _user) external view returns (uint256 contribution, uint256 tokenBalance) {
        return (contributions[_user], tokenBalances[_user]);
    }
    
    /**
     * @dev Get tier information
     */
    function getTierInfo(uint256 _tierId) external view returns (
        uint256 rate,
        uint256 minPurchase,
        uint256 maxPurchase,
        uint256 totalSold,
        uint256 hardCap,
        bool active
    ) {
        SaleTier storage tier = saleTiers[_tierId];
        return (
            tier.rate,
            tier.minPurchase,
            tier.maxPurchase,
            tier.totalSold,
            tier.hardCap,
            tier.active
        );
    }
    
    /**
     * @dev Withdraw stuck tokens (only owner)
     */
    function withdrawStuckTokens(address _token, uint256 _amount) external onlyOwner {
        require(IERC20(_token).transfer(owner(), _amount), "Transfer failed");
    }
    
    /**
     * @dev Withdraw stuck ETH (only owner)
     */
    function withdrawStuckETH() external onlyOwner {
        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Withdrawal failed");
    }
    
    receive() external payable {
        // Allow contract to receive ETH
    }
}
