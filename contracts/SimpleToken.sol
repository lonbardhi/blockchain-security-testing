// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title SimpleToken
 * @dev ERC20 token with security features for testing
 */
contract SimpleToken is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 1000000 * 10**18; // 1M tokens
    
    mapping(address => bool) public blacklisted;
    mapping(address => uint256) public lastTransferTime;
    
    event Blacklisted(address indexed account, bool status);
    event TokensBurned(address indexed burner, uint256 amount);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        require(initialSupply <= MAX_SUPPLY, "Initial supply exceeds maximum");
        _mint(msg.sender, initialSupply);
    }
    
    /**
     * @dev Mint new tokens (only owner)
     */
    function mint(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Cannot mint to zero address");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds maximum supply");
        _mint(to, amount);
    }
    
    /**
     * @dev Burn tokens
     */
    function burn(uint256 amount) external nonReentrant {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _burn(msg.sender, amount);
        emit TokensBurned(msg.sender, amount);
    }
    
    /**
     * @dev Transfer with rate limiting and blacklist check
     */
    function transfer(address to, uint256 amount) 
        public 
        override 
        nonReentrant 
        returns (bool) 
    {
        require(!blacklisted[msg.sender], "Sender is blacklisted");
        require(!blacklisted[to], "Recipient is blacklisted");
        require(block.timestamp - lastTransferTime[msg.sender] >= 1 minutes, "Rate limited");
        
        lastTransferTime[msg.sender] = block.timestamp;
        return super.transfer(to, amount);
    }
    
    /**
     * @dev TransferFrom with additional security checks
     */
    function transferFrom(
        address from,
        address to, 
        uint256 amount
    ) public override nonReentrant returns (bool) {
        require(!blacklisted[from], "Sender is blacklisted");
        require(!blacklisted[to], "Recipient is blacklisted");
        require(block.timestamp - lastTransferTime[from] >= 1 minutes, "Rate limited");
        
        lastTransferTime[from] = block.timestamp;
        return super.transferFrom(from, to, amount);
    }
    
    /**
     * @dev Blacklist/unblacklist account (only owner)
     */
    function setBlacklist(address account, bool status) external onlyOwner {
        blacklisted[account] = status;
        emit Blacklisted(account, status);
    }
    
    /**
     * @dev Emergency pause functionality
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
    
    function transfer(address to, uint256 amount) 
        public 
        override 
        whenNotPaused
        nonReentrant 
        returns (bool) 
    {
        return super.transfer(to, amount);
    }
}
