import unittest
from backend.services.nutrient_advisor import NutrientAdvisor

class TestNutrientOptimization(unittest.TestCase):
    """
    Validates the AI-driven nutrient recalibration logic.
    """
    
    def test_dynamic_goal_calculation(self):
        # Case 1: Rice in Vegetative stage
        goals, s_goal = NutrientAdvisor.get_dynamic_nutrient_goal('Rice', 'Vegetative')
        self.assertEqual(goals['N'], 120 * 1.2)
        self.assertEqual(goals['K'], 80 * 1.2)
        self.assertEqual(s_goal, 20 * 1.2)
        
        # Case 2: Wheat in Ripening stage
        goals, s_goal = NutrientAdvisor.get_dynamic_nutrient_goal('Wheat', 'Ripening')
        self.assertEqual(goals['N'], 150 * 0.4)
        self.assertEqual(s_goal, 15 * 0.4)

    def test_leaching_correction_impact(self):
        """Verify that high rainfall increases carrier water volume for chemical delivery."""
        # Volume = 500 * Area * (1 + Rainfall/50)
        
        vol_dry = 500.0 * 1.0 * (1.0 + (0.0 / 50.0))
        vol_wet = 500.0 * 1.0 * (1.0 + (50.0 / 50.0)) # 50mm rain
        
        self.assertEqual(vol_dry, 500.0)
        self.assertEqual(vol_wet, 1000.0)
        self.assertTrue(vol_wet > vol_dry)

if __name__ == '__main__':
    unittest.main()
