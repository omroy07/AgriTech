class NutrientFormulas:
    """
    Scientific formulas for soil health analysis and fertilizer recommendations.
    """
    
    @staticmethod
    def calculate_nutrient_gap(current, target):
        """Calculates the gap between current soil nutrients and target levels for a crop."""
        gap = max(0, target - current)
        return round(gap, 2)

    @staticmethod
    def calculate_fertilizer_amount(nutrient_need_kg_ha, nutrient_percentage):
        """Calculates the amount of a specific fertilizer needed based on nutrient content."""
        if nutrient_percentage <= 0:
            return 0
        amount = (nutrient_need_kg_ha / (nutrient_percentage / 100))
        return round(amount, 2)

    @staticmethod
    def calculate_lime_requirement(current_ph, target_ph=6.5):
        """
        Estimates lime required (tons/hectare) to raise soil pH.
        Highly simplified: 1.5 tons per 0.5 pH increase.
        """
        if current_ph >= target_ph:
            return 0.0
        gap = target_ph - current_ph
        # Constant for medium textured soil
        lime_needed = (gap / 0.5) * 1.5
        return round(lime_needed, 2)

    @staticmethod
    def get_crop_targets(crop_type):
        """Returns standard N-P-K targets (mg/kg) for various crops."""
        TARGETS = {
            'Wheat': {'N': 150, 'P': 40, 'K': 120},
            'Rice': {'N': 120, 'P': 30, 'K': 100},
            'Coffee': {'N': 200, 'P': 60, 'K': 180},
            'Corn': {'N': 180, 'P': 50, 'K': 150}
        }
        return TARGETS.get(crop_type, {'N': 100, 'P': 25, 'K': 80})
