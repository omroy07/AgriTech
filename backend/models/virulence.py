"""
Pathogen Virulence Evolution Models
===================================
Simulates the mutational landscape of agricultural diseases (fungi, bacteria, pests).
Virulence strains adapt algorithmically to overcome Crop Phenotypic defenses.
"""

from datetime import datetime
from backend.extensions import db

class PathogenStrain(db.Model):
    """
    A specific genetic lineage of an outbreak zone's disease.
    """
    __tablename__ = 'pathogen_strains'
    
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease_incidents.id'), nullable=False)
    
    strain_designation = db.Column(db.String(100), unique=True, nullable=False) # e.g. "Puccinia-Gamma-09"
    
    # Pathogenic Capabilities (0.0 to 1.0)
    infectivity_rate = db.Column(db.Float, default=0.5) 
    spore_dispersal_radius_km = db.Column(db.Float, default=50.0)
    pesticide_resistance_factor = db.Column(db.Float, default=0.1)
    
    # Virulence Matrix: How effectively it pierces crop defenses
    anti_drought_gene_exploit = db.Column(db.Float, default=0.0) # Bonus infectivity on drought-resistant crops
    defense_bypass_capability = db.Column(db.Float, default=0.2)
    
    mutation_generation = db.Column(db.Integer, default=1)
    
    first_detected = db.Column(db.DateTime, default=datetime.utcnow)
    extinct_marker = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'strain': self.strain_designation,
            'infectivity': self.infectivity_rate,
            'spore_radius': self.spore_dispersal_radius_km,
            'generation': self.mutation_generation,
            'active': not self.extinct_marker
        }

class InfectionCombatSimulation(db.Model):
    """
    L3 Simulator Result: A deterministic battle between a PathogenStrain and a LiveCropPhenotype.
    """
    __tablename__ = 'infection_combat_simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    strain_id = db.Column(db.Integer, db.ForeignKey('pathogen_strains.id'), nullable=False)
    phenotype_id = db.Column(db.Integer, db.ForeignKey('live_crop_phenotypes.id'), nullable=False)
    
    # Simulation Math
    base_attack_power = db.Column(db.Float, nullable=False)
    crop_defense_power = db.Column(db.Float, nullable=False)
    environmental_modifier = db.Column(db.Float, default=1.0)
    
    # Outcome
    infection_success = db.Column(db.Boolean, nullable=False)
    damage_inflicted_pct = db.Column(db.Float, default=0.0) # If successful, how much health lost
    
    # Spontaneous Mutation Triggered?
    triggered_new_mutation = db.Column(db.Boolean, default=False)
    
    simulated_at = db.Column(db.DateTime, default=datetime.utcnow)
