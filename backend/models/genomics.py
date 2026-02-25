"""
Quantum-Inspired Genomic Trait Propagation Models
=================================================
Models the genetic makeup of seeds and live crops, simulating how traits 
(drought resistance, pest resilience, yield multiplier) are expressed 
probabilistically across generations under environmental stress.
"""

from datetime import datetime
import json
from backend.extensions import db

class SeedGenomeProfile(db.Model):
    """
    Base genetic blueprint of a newly minted seed batch.
    Stores traits as quantum superpositions (probabilities of expression).
    """
    __tablename__ = 'seed_genome_profiles'

    id = db.Column(db.Integer, primary_key=True)
    strain_name = db.Column(db.String(150), nullable=False)
    species = db.Column(db.String(50), nullable=False) # RICE, WHEAT, SOYBEAN
    
    # Genetic Traits encoded as expression probabilities (0.0 to 1.0)
    drought_tolerance_allele = db.Column(db.Float, default=0.5)
    heat_shock_protein_expression = db.Column(db.Float, default=0.5)
    pest_resistance_marker = db.Column(db.Float, default=0.5)
    yield_vigor_multiplier = db.Column(db.Float, default=1.0)
    
    # Genomic Origin
    is_crispr_edited = db.Column(db.Boolean, default=False)
    original_wild_type_id = db.Column(db.Integer, db.ForeignKey('seed_genome_profiles.id'), nullable=True)
    
    generation_num = db.Column(db.Integer, default=1)
    
    # Meta
    lab_certification_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'strain': self.strain_name,
            'species': self.species,
            'drought_allele': self.drought_tolerance_allele,
            'heat_shock_marker': self.heat_shock_protein_expression,
            'pest_resistance': self.pest_resistance_marker,
            'yield_vigor': self.yield_vigor_multiplier,
            'generation': self.generation_num,
            'is_gmo': self.is_crispr_edited
        }


class LiveCropPhenotype(db.Model):
    """
    Instantiated expression of a Genome Profile actively growing on a Farm.
    Subject to epigenetic drift driven by real-world weather.
    """
    __tablename__ = 'live_crop_phenotypes'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    genome_id = db.Column(db.Integer, db.ForeignKey('seed_genome_profiles.id'), nullable=False)
    
    # Realized Trait Expression (Drifts from base allele probability based on environment)
    expressed_drought_tolerance = db.Column(db.Float, nullable=False)
    expressed_heat_shock_resilience = db.Column(db.Float, nullable=False)
    expressed_pest_defense = db.Column(db.Float, nullable=False)
    
    # Epigenetic Wear (0.0 = perfect health, 1.0 = genetic breakdown & senescence)
    epigenetic_stress_factor = db.Column(db.Float, default=0.0)
    
    # Overall Plant Vigor
    current_health_score = db.Column(db.Float, default=1.0) # 0 to 1
    
    planted_at = db.Column(db.DateTime, default=datetime.utcnow)
    harvested_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='GROWING') # GROWING, HARVESTED, FAILED
    
    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'genome_id': self.genome_id,
            'expressed_drought_tol': self.expressed_drought_tolerance,
            'expressed_heat_resilience': self.expressed_heat_shock_resilience,
            'expressed_pest_defense': self.expressed_pest_defense,
            'stress_factor': self.epigenetic_stress_factor,
            'health_score': self.current_health_score,
            'status': self.status
        }

class EpigeneticDriftLog(db.Model):
    """
    High-frequency log showing how environmental factors (telemetry) 
    activate or suppress gene expression dynamically over the crop's lifecycle.
    """
    __tablename__ = 'epigenetic_drift_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    phenotype_id = db.Column(db.Integer, db.ForeignKey('live_crop_phenotypes.id'), nullable=False)
    
    triggering_event = db.Column(db.String(100)) # e.g., "Heatwave > 42C"
    
    # The Delta applied to the phenotype's expressed genome
    delta_drought_tolerance = db.Column(db.Float, default=0.0)
    delta_stress_factor = db.Column(db.Float, default=0.0)
    delta_health_score = db.Column(db.Float, default=0.0)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
