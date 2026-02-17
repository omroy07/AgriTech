class QualityFormulas:
    """
    Scientific utility for manufacturing quality analysis.
    Calculates variance, purity, and processing loss metrics.
    """
    
    @staticmethod
    def calculate_purity_score(raw_weight, trash_weight, stone_weight):
        """
        Calculate purity percentage.
        Formula: (Raw - Internal Impurities) / Raw * 100
        """
        if raw_weight <= 0:
            return 0.0
        impurities = trash_weight + stone_weight
        purity = ((raw_weight - impurities) / raw_weight) * 100
        return round(max(0, purity), 2)

    @staticmethod
    def calculate_processing_loss(input_weight, output_weight):
        """Calculate loss percentage during a specific stage"""
        if input_weight <= 0:
            return 0.0
        loss = ((input_weight - output_weight) / input_weight) * 100
        return round(loss, 2)

    @staticmethod
    def is_moisture_acceptable(crop_type, moisture_percentage):
        """Threshold logic for safe storage/processing moisture levels"""
        THRESHOLDS = {
            'Wheat': 13.5,
            'Rice': 14.0,
            'Coffee': 12.0,
            'Corn': 15.5
        }
        max_allowed = THRESHOLDS.get(crop_type, 14.0)
        return moisture_percentage <= max_allowed

    @staticmethod
    def calculate_quality_grade(purity, moisture, color_score=10):
        """Heuristic for assigning a grade based on multiple parameters"""
        if purity > 98 and moisture < 12:
            return "Grade A+"
        elif purity > 95 and moisture < 14:
            return "Grade A"
        elif purity > 90:
            return "Grade B"
        return "Standard"
