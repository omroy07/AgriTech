import math

class StockFormulas:
    """
    Scientific formulas for inventory management and supply chain optimization.
    """
    
    @staticmethod
    def calculate_eoq(annual_demand, ordering_cost, holding_cost_per_unit):
        """
        Economic Order Quantity (EOQ) - optimal order quantity to minimize total inventory costs.
        Formula: sqrt((2 * D * S) / H)
        D = Annual demand, S = Ordering cost per order, H = Holding cost per unit per year
        """
        if holding_cost_per_unit <= 0:
            return 0
        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
        return round(eoq, 2)

    @staticmethod
    def calculate_reorder_point(daily_demand, lead_time_days, safety_stock=0):
        """
        Reorder Point - stock level at which a new order should be placed.
        Formula: (Daily Demand * Lead Time) + Safety Stock
        """
        rop = (daily_demand * lead_time_days) + safety_stock
        return round(rop, 2)

    @staticmethod
    def calculate_turnover_ratio(cost_of_goods_sold, average_inventory):
        """
        Inventory Turnover Ratio - how many times inventory is sold/replaced in a period.
        Higher ratio indicates efficient inventory management.
        """
        if average_inventory <= 0:
            return 0
        return round(cost_of_goods_sold / average_inventory, 2)

    @staticmethod
    def calculate_shrinkage_percentage(book_inventory, physical_inventory):
        """
        Shrinkage % - percentage of inventory lost due to theft, damage, or errors.
        Formula: ((Book - Physical) / Book) * 100
        """
        if book_inventory <= 0:
            return 0
        shrinkage = ((book_inventory - physical_inventory) / book_inventory) * 100
        return round(max(0, shrinkage), 2)

    @staticmethod
    def calculate_days_to_expiry(expiry_date, current_date):
        """
        Calculates days remaining until stock expiry.
        """
        delta = (expiry_date - current_date).days
        return max(0, delta)

    @staticmethod
    def calculate_holding_cost(quantity, unit_cost, holding_rate=0.20):
        """
        Annual holding cost for inventory.
        Holding rate typically 15-25% of unit cost per year.
        """
        cost = quantity * unit_cost * holding_rate
        return round(cost, 2)
