import unittest
import math
import random
import os
import sys

# Attempt dynamic path loading for local testing bounds
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.services.virulence_engine import VirulenceEngine
    from backend.models.genomics import LiveCropPhenotype
    from backend.models.virulence import PathogenStrain, InfectionCombatSimulation
except ImportError:
    pass

class TestVirulenceEngine(unittest.TestCase):
    """
    Test suite for the deterministic pathogen combat engine.
    Ensures math calculating attack and defense scales logarithmically and correctly.
    """
    
    def test_base_attack_power_math(self):
        """Test the equation driving pathogen infection rates without database latency."""
        # Create mock structs
        class MockStrain:
            infectivity_rate = 0.5
            anti_drought_gene_exploit = 0.0
            
        class MockPheno:
            expressed_drought_tolerance = 0.5
            
        strain = MockStrain()
        pheno = MockPheno()
        
        # Base calculation = 0.5 * 10 = 5.0
        pwr = VirulenceEngine._calculate_attack_power(strain, pheno)
        self.assertEqual(pwr, 5.0, "Base power should strictly follow the scalar multiplier.")
        
    def test_exploit_attack_power_multiplier(self):
        """Pathogens that have adapted to exploit a certain crop trait should gain a massive multiplier."""
        class MockStrain:
            infectivity_rate = 0.5
            anti_drought_gene_exploit = 0.8
            
        class MockPheno:
            expressed_drought_tolerance = 0.9 # High defense that is being exploited
            
        strain = MockStrain()
        pheno = MockPheno()
        
        pwr = VirulenceEngine._calculate_attack_power(strain, pheno)
        # Expected: 5.0 + (0.9 * 0.8 * 5.0) = 5.0 + 3.6 = 8.6
        self.assertAlmostEqual(pwr, 8.6, places=1)
        
    def test_defense_power_matrix(self):
        """Ensure Phenotypic health and genetic traits interlink successfully to generate defense."""
        class MockPheno:
            expressed_pest_defense = 0.9
            current_health_score = 1.0 # Perfect Health
            
        pheno = MockPheno()
        bypass = 0.2
        
        pwr = VirulenceEngine._calculate_defense_power(pheno, bypass)
        # Expected: max(0, 0.9 - 0.2) * 1.0 * 12.0 = 0.7 * 12.0 = 8.4
        self.assertAlmostEqual(pwr, 8.4, places=1)
        
        # Test Sick Plant Modifiers
        pheno.current_health_score = 0.1 # Very Sick
        pwr_sick = VirulenceEngine._calculate_defense_power(pheno, bypass)
        # Expected: 0.7 * 0.1 * 12.0 = 0.84 
        self.assertAlmostEqual(pwr_sick, 0.84, places=2)
        
        self.assertTrue(pwr_sick < pwr, "Sick plants must generate fundamentally lower defensive integers.")

if __name__ == '__main__':
    unittest.main()
