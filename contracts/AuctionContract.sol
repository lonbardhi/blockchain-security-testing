// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AuctionContract
 * @dev Auction contract with multiple security vulnerabilities for testing
 * DO NOT USE IN PRODUCTION - FOR TESTING PURPOSES ONLY
 */
contract AuctionContract is ReentrancyGuard, Ownable {
    struct Auction {
        uint256 id;
        address payable seller;
        uint256 startBlock;
        uint256 endBlock;
        string description;
        uint256 highestBid;
        address payable highestBidder;
        bool ended;
        uint256 minBidIncrement;
    }
    
    mapping(uint256 => Auction) public auctions;
    mapping(uint256 => mapping(address => uint256)) public pendingReturns;
    mapping(address => uint256) public userAuctions;
    
    uint256 public nextAuctionId;
    uint256 public constant MIN_AUCTION_DURATION = 100; // blocks
    
    event AuctionCreated(uint256 indexed auctionId, address indexed seller, string description);
    event BidPlaced(uint256 indexed auctionId, address indexed bidder, uint256 amount);
    event AuctionEnded(uint256 indexed auctionId, address indexed winner, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    constructor() {
        nextAuctionId = 1;
    }
    
    /**
     * @dev Create new auction
     */
    function createAuction(
        string memory _description,
        uint256 _duration,
        uint256 _minBidIncrement
    ) external returns (uint256) {
        require(_duration >= MIN_AUCTION_DURATION, "Duration too short");
        require(_minBidIncrement > 0, "Min bid increment must be > 0");
        
        uint256 auctionId = nextAuctionId++;
        Auction storage auction = auctions[auctionId];
        
        auction.id = auctionId;
        auction.seller = payable(msg.sender);
        auction.startBlock = block.number;
        auction.endBlock = block.number + _duration;
        auction.description = _description;
        auction.highestBid = 0;
        auction.highestBidder = payable(address(0));
        auction.ended = false;
        auction.minBidIncrement = _minBidIncrement;
        
        userAuctions[msg.sender] = auctionId;
        
        emit AuctionCreated(auctionId, msg.sender, _description);
        return auctionId;
    }
    
    /**
     * @dev VULNERABLE: Bid function with reentrancy and access control issues
     */
    function bid(uint256 _auctionId) external payable {
        Auction storage auction = auctions[_auctionId];
        require(block.number < auction.endBlock, "Auction ended");
        require(!auction.ended, "Auction already ended");
        require(msg.value >= auction.highestBid + auction.minBidIncrement, "Bid too low");
        
        // VULNERABILITY: External call before state update
        if (auction.highestBidder != address(0)) {
            (bool success, ) = auction.highestBidder.call{value: auction.highestBid}("");
            require(success, "Refund failed");
        }
        
        auction.highestBid = msg.value;
        auction.highestBidder = payable(msg.sender);
        
        emit BidPlaced(_auctionId, msg.sender, msg.value);
    }
    
    /**
     * @dev SECURE: Bid function with reentrancy protection
     */
    function bidSecure(uint256 _auctionId) external payable nonReentrant {
        Auction storage auction = auctions[_auctionId];
        require(block.number < auction.endBlock, "Auction ended");
        require(!auction.ended, "Auction already ended");
        require(msg.value >= auction.highestBid + auction.minBidIncrement, "Bid too low");
        
        // SECURE: State update before external call
        uint256 refundAmount = auction.highestBid;
        auction.highestBid = msg.value;
        auction.highestBidder = payable(msg.sender);
        
        // External call after state update
        if (refundAmount > 0) {
            (bool success, ) = auction.highestBidder.call{value: refundAmount}("");
            require(success, "Refund failed");
        }
        
        emit BidPlaced(_auctionId, msg.sender, msg.value);
    }
    
    /**
     * @dev VULNERABLE: End auction with access control issue
     */
    function endAuction(uint256 _auctionId) external {
        Auction storage auction = auctions[_auctionId];
        require(block.number >= auction.endBlock, "Auction not ended");
        require(!auction.ended, "Auction already ended");
        
        // VULNERABILITY: Anyone can end auction
        auction.ended = true;
        
        // Transfer highest bid to seller
        (bool success, ) = auction.seller.call{value: auction.highestBid}("");
        require(success, "Transfer to seller failed");
        
        emit AuctionEnded(_auctionId, auction.highestBidder, auction.highestBid);
    }
    
    /**
     * @dev SECURE: End auction with proper access control
     */
    function endAuctionSecure(uint256 _auctionId) external nonReentrant {
        Auction storage auction = auctions[_auctionId];
        require(block.number >= auction.endBlock, "Auction not ended");
        require(!auction.ended, "Auction already ended");
        require(msg.sender == auction.seller || msg.sender == owner(), "Not authorized");
        
        auction.ended = true;
        
        // Transfer highest bid to seller
        (bool success, ) = auction.seller.call{value: auction.highestBid}("");
        require(success, "Transfer to seller failed");
        
        emit AuctionEnded(_auctionId, auction.highestBidder, auction.highestBid);
    }
    
    /**
     * @dev VULNERABLE: Withdraw with integer overflow
     */
    function withdraw(uint256 _auctionId) external {
        uint256 amount = pendingReturns[_auctionId][msg.sender];
        require(amount > 0, "No funds to withdraw");
        
        // VULNERABILITY: Integer overflow possible
        pendingReturns[_auctionId][msg.sender] = 0;
        
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Withdrawal failed");
        
        emit Withdrawal(msg.sender, amount);
    }
    
    /**
     * @dev VULNERABLE: Front-running susceptible
     */
    function placeBidWithMinGas(uint256 _auctionId, uint256 _bidAmount) external payable {
        Auction storage auction = auctions[_auctionId];
        
        // VULNERABILITY: No minimum gas price protection
        require(msg.value == _bidAmount, "Incorrect amount");
        require(_bidAmount >= auction.highestBid + auction.minBidIncrement, "Bid too low");
        
        // Same logic as vulnerable bid function
        if (auction.highestBidder != address(0)) {
            (bool success, ) = auction.highestBidder.call{value: auction.highestBid}("");
            require(success, "Refund failed");
        }
        
        auction.highestBid = _bidAmount;
        auction.highestBidder = payable(msg.sender);
        
        emit BidPlaced(_auctionId, msg.sender, _bidAmount);
    }
    
    /**
     * @dev VULNERABLE: Timestamp dependency
     */
    function isAuctionActive(uint256 _auctionId) external view returns (bool) {
        Auction storage auction = auctions[_auctionId];
        // VULNERABILITY: Relies on block.timestamp which can be manipulated
        return block.timestamp < (auction.startBlock + auction.endBlock);
    }
    
    /**
     * @dev VULNERABLE: Unbounded loop
     */
    function refundAllBidders(uint256 _auctionId) external {
        Auction storage auction = auctions[_auctionId];
        
        // VULNERABILITY: Unbounded loop can cause gas limit issues
        for (uint256 i = 0; i < 1000; i++) {
            address bidder = address(uint160(i)); // Mock iteration
            uint256 refund = pendingReturns[_auctionId][bidder];
            if (refund > 0) {
                (bool success, ) = payable(bidder).call{value: refund}("");
                // VULNERABILITY: Unchecked return value
            }
        }
    }
    
    /**
     * @dev VULNERABLE: Delegatecall to arbitrary address
     */
    function executeDelegate(uint256 _auctionId, address _target, bytes calldata _data) external onlyOwner {
        // VULNERABILITY: Arbitrary delegatecall can be dangerous
        (bool success, ) = _target.delegatecall(_data);
        require(success, "Delegatecall failed");
    }
    
    /**
     * @dev Get auction details
     */
    function getAuction(uint256 _auctionId) external view returns (
        uint256 id,
        address payable seller,
        uint256 startBlock,
        uint256 endBlock,
        string memory description,
        uint256 highestBid,
        address payable highestBidder,
        bool ended,
        uint256 minBidIncrement
    ) {
        Auction storage auction = auctions[_auctionId];
        return (
            auction.id,
            auction.seller,
            auction.startBlock,
            auction.endBlock,
            auction.description,
            auction.highestBid,
            auction.highestBidder,
            auction.ended,
            auction.minBidIncrement
        );
    }
    
    /**
     * @dev Get user's pending returns
     */
    function getPendingReturns(uint256 _auctionId, address _user) external view returns (uint256) {
        return pendingReturns[_auctionId][_user];
    }
    
    receive() external payable {
        // Allow contract to receive ETH
    }
}
