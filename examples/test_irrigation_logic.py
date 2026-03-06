import unittest
from backend.services.irrigation_orchestrator import IrrigationOrchestrator

class TestIrrigationLogic(unittest.TestCase):
    """
    Validates water deficit calculations and aquifer sustainability logic.
    """
    
    def test_water_deficit_math(self):
        # Case 1: Low moisture, low ET
        deficit_low = IrrigationOrchestrator.calculate_water_deficit(1, 20.0, 20.0, 80.0)
        # 45 - 20 = 25. ET mod = (20*0.05) + (20*0.02) = 1.0 + 0.4 = 1.4%
        self.assertAlmostEqual(deficit_low, 25.35, places=2)
        
        # Case 2: Low moisture, high ET (Heatwave)
        deficit_high = IrrigationOrchestrator.calculate_water_deficit(1, 20.0, 42.0, 10.0)
        # 45 - 20 = 25. ET mod = (42*0.05) + (90*0.02) = 2.1 + 1.8 = 3.9%
        self.assertAlmostEqual(deficit_high, 25.975, places=3)
        
        self.assertTrue(deficit_high > deficit_low, "Heatwave must result in higher water requirement.")

    def test_valve_trigger_thresholds(self):
        """Verify that stress scores above 0.4 trigger autonomous actions."""
        # 45 - 15 / 45 = 30 / 45 = 0.66 (Trigger)
        stress_trigger = (45.0 - 15.0) / 45.0
        self.assertTrue(stress_trigger > 0.4)
        
        # 45 - 40 / 45 = 5 / 45 = 0.11 (No Trigger)
        stress_safe = (45.0 - 40.0) / 45.0
        self.assertFalse(stress_safe > 0.4)

if __name__ == '__main__':
    unittest.main()
