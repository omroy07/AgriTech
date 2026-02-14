class PayrollFormulas:
    """
    Financial formulas for agricultural labor wage calculation and taxation.
    """

    @staticmethod
    def calculate_hourly_pay(hours, rate, ot_threshold=40.0, ot_multiplier=1.5):
        """
        Calculates hourly pay with overtime premiums.
        """
        if hours <= ot_threshold:
            return round(hours * rate, 2), 0.0
        
        regular_pay = ot_threshold * rate
        ot_hours = hours - ot_threshold
        ot_pay = ot_hours * rate * ot_multiplier
        
        return round(regular_pay, 2), round(ot_pay, 2)

    @staticmethod
    def calculate_piece_pay(quantity_kg, rate_per_kg):
        """
        Calculates pay based on quantity harvested.
        """
        return round(quantity_kg * rate_per_kg, 2)

    @staticmethod
    def calculate_tax(gross_pay):
        """
        Simplified tax deduction (slabs).
        """
        if gross_pay <= 5000:
            return 0.0
        if gross_pay <= 15000:
            return round(gross_pay * 0.05, 2) # 5%
        return round(gross_pay * 0.1, 2) # 10%

    @staticmethod
    def calculate_performance_bonus(quantity_kg, target_kg, bonus_per_extra_kg):
        """
        Calculates bonus if targets are exceeded.
        """
        if quantity_kg <= target_kg:
            return 0.0
        extra = quantity_kg - target_kg
        return round(extra * bonus_per_extra_kg, 2)

    @staticmethod
    def calculate_net_pay(gross, deductions):
        """
        Calculates final take-home pay.
        """
        return round(max(0, gross - deductions), 2)
