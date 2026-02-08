import random
from datetime import datetime

class IoTSimulator:
    """
    Simulates high-frequency IoT sensor telemetry with realistic data jitter.
    Used for moisture, temperature, and pH level emulation.
    """
    
    @staticmethod
    def generate_sensor_data(zone_id, prev_moisture=45.0):
        """
        Generates a new set of sensor readings based on previous state 
        to simulate cohesive environmental changes.
        """
        # Moisture fluctuates slow (unless irrigation is on)
        # Random jitter +/- 1%
        moisture_delta = random.uniform(-1.0, 1.0)
        new_moisture = max(0, min(100, prev_moisture + moisture_delta))
        
        # Temperature usually between 20-35 C
        temperature = random.uniform(22.0, 32.0)
        
        # pH Level between 6.0 and 7.5
        ph = random.uniform(6.3, 7.2)
        
        return {
            'zone_id': zone_id,
            'moisture': round(new_moisture, 2),
            'temperature': round(temperature, 2),
            'ph_level': round(ph, 2),
            'timestamp': datetime.utcnow()
        }

    @staticmethod
    def simulate_irrigation_effect(current_moisture, flow_rate=2.5):
        """Simulate moisture rising while valve is OPEN"""
        return max(0, min(100, current_moisture + flow_rate))
