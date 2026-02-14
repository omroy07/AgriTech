# Location: /utils/irrigation_helper.py
def calculate_evapotranspiration(temp, humidity):
    # Simplified Penman-Monteith logic for demo
    return (temp * 0.46) + (humidity * 0.05)