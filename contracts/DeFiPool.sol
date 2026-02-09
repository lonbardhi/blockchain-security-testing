// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title DeFiPool
 * @dev A simplified DeFi liquidity pool for testing security patterns
 */
contract DeFiPool is ReentrancyGuard, Ownable {
    IERC20 public token;
    IERC20 public rewardToken;
    
    struct UserInfo {
        uint256 amount;
        uint256 rewardDebt;
        uint256 pendingRewards;
        uint256 lastDepositTime;
    }
    
    mapping(address => UserInfo) public userInfo;
    address[] public stakers;
    
    uint256 public totalStaked;
    uint256 public rewardRate = 100; // tokens per block
    uint256 public lastUpdateTime;
    uint256 public accRewardPerShare;
    
    uint256 public constant MIN_STAKE = 100 * 10**18;
    uint256 public constant MAX_STAKE = 1000000 * 10**18;
    uint256 public constant COOLDOWN_PERIOD = 1 days;
    
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);
    event EmergencyWithdraw(address indexed user, uint256 amount);
    
    constructor(address _token, address _rewardToken) {
        token = IERC20(_token);
        rewardToken = IERC20(_rewardToken);
        lastUpdateTime = block.number;
    }
    
    /**
     * @dev Update reward variables
     */
    function updateReward() internal {
        if (block.number <= lastUpdateTime) {
            return;
        }
        
        uint256 multiplier = block.number - lastUpdateTime;
        if (totalStaked > 0) {
            accRewardPerShare += (multiplier * rewardRate * 1e12) / totalStaked;
        }
        lastUpdateTime = block.number;
    }
    
    /**
     * @dev Stake tokens in the pool
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount >= MIN_STAKE, "Amount below minimum stake");
        require(amount <= MAX_STAKE, "Amount exceeds maximum stake");
        
        UserInfo storage user = userInfo[msg.sender];
        
        updateReward();
        
        if (user.amount > 0) {
            user.pendingRewards += (user.amount * accRewardPerShare) / 1e12 - user.rewardDebt;
        }
        
        require(token.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        if (user.amount == 0) {
            stakers.push(msg.sender);
        }
        
        user.amount += amount;
        user.rewardDebt = (user.amount * accRewardPerShare) / 1e12;
        user.lastDepositTime = block.timestamp;
        totalStaked += amount;
        
        emit Staked(msg.sender, amount);
    }
    
    /**
     * @dev Withdraw staked tokens
     */
    function withdraw(uint256 amount) external nonReentrant {
        UserInfo storage user = userInfo[msg.sender];
        require(user.amount >= amount, "Insufficient staked amount");
        require(block.timestamp >= user.lastDepositTime + COOLDOWN_PERIOD, "Still in cooldown");
        
        updateReward();
        
        user.pendingRewards += (user.amount * accRewardPerShare) / 1e12 - user.rewardDebt;
        
        user.amount -= amount;
        user.rewardDebt = (user.amount * accRewardPerShare) / 1e12;
        totalStaked -= amount;
        
        require(token.transfer(msg.sender, amount), "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
    
    /**
     * @dev Claim pending rewards
     */
    function claimRewards() external nonReentrant {
        UserInfo storage user = userInfo[msg.sender];
        updateReward();
        
        uint256 pending = user.pendingRewards + (user.amount * accRewardPerShare) / 1e12 - user.rewardDebt;
        
        require(pending > 0, "No rewards to claim");
        require(rewardToken.balanceOf(address(this)) >= pending, "Insufficient reward tokens");
        
        user.pendingRewards = 0;
        user.rewardDebt = (user.amount * accRewardPerShare) / 1e12;
        
        require(rewardToken.transfer(msg.sender, pending), "Transfer failed");
        
        emit RewardClaimed(msg.sender, pending);
    }
    
    /**
     * @dev Emergency withdraw (forfeits rewards)
     */
    function emergencyWithdraw() external nonReentrant {
        UserInfo storage user = userInfo[msg.sender];
        require(user.amount > 0, "No staked tokens");
        
        uint256 amount = user.amount;
        
        user.amount = 0;
        user.rewardDebt = 0;
        user.pendingRewards = 0;
        totalStaked -= amount;
        
        require(token.transfer(msg.sender, amount), "Transfer failed");
        
        emit EmergencyWithdraw(msg.sender, amount);
    }
    
    /**
     * @dev VULNERABLE: Flash loan attack simulation
     */
    function flashLoan(uint256 amount) external nonReentrant {
        require(amount <= totalStaked, "Amount exceeds total staked");
        
        // VULNERABILITY: No flash loan fee or protection
        require(token.transfer(msg.sender, amount), "Flash loan transfer failed");
        
        // Expect callback to repay
        require(token.transferFrom(msg.sender, address(this), amount), "Flash loan repayment failed");
    }
    
    /**
     * @dev VULNERABLE: Oracle manipulation susceptible
     */
    function getTokenPrice() external view returns (uint256) {
        // VULNERABILITY: No oracle, uses manipulated price
        return 1000 * 10**18; // Fixed price for testing
    }
    
    /**
     * @dev VULNERABLE: Slippage protection missing
     */
    function swap(uint256 amountIn) external {
        // VULNERABILITY: No slippage protection
        require(token.transferFrom(msg.sender, address(this), amountIn), "Transfer failed");
        // Swap logic without slippage checks
    }
    
    /**
     * @dev Get pending rewards for user
     */
    function pendingReward(address user) external view returns (uint256) {
        UserInfo storage userInfo_ = userInfo[user];
        if (block.number > lastUpdateTime && totalStaked > 0) {
            uint256 accRewardPerShare_ = accRewardPerShare + 
                ((block.number - lastUpdateTime) * rewardRate * 1e12) / totalStaked;
            return userInfo_.pendingRewards + 
                (userInfo_.amount * accRewardPerShare_) / 1e12 - userInfo_.rewardDebt;
        } else {
            return userInfo_.pendingRewards + 
                (userInfo_.amount * accRewardPerShare) / 1e12 - userInfo_.rewardDebt;
        }
    }
    
    /**
     * @dev Get staker count
     */
    function stakerCount() external view returns (uint256) {
        return stakers.length;
    }
    
    /**
     * @dev Update reward rate (only owner)
     */
    function updateRewardRate(uint256 newRate) external onlyOwner {
        rewardRate = newRate;
    }
    
    /**
     * @dev Withdraw stuck tokens (only owner)
     */
    function withdrawStuckTokens(address _token, uint256 amount) external onlyOwner {
        require(IERC20(_token).transfer(msg.sender, amount), "Transfer failed");
    }
}
