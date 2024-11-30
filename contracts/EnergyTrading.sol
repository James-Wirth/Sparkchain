// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SPARKToken.sol";

contract EnergyTrading {
    SPARKToken public sparkToken;

    struct Offer {
        address generator;
        uint256 energy;
        uint256 price;
        bool fulfilled;
    }

    struct Bid {
        address supplier;
        uint256 energy;
        uint256 price;
        bool fulfilled;
    }

    struct Trade {
        address generator;
        address supplier;
        uint256 energy;
        uint256 price;
    }

    Offer[] public offers;
    Bid[] public bids;
    Trade[] public trades;

    uint256 public totalEnergyReserve;
    uint256 public totalSPARKReserve;

    mapping(address => uint256) public balances;

    event OfferSubmitted(address indexed generator, uint256 energy, uint256 price);
    event BidSubmitted(address indexed supplier, uint256 energy, uint256 price);
    event TradeExecuted(address indexed generator, address indexed supplier, uint256 energy, uint256 price);
    event LiquidityAdded(address indexed provider, uint256 energy, uint256 spark);
    event LiquidityRemoved(address indexed provider, uint256 energy, uint256 spark);

    constructor(SPARKToken _sparkToken) {
        sparkToken = _sparkToken;
    }

    function addLiquidity(uint256 energy, uint256 spark) external {
        emit LiquidityDebug("Before Transfer", totalEnergyReserve, totalSPARKReserve);
        require(sparkToken.transferFrom(msg.sender, address(this), spark), "SPARK transfer failed");
        totalEnergyReserve += energy;
        totalSPARKReserve += spark;
        emit LiquidityDebug("After Update", totalEnergyReserve, totalSPARKReserve);
        emit LiquidityAdded(msg.sender, energy, spark);
    }
    event LiquidityDebug(string stage, uint256 energyReserve, uint256 sparkReserve);


    function getEnergyPrice() public view returns (uint256) {
        require(totalEnergyReserve > 0, "No energy in reserve");
        return totalSPARKReserve / totalEnergyReserve;
    }

    function submitOffer(uint256 energy, uint256 price) external {
        offers.push(Offer(msg.sender, energy, price, false));
        emit OfferSubmitted(msg.sender, energy, price);
    }

    function submitBid(uint256 energy, uint256 price) external {
        bids.push(Bid(msg.sender, energy, price, false));
        emit BidSubmitted(msg.sender, energy, price);
    }

    function executeTrade(uint256 offerIndex, uint256 bidIndex, uint256 tradeEnergy) external {
        Offer storage offer = offers[offerIndex];
        Bid storage bid = bids[bidIndex];

        require(!offer.fulfilled, "Offer already fulfilled");
        require(!bid.fulfilled, "Bid already fulfilled");
        require(tradeEnergy <= offer.energy, "Trade exceeds offer energy");
        require(tradeEnergy <= bid.energy, "Trade exceeds bid energy");
        require(bid.price >= offer.price, "Bid price is too low");

        uint256 totalPrice = tradeEnergy * offer.price;
        uint256 energyPrice = getEnergyPrice();
        // require(totalPrice <= energyPrice * tradeEnergy, "Trade price exceeds AMM price");

        offer.energy -= tradeEnergy;
        bid.energy -= tradeEnergy;

        if (offer.energy == 0) offer.fulfilled = true;
        if (bid.energy == 0) bid.fulfilled = true;

        require(sparkToken.transferFrom(bid.supplier, offer.generator, totalPrice), "SPARK transfer failed");

        trades.push(Trade(offer.generator, bid.supplier, tradeEnergy, offer.price));
        emit TradeExecuted(offer.generator, bid.supplier, tradeEnergy, offer.price);
    }

    function getOffers() public view returns (Offer[] memory) {
        return offers;
    }

    function getBids() public view returns (Bid[] memory) {
        return bids;
    }

    function getTrades() public view returns (Trade[] memory) {
        return trades;
    }
}
