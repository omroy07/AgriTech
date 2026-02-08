class CarbonFormulas:
    """
    Scientific utility for calculating carbon sequestration offsets.
    Formulas based on IPCC (Intergovernmental Panel on Climate Change) standards.
    """
    
    # Coefficients: Tonnes of CO2 sequestered per acre per year
    FACTORS = {
        'No-Till': 0.52,          # conservation tillage
        'Cover Cropping': 0.65,   # planting off-season crops to protect soil
        'Reforestation': 2.40,    # planting trees on farm boundaries
        'Organic Manure': 0.35,   # shifting from chemical to organic
        'Precision Irrigation': 0.22 # energy savings + soil health
    }

    @staticmethod
    def calculate_offset(practice_type, acres, duration_days):
        """
        Calculate tonnes of CO2 offset.
        Formula: Acres * (Days / 365) * SequestrationFactor
        """
        factor = CarbonFormulas.FACTORS.get(practice_type, 0.1) # Default tiny factor if unknown
        years = duration_days / 365.0
        
        offset = acres * years * factor
        return round(offset, 4)

    @staticmethod
    def estimate_market_value(tonnes, price_per_tonne=25.0):
        """Estimate the cash value of credits in USD"""
        return round(tonnes * price_per_tonne, 2)
