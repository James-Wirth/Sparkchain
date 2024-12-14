from pulp import LpMaximize, LpProblem, LpVariable, lpSum

class TradeMatcher:
    def __init__(self, offers, bids):
        self.offers = self.normalize_data(offers)
        self.bids = self.normalize_data(bids)

    def normalize_data(self, data):
        if isinstance(data[0], (tuple, list)):  # Check if input is tuple or list
            return [{"id": d[0], "energy": d[1], "price": d[2]} for d in data]
        return data

    def optimize_matching(self):
        prob = LpProblem("Maximize_Social_Welfare", LpMaximize)

        trade_vars = {}
        for i, offer in enumerate(self.offers):
            for j, bid in enumerate(self.bids):
                trade_vars[(i, j)] = LpVariable(f"trade_{i}_{j}", lowBound=0, cat="Continuous")

        prob += lpSum(
            trade_vars[(i, j)] * (bid['price'] - offer['price'])
            for i, offer in enumerate(self.offers)
            for j, bid in enumerate(self.bids)
        )

        for i, offer in enumerate(self.offers):
            prob += lpSum(trade_vars[(i, j)] for j in range(len(self.bids))) <= offer['energy'], f"OfferEnergy_{i}"
        for j, bid in enumerate(self.bids):
            prob += lpSum(trade_vars[(i, j)] for i in range(len(self.offers))) <= bid['energy'], f"BidEnergy_{j}"

        prob.solve()

        matched_trades = {
            (i, j): trade_vars[(i, j)].varValue
            for i, offer in enumerate(self.offers)
            for j, bid in enumerate(self.bids)
            if trade_vars[(i, j)].varValue > 0
        }

        offer_prices = []
        bid_prices = []
        for (i, j), trade_energy in matched_trades.items():
            offer_prices.append(self.offers[i]['price'])
            bid_prices.append(self.bids[j]['price'])

        if matched_trades:
            clearing_price = max(min(bid_prices), max(offer_prices))
        else:
            clearing_price = None

        return matched_trades
