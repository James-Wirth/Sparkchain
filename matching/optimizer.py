from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value


class TradeMatcher:
    def __init__(self, offers, bids):
        self.offers = self.normalize_data(offers)
        self.bids = self.normalize_data(bids)

    def normalize_data(self, data):
        if isinstance(data[0], (tuple, list)):  # Check if input is tuple or list
            return [{"id": d[0], "energy": d[1], "price": d[2]} for d in data]
        return data

    def optimize_matching(self):
        """
        Optimizes the matching of bids and offers, aiming to match them at the best possible prices.
        :return: Dictionary of matched trades in the format:
                 {(offer_index, bid_index): trade_energy, ...}
        """
        matched_trades = {}

        # Sort offers by price (ascending), bids by price (descending)
        sorted_offers = sorted(enumerate(self.offers), key=lambda x: x[1]['price'])
        sorted_bids = sorted(enumerate(self.bids), key=lambda x: x[1]['price'], reverse=True)

        # Initialize pointers for offers and bids
        offer_idx = 0
        bid_idx = 0

        # Start matching offers and bids
        while offer_idx < len(sorted_offers) and bid_idx < len(sorted_bids):
            offer = sorted_offers[offer_idx][1]
            bid = sorted_bids[bid_idx][1]

            # Check if bid price is at least equal to offer price (can we match?)
            if bid['price'] >= offer['price'] and offer['energy'] > 0 and bid['energy'] > 0:
                # Determine the amount of energy that can be traded
                trade_energy = min(offer['energy'], bid['energy'])

                # Register the match
                matched_trades[(sorted_offers[offer_idx][0], sorted_bids[bid_idx][0])] = trade_energy

                # Update the energy of the offer and bid
                self.offers[sorted_offers[offer_idx][0]]['energy'] -= trade_energy
                self.bids[sorted_bids[bid_idx][0]]['energy'] -= trade_energy

                # If the offer is fulfilled, move to the next offer
                if self.offers[sorted_offers[offer_idx][0]]['energy'] == 0:
                    offer_idx += 1

                # If the bid is fulfilled, move to the next bid
                if self.bids[sorted_bids[bid_idx][0]]['energy'] == 0:
                    bid_idx += 1
            else:
                # If the bid price is too low for this offer, move to the next bid
                bid_idx += 1

        return matched_trades