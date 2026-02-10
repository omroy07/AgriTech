class CreditScoring:
    """
    Advanced credit risk models for default probability and payment behavior analysis.
    """
    
    @staticmethod
    def calculate_default_probability(days_overdue, payment_consistency, loan_age_months):
        """
        Logistic regression-inspired model for default probability.
        Returns probability between 0-1.
        """
        # Base risk from overdue days
        overdue_factor = min(1.0, days_overdue / 90.0) * 0.5
        
        # Consistency penalty (1 - consistency gives penalty)
        consistency_penalty = (1 - payment_consistency) * 0.3
        
        # Age factor (newer loans are riskier)
        age_factor = max(0, (12 - loan_age_months) / 12) * 0.2
        
        probability = overdue_factor + consistency_penalty + age_factor
        return round(min(1.0, probability), 4)

    @staticmethod
    def calculate_payment_consistency(total_payments, on_time_payments):
        """
        Calculates payment consistency score (0-1).
        """
        if total_payments == 0:
            return 1.0
        return round(on_time_payments / total_payments, 4)

    @staticmethod
    def calculate_risk_score(default_probability):
        """
        Converts default probability to a 0-100 risk score.
        """
        return round(default_probability * 100, 2)

    @staticmethod
    def calculate_penalty_interest(principal, days_late, annual_rate=18.0):
        """
        Calculates penalty interest for late payments.
        Penalty rate is typically 2-3% higher than base rate.
        """
        penalty_rate = annual_rate + 3.0
        daily_rate = penalty_rate / 365 / 100
        penalty = principal * daily_rate * days_late
        return round(penalty, 2)

    @staticmethod
    def calculate_late_fee(emi_amount, days_late, grace_period=3):
        """
        Flat late fee after grace period.
        Typically 2-5% of EMI amount.
        """
        if days_late <= grace_period:
            return 0.0
        fee = emi_amount * 0.02  # 2% late fee
        return round(fee, 2)
