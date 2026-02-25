"""
Pathogen Virulence Combat Engine — L3-1637
==========================================
Deterministic battle engine calculating Infection capabilities vs Phenotypic Resistance.
If Pathogen succeeds, it mutates. If Crop succeeds, the pathogen generation dies out.
"""

from typing import Dict, Any, List
import random
import uuid
import logging
from backend.extensions import db
from backend.models.genomics import LiveCropPhenotype
from backend.models.virulence import PathogenStrain, InfectionCombatSimulation
from backend.models.farm import Farm

logger = logging.getLogger(__name__)

class VirulenceEngine:
    
    @staticmethod
    def _calculate_attack_power(strain: PathogenStrain, phenotype: LiveCropPhenotype) -> float:
        """Derives a single deterministic attack scaler bridging multiple vulnerability axes."""
        # Base infectivity
        atk = strain.infectivity_rate * 10.0 
        
        # If crop is drought tolerant and Strain possesses the exploit allele, attack scales heavily
        if phenotype.expressed_drought_tolerance > 0.6 and strain.anti_drought_gene_exploit > 0.0:
            atk += (phenotype.expressed_drought_tolerance * strain.anti_drought_gene_exploit * 5.0)
            
        return max(0.0, atk)
        
    @staticmethod
    def _calculate_defense_power(phenotype: LiveCropPhenotype, strain_bypass_cap: float) -> float:
        """Derives the phenotypic wall the pathogen must break through."""
        # Natural pest defense modified by bypass
        eff_defense = max(0.0, phenotype.expressed_pest_defense - strain_bypass_cap)
        
        # Multiply by overall health (sick plants are easier to infect)
        defense = eff_defense * phenotype.current_health_score * 12.0
        return defense

    @staticmethod
    def execute_infection_simulation(strain_id: int, phenotype_id: int) -> InfectionCombatSimulation:
        """
        Pits a pathogen against a living crop profile.
        Returns the combat outcome which updates the db objects accordingly.
        """
        strain = PathogenStrain.query.get(strain_id)
        pheno = LiveCropPhenotype.query.get(phenotype_id)
        
        if not strain or not pheno:
            raise ValueError("Entities not found for simulation context.")
            
        atk_pwr = VirulenceEngine._calculate_attack_power(strain, pheno)
        def_pwr = VirulenceEngine._calculate_defense_power(pheno, strain.defense_bypass_capability)
        
        # Weather noise (+- 20%)
        env_modifier = random.uniform(0.8, 1.2)
        final_atk = atk_pwr * env_modifier
        
        infection_success = (final_atk > def_pwr)
        
        dmg_pct = 0.0
        mutated = False
        
        if infection_success:
            # Plant loses health based on severity of overwrite
            overkill_ratio = (final_atk / max(0.1, def_pwr))
            dmg_pct = min(1.0, 0.1 * overkill_ratio)
            pheno.current_health_score = max(0.0, pheno.current_health_score - dmg_pct)
            
            if pheno.current_health_score < 0.1:
                pheno.status = 'FAILED'
                
            # Pathogen Mutation Check (15% chance to mutate on success)
            if random.uniform(0, 1.0) < 0.15:
                mutated = True
                VirulenceEngine._spawn_mutated_strain(strain)
        else:
            # Crop repelled it, strain becomes extinct if it hits enough walls
            if random.uniform(0, 1.0) < 0.05:
                strain.extinct_marker = True
                
        combat_log = InfectionCombatSimulation(
            strain_id=strain.id,
            phenotype_id=pheno.id,
            base_attack_power=final_atk,
            crop_defense_power=def_pwr,
            environmental_modifier=env_modifier,
            infection_success=infection_success,
            damage_inflicted_pct=dmg_pct,
            triggered_new_mutation=mutated
        )
        db.session.add(combat_log)
        db.session.commit()
        
        logger.info(f"🦠 [VirulenceEngine] Combat {strain.strain_designation} vs Phenotype {pheno.id} -> "
                    f"Success: {infection_success}, Dmg: {dmg_pct*100:.1f}%, Mutated: {mutated}")
                    
        return combat_log

    @staticmethod
    def _spawn_mutated_strain(parent: PathogenStrain):
        """Generates the next generation of pathogen with slightly raised virulence capability."""
        child = PathogenStrain(
            disease_id=parent.disease_id,
            strain_designation=f"{parent.strain_designation}-MUT-{uuid.uuid4().hex[:4]}",
            infectivity_rate=min(1.0, parent.infectivity_rate + random.uniform(-0.02, 0.08)),
            spore_dispersal_radius_km=parent.spore_dispersal_radius_km * random.uniform(0.9, 1.15),
            defense_bypass_capability=min(1.0, parent.defense_bypass_capability + 0.05),
            anti_drought_gene_exploit=min(1.0, parent.anti_drought_gene_exploit + 0.10 if parent.anti_drought_gene_exploit > 0 else 0.02),
            mutation_generation=parent.mutation_generation + 1
        )
        db.session.add(child)
        # Parent continues, child becomes distinct lineage
        return child
        
    @staticmethod
    def simulate_global_battles(num_engagements: int = 20):
        """Scans global pathogen strains and active phenotypes to run interactions continuously."""
        strains = PathogenStrain.query.filter_by(extinct_marker=False).all()
        phenos = LiveCropPhenotype.query.filter_by(status='GROWING').all()
        
        if not strains or not phenos:
            return {'status': 'No active combatants found'}
            
        logs = []
        for _ in range(num_engagements):
            s = random.choice(strains)
            p = random.choice(phenos)
            res = VirulenceEngine.execute_infection_simulation(s.id, p.id)
            logs.append(res.id)
            
        return {'engagements_fired': len(logs)}
