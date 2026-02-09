// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title NFTMarketplace
 * @dev NFT marketplace with multiple security vulnerabilities for testing
 * DO NOT USE IN PRODUCTION - FOR TESTING PURPOSES ONLY
 */
contract NFTMarketplace is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    struct Listing {
        uint256 listingId;
        address nftContract;
        uint256 tokenId;
        address payable seller;
        uint256 price;
        bool active;
        uint256 createdAt;
        uint256 expiresAt;
    }
    
    struct Offer {
        uint256 offerId;
        uint256 listingId;
        address payable offeror;
        uint256 amount;
        uint256 expiresAt;
        bool active;
    }
    
    Counters.Counter private _listingIds;
    Counters.Counter private _offerIds;
    
    mapping(uint256 => Listing) public listings;
    mapping(uint256 => Offer[]) public listingOffers;
    mapping(uint256 => mapping(address => bool)) public hasOffered;
    
    uint256 public marketplaceFee = 250; // 2.5% in basis points
    uint256 public constant MAX_FEE = 1000; // 10%
    
    event ListingCreated(uint256 indexed listingId, address indexed seller, address nftContract, uint256 tokenId, uint256 price);
    event OfferMade(uint256 indexed offerId, uint256 indexed listingId, address indexed offeror, uint256 amount);
    event OfferAccepted(uint256 indexed listingId, uint256 indexed offerId, address buyer);
    event ListingCancelled(uint256 indexed listingId);
    event OfferWithdrawn(uint256 indexed offerId);
    
    constructor() {}
    
    /**
     * @dev VULNERABLE: Create listing with access control issues
     */
    function createListing(
        address _nftContract,
        uint256 _tokenId,
        uint256 _price,
        uint256 _duration
    ) external returns (uint256) {
        require(_price > 0, "Price must be > 0");
        require(_duration > 0, "Duration must be > 0");
        
        // VULNERABILITY: No NFT ownership check
        // Should check: IERC721(_nftContract).ownerOf(_tokenId) == msg.sender
        
        _listingIds.increment();
        uint256 listingId = _listingIds.current();
        
        Listing storage listing = listings[listingId];
        listing.listingId = listingId;
        listing.nftContract = _nftContract;
        listing.tokenId = _tokenId;
        listing.seller = payable(msg.sender);
        listing.price = _price;
        listing.active = true;
        listing.createdAt = block.timestamp;
        listing.expiresAt = block.timestamp + _duration;
        
        emit ListingCreated(listingId, msg.sender, _nftContract, _tokenId, _price);
        return listingId;
    }
    
    /**
     * @dev VULNERABLE: Make offer with reentrancy
     */
    function makeOffer(uint256 _listingId) external payable {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        require(block.timestamp < listing.expiresAt, "Listing expired");
        require(!hasOffered[_listingId][msg.sender], "Already offered");
        require(msg.value > 0, "Offer must be > 0");
        
        // VULNERABILITY: External call before state update
        // Should update state before any external calls
        
        _offerIds.increment();
        uint256 offerId = _offerIds.current();
        
        Offer memory offer = Offer({
            offerId: offerId,
            listingId: _listingId,
            offeror: payable(msg.sender),
            amount: msg.value,
            expiresAt: block.timestamp + 7 days,
            active: true
        });
        
        listingOffers[_listingId].push(offer);
        hasOffered[_listingId][msg.sender] = true;
        
        emit OfferMade(offerId, _listingId, msg.sender, msg.value);
    }
    
    /**
     * @dev VULNERABLE: Accept offer with reentrancy and access control issues
     */
    function acceptOffer(uint256 _listingId, uint256 _offerId) external {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        
        Offer storage offer = listingOffers[_listingId][_offerId];
        require(offer.active, "Offer not active");
        require(block.timestamp < offer.expiresAt, "Offer expired");
        
        // VULNERABILITY: No access control - anyone can accept any offer
        // Should require: msg.sender == listing.seller
        
        // VULNERABILITY: External call before state update
        uint256 fee = (offer.amount * marketplaceFee) / 10000;
        uint256 sellerAmount = offer.amount - fee;
        
        // Transfer NFT first (external call)
        IERC721(listing.nftContract).transferFrom(listing.seller, offer.offeror, listing.tokenId);
        
        // Then transfer ETH (external call)
        (bool success, ) = listing.seller.call{value: sellerAmount}("");
        require(success, "Payment to seller failed");
        
        // Update state after external calls
        listing.active = false;
        offer.active = false;
        
        emit OfferAccepted(_listingId, _offerId, offer.offeror);
    }
    
    /**
     * @dev SECURE: Accept offer with proper protections
     */
    function acceptOfferSecure(uint256 _listingId, uint256 _offerId) external nonReentrant {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        require(msg.sender == listing.seller, "Not the seller");
        
        Offer storage offer = listingOffers[_listingId][_offerId];
        require(offer.active, "Offer not active");
        require(block.timestamp < offer.expiresAt, "Offer expired");
        
        // SECURE: State update before external calls
        uint256 fee = (offer.amount * marketplaceFee) / 10000;
        uint256 sellerAmount = offer.amount - fee;
        
        listing.active = false;
        offer.active = false;
        
        // External calls after state update
        IERC721(listing.nftContract).transferFrom(listing.seller, offer.offeror, listing.tokenId);
        (bool success, ) = listing.seller.call{value: sellerAmount}("");
        require(success, "Payment to seller failed");
        
        emit OfferAccepted(_listingId, _offerId, offer.offeror);
    }
    
    /**
     * @dev VULNERABLE: Cancel listing with access control issue
     */
    function cancelListing(uint256 _listingId) external {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        
        // VULNERABILITY: Anyone can cancel any listing
        // Should require: msg.sender == listing.seller
        
        listing.active = false;
        
        // Refund all offers
        Offer[] storage offers = listingOffers[_listingId];
        for (uint256 i = 0; i < offers.length; i++) {
            if (offers[i].active) {
                offers[i].active = false;
                (bool success, ) = offers[i].offeror.call{value: offers[i].amount}("");
                // VULNERABILITY: Unchecked return value
            }
        }
        
        emit ListingCancelled(_listingId);
    }
    
    /**
     * @dev VULNERABLE: Withdraw offer with integer overflow
     */
    function withdrawOffer(uint256 _listingId, uint256 _offerId) external {
        Offer storage offer = listingOffers[_listingId][_offerId];
        require(offer.offeror == msg.sender, "Not the offeror");
        require(offer.active, "Offer not active");
        
        uint256 amount = offer.amount;
        
        // VULNERABILITY: Integer overflow possible
        offer.amount = 0;
        offer.active = false;
        hasOffered[_listingId][msg.sender] = false;
        
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Withdrawal failed");
        
        emit OfferWithdrawn(_offerId);
    }
    
    /**
     * @dev VULNERABLE: Update marketplace fee without proper validation
     */
    function updateMarketplaceFee(uint256 _newFee) external onlyOwner {
        // VULNERABILITY: No upper bound on fee
        // Should require: _newFee <= MAX_FEE
        marketplaceFee = _newFee;
    }
    
    /**
     * @dev VULNERABLE: Batch operations with gas limit issues
     */
    function batchCancelListings(uint256[] calldata _listingIds) external onlyOwner {
        // VULNERABILITY: Unbounded loop can cause gas limit DoS
        for (uint256 i = 0; i < _listingIds.length; i++) {
            uint256 listingId = _listingIds[i];
            Listing storage listing = listings[listingId];
            if (listing.active) {
                listing.active = false;
                // Refund logic here...
            }
        }
    }
    
    /**
     * @dev VULNERABLE: Price manipulation susceptible
     */
    function getFloorPrice(address _nftContract) external view returns (uint256) {
        uint256 lowestPrice = type(uint256).max;
        uint256 count = 0;
        
        // VULNERABILITY: No pagination, can cause gas limit issues
        for (uint256 i = 1; i <= _listingIds.current(); i++) {
            Listing storage listing = listings[i];
            if (listing.active && listing.nftContract == _nftContract) {
                if (listing.price < lowestPrice) {
                    lowestPrice = listing.price;
                }
                count++;
            }
        }
        
        return count > 0 ? lowestPrice : 0;
    }
    
    /**
     * @dev VULNERABLE: Front-running susceptible
     */
    function acceptBestOffer(uint256 _listingId) external payable {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        require(msg.value >= listing.price, "Insufficient payment");
        
        // VULNERABILITY: No minimum gas price protection
        // Can be front-run by bots
        
        // Find best offer
        uint256 bestOfferId = 0;
        uint256 bestAmount = 0;
        
        Offer[] storage offers = listingOffers[_listingId];
        for (uint256 i = 0; i < offers.length; i++) {
            if (offers[i].active && offers[i].amount > bestAmount) {
                bestAmount = offers[i].amount;
                bestOfferId = i;
            }
        }
        
        if (bestOfferId > 0) {
            // Accept best offer logic here...
        }
    }
    
    /**
     * @dev VULNERABLE: Oracle manipulation
     */
    function getNFTPrice(address _nftContract, uint256 _tokenId) external view returns (uint256) {
        // VULNERABILITY: Fixed price oracle that can be manipulated
        // Should use proper price oracle like Chainlink
        return 1000 * 10**18; // Fixed 1000 ETH
    }
    
    /**
     * @dev VULNERABLE: Slippage protection missing
     */
    function buyNow(uint256 _listingId) external payable {
        Listing storage listing = listings[_listingId];
        require(listing.active, "Listing not active");
        require(msg.value >= listing.price, "Insufficient payment");
        
        // VULNERABILITY: No slippage protection
        // User might pay much more than intended
        
        uint256 fee = (msg.value * marketplaceFee) / 10000;
        uint256 sellerAmount = msg.value - fee;
        
        // Transfer NFT and ETH
        IERC721(listing.nftContract).transferFrom(listing.seller, msg.sender, listing.tokenId);
        (bool success, ) = listing.seller.call{value: sellerAmount}("");
        require(success, "Payment to seller failed");
        
        listing.active = false;
    }
    
    /**
     * @dev Get listing details
     */
    function getListing(uint256 _listingId) external view returns (
        uint256 listingId,
        address nftContract,
        uint256 tokenId,
        address payable seller,
        uint256 price,
        bool active,
        uint256 createdAt,
        uint256 expiresAt
    ) {
        Listing storage listing = listings[_listingId];
        return (
            listing.listingId,
            listing.nftContract,
            listing.tokenId,
            listing.seller,
            listing.price,
            listing.active,
            listing.createdAt,
            listing.expiresAt
        );
    }
    
    /**
     * @dev Get offers for listing
     */
    function getListingOffers(uint256 _listingId) external view returns (Offer[] memory) {
        return listingOffers[_listingId];
    }
    
    /**
     * @dev Emergency functions
     */
    function emergencyPause() external onlyOwner {
        // VULNERABILITY: No unpause function
        // Could permanently disable the marketplace
        marketplaceFee = 10000; // 100% fee effectively pauses trading
    }
    
    function emergencyWithdraw() external onlyOwner {
        // VULNERABILITY: Can withdraw all contract funds
        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Emergency withdraw failed");
    }
}
