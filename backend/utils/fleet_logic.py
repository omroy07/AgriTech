class FleetLogic:
    """
    Business logic for machinery fleet management.
    Calculates usage-based billing, depreciation, and maintenance forecasting.
    """
    
    @staticmethod
    def calculate_usage_cost(base_rate, hours_used, overage_threshold=8, overage_rate=1.5):
        """
        Calculates cost based on engine hours. 
        Includes premium for exceeding 'standard' daily usage (8h).
        """
        if hours_used <= overage_threshold:
            return round(base_rate * hours_used, 2)
        
        standard_cost = base_rate * overage_threshold
        overage_hours = hours_used - overage_threshold
        overage_cost = overage_hours * base_rate * overage_rate
        
        return round(standard_cost + overage_cost, 2)

    @staticmethod
    def calculate_depreciation(purchase_price, current_hours, total_life_hours=10000):
        """
        Straight-line depreciation based on engine hours.
        """
        if current_hours >= total_life_hours:
            return 0.0
        
        hourly_depreciation = purchase_price / total_life_hours
        remaining_value = purchase_price - (hourly_depreciation * current_hours)
        return round(max(0, remaining_value), 2)

    @staticmethod
    def forecast_maintenance(current_hours, last_service_hour, interval_hours):
        """
        Returns hours remaining until next service.
        """
        next_due = last_service_hour + interval_hours
        remaining = next_due - current_hours
        return round(remaining, 1)

    @staticmethod
    def calculate_escrow_deduction(damage_estimate, security_deposit):
        """
        Determines how much to deduct from the security deposit for damage.
        """
        deduction = min(damage_estimate, security_deposit)
        remaining_refund = security_deposit - deduction
        return round(deduction, 2), round(remaining_refund, 2)
