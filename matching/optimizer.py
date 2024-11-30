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
        self.offers.sort(key=lambda o: o["price"])
        self.bids.sort(key=lambda b: b["price"], reverse=True)

        prob = LpProblem("TradeOptimization", LpMaximize)

        trade_vars = {}
        for i, offer in enumerate(self.offers):
            for j, bid in enumerate(self.bids):
                trade_vars[(i, j)] = LpVariable(
                    f"Trade_{i}_{j}",
                    lowBound=0,
                    upBound=min(offer["energy"], bid["energy"])
                )

        prob += lpSum(trade_vars[(i, j)] for i in range(len(self.offers)) for j in range(len(self.bids)))
        for i, offer in enumerate(self.offers):
            prob += lpSum(trade_vars[(i, j)] for j in range(len(self.bids))) <= offer[
                "energy"], f"Supply_Constraint_{i}"

        for j, bid in enumerate(self.bids):
            prob += lpSum(trade_vars[(i, j)] for i in range(len(self.offers))) <= bid[
                "energy"], f"Demand_Constraint_{j}"

        for i, offer in enumerate(self.offers):
            for j, bid in enumerate(self.bids):
                if offer["price"] > bid["price"]:
                    prob += trade_vars[(i, j)] == 0, f"Price_Constraint_{i}_{j}"

        prob.solve()

        matched_trades = {}
        for (i, j), var in trade_vars.items():
            trade_energy = var.value()
            if trade_energy > 0:
                matched_trades[(i, j)] = trade_energy

        self.print_debug_info(prob, trade_vars)
        return matched_trades

    def print_debug_info(self, prob, trade_vars):
        print("Optimization Status:", prob.status)
        print("Objective Value (Total Traded Energy):", value(prob.objective))
        for (i, j), var in trade_vars.items():
            if var.value() > 0:
                print(f"Matched Trade: Offer {i} -> Bid {j}, Energy: {var.value()}")
