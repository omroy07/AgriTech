import unittest
from backend.services.diagnostic_engine import DiagnosticEngine

class TestAIDiagnostics(unittest.TestCase):
    """
    Validates crop diagnostic engine lesion spread calculations.
    """
    
    def test_lesion_analysis_logic(self):
        # Leaf area is hardcoded to 1000.0 sq mm in service
        # spread_ratio = (lesion_count * 15.0) / 1000.0
        
        # Case 1: Minimal lesions (5)
        metadata_low = {'spectral_lesions': 5}
        spread_low = DiagnosticEngine.calculate_lesion_spread(metadata_low)
        self.assertEqual(spread_low, 0.075) # (5 * 15) / 1000 = 75 / 1000
        
        # Case 2: High infection (50 lesions)
        metadata_high = {'spectral_lesions': 50}
        spread_high = DiagnosticEngine.calculate_lesion_spread(metadata_high)
        self.assertEqual(spread_high, 0.75) # (50 * 15) / 1000
        
        # Case 3: Over saturation (100 lesions)
        metadata_max = {'spectral_lesions': 100}
        spread_max = DiagnosticEngine.calculate_lesion_spread(metadata_max)
        self.assertEqual(spread_max, 1.0, "Should cap at 1.0 (100% coverage)")

    def test_pathogen_database_lookup(self):
        """Verify that simulated pathogen database contains expected keys."""
        from backend.services.diagnostic_engine import PATHOGEN_DATABASE
        self.assertIn("RICE_BLAST", PATHOGEN_DATABASE)
        self.assertIn("BROWN_PLANTHOPPER", PATHOGEN_DATABASE)

if __name__ == '__main__':
    unittest.main()
