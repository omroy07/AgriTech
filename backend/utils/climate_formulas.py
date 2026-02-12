import math

class ClimateFormulas:
    """
    Advanced environmental formulas for Greenhouse management and Smart Farming.
    """

    @staticmethod
    def calculate_vpd(temp_c, relative_humidity):
        """
        Vapor Pressure Deficit (VPD) in kPa.
        Critical for understanding plant transpiration and stress.
        Formula: SVP - AVP
        """
        # Saturated Vapor Pressure (SVP) in kPa
        svp = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
        
        # Actual Vapor Pressure (AVP)
        avp = svp * (relative_humidity / 100)
        
        return round(svp - avp, 4)

    @staticmethod
    def calculate_heat_index(temp_c, relative_humidity):
        """
        Calculates Heat Index (Perceived Temperature) in Celsius.
        Uses the Rothfusz regression formula.
        """
        T = (temp_c * 9/5) + 32 # Convert to Fahrenheit
        RH = relative_humidity
        
        hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
        
        if hi > 80:
            hi = -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH - 0.00683783*T*T - 0.05481717*RH*RH + 0.00122874*T*T*RH + 0.00085282*T*RH*RH - 0.00000199*T*T*RH*RH
            
        return round((hi - 32) * 5/9, 2)

    @staticmethod
    def calculate_dli(lux, hours_per_day):
        """
        Daily Light Integral (DLI) - mol/m2/day.
        Converts Lux to PPFD (approximate for sunlight/white LED) and integrates over time.
        Approx Factor: 1 lux = 0.0185 umol/m2/s (Source dependent)
        """
        ppfd = lux * 0.0185
        dli = (ppfd * 3600 * hours_per_day) / 1_000_000
        return round(dli, 2)

    @staticmethod
    def calculate_dew_point(temp_c, relative_humidity):
        """
        Magnus formula for Dew Point.
        """
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(relative_humidity/100.0)
        return round((b * alpha) / (a - alpha), 2)

    @staticmethod
    def get_vpd_status(vpd):
        """
        Classifies VPD into growth stages.
        """
        if vpd < 0.4: return "UNDER_TRANSPIRATION"
        if 0.4 <= vpd <= 0.8: return "PROPAGATION"
        if 0.8 < vpd <= 1.2: return "VEGETATIVE"
        if 1.2 < vpd <= 1.6: return "FLOWERING"
        return "HIGH_STRESS"
