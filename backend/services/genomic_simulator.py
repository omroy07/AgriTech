"""
Quantum-Inspired Genomic Simulator Engine — L3-1637
===================================================
Simulates the translation of theoretical seed genotypic alleles into
real-world LiveCropPhenotypes deployed on farms. Evaluates Epigenetic drift
where real environmental stress alters gene expression dynamically.
"""

from typing import Dict, Any, List
import random
import math
import uuid
import logging
from backend.extensions import db
from backend.models.genomics import SeedGenomeProfile, LiveCropPhenotype, EpigeneticDriftLog
from backend.models.farm import Farm
from backend.models.weather import ClimateTelemetryEvent

logger = logging.getLogger(__name__)

class QuantumGenomicSimulator:
    """
    Handles probability collapses of 'superposition' trait alleles into deterministic phenotypes.
    """

    @staticmethod
    def _collapse_allele_wavefunction(base_probability: float, precision_modifier: float = 1.0) -> float:
        """
        Quantum-inspired probabilistic trait instantiation.
        E.g., A drought allele probability of 0.6 has a 60% chance to express strongly,
        but environment variables at planting (precision modifier) alter the variance.
        """
        # A mock implementation of wave-function collapse logic returning a phenotype capability scalar [0 - 1.0]
        base = max(0.01, min(0.99, base_probability))
        # Add gaussian noise around the expected mean
        collapse = random.gauss(base, 0.15 / precision_modifier)
        return max(0.0, min(1.0, collapse))
        
    @staticmethod
    def spawn_live_phenotype(genome_id: int, farm_id: int, precision_agriculture_index: float) -> LiveCropPhenotype:
        """
        Translates a seed blueprint into a live plant phenotype, collapsing probabilities.
        """
        genome = SeedGenomeProfile.query.get(genome_id)
        if not genome:
            raise ValueError(f"Genome {genome_id} not found.")

        phenotype = LiveCropPhenotype(
            farm_id=farm_id,
            genome_id=genome_id,
            expressed_drought_tolerance=QuantumGenomicSimulator._collapse_allele_wavefunction(
                genome.drought_tolerance_allele, precision_agriculture_index),
            expressed_heat_shock_resilience=QuantumGenomicSimulator._collapse_allele_wavefunction(
                genome.heat_shock_protein_expression, precision_agriculture_index),
            expressed_pest_defense=QuantumGenomicSimulator._collapse_allele_wavefunction(
                genome.pest_resistance_marker, precision_agriculture_index),
            current_health_score=1.0,
            epigenetic_stress_factor=0.0
        )
        db.session.add(phenotype)
        db.session.commit()
        
        logger.info(f"🧬 [GenomicEngine] Phenotype {phenotype.id} spawned from {genome.strain_name} on Farm {farm_id}. "
                    f"Drought Def: {phenotype.expressed_drought_tolerance:.2f}")
        return phenotype

    @staticmethod
    def process_epigenetic_drift_batch():
        """
        Scans recent extreme weather events across all active live phenotypes to apply 
        dynamic gene-suppression or activation.
        """
        phenotypes = LiveCropPhenotype.query.filter_by(status='GROWING').all()
        if not phenotypes:
            return 0
            
        farm_ids = list(set([p.farm_id for p in phenotypes]))
        
        # We find the latest extreme telemetry events for these farms in the last 24h
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        events = ClimateTelemetryEvent.query.filter(
            ClimateTelemetryEvent.farm_id.in_(farm_ids),
            ClimateTelemetryEvent.is_extreme == True,
            ClimateTelemetryEvent.recorded_at >= cutoff
        ).all()
        
        # Build event map per farm
        farm_event_map = {}
        for ev in events:
            if ev.farm_id not in farm_event_map:
                farm_event_map[ev.farm_id] = []
            farm_event_map[ev.farm_id].append(ev)

        drifts_applied = 0
            
        for pheno in phenotypes:
            farm_events = farm_event_map.get(pheno.farm_id, [])
            for ev in farm_events:
                # Calculate Epigenetic Drift based on Extreme Event Type
                d_drought = 0.0
                d_health = 0.0
                
                if ev.extreme_type == 'DROUGHT':
                    # Extended drought triggers epigenetic memory *if* the plant survives without health going < 0.2
                    if pheno.expressed_drought_tolerance > 0.5:
                        d_drought = 0.02 # Upregulation of drought resistance genes
                        d_health = -0.05
                    else:
                        d_drought = -0.10 # Complete collapse of defense mechanism
                        d_health = -0.25
                        
                elif ev.extreme_type == 'HEAT_WAVE':
                    if pheno.expressed_heat_shock_resilience < 0.4:
                        d_health = -0.20
                        
                if abs(d_drought) > 0.01 or abs(d_health) > 0.01:
                    # Apply changes
                    pheno.expressed_drought_tolerance = max(0.0, min(1.0, pheno.expressed_drought_tolerance + d_drought))
                    pheno.current_health_score = max(0.0, min(1.0, pheno.current_health_score + d_health))
                    pheno.epigenetic_stress_factor = min(1.0, pheno.epigenetic_stress_factor + abs(d_health) * 0.5)
                    
                    if pheno.current_health_score < 0.1:
                        pheno.status = 'FAILED'
                        
                    db.session.add(EpigeneticDriftLog(
                        phenotype_id=pheno.id,
                        triggering_event=f"Epigenetic Shift due to {ev.extreme_type} at {ev.temperature_c}C",
                        delta_drought_tolerance=d_drought,
                        delta_health_score=d_health
                    ))
                    drifts_applied += 1

        db.session.commit()
        return drifts_applied

    @staticmethod
    def generate_progeny_genome_cross(father_id: int, mother_id: int, new_strain_name: str) -> SeedGenomeProfile:
        """
        L3 Mendelian algorithmic cross-mating simulation picking up alleles 
        with probabilistic inheritance modifiers.
        """
        father = SeedGenomeProfile.query.get(father_id)
        mother = SeedGenomeProfile.query.get(mother_id)
        
        # Calculate new traits via weighted random mixing
        f_drought = father.drought_tolerance_allele
        m_drought = mother.drought_tolerance_allele
        drought_mix = (f_drought * 0.5) + (m_drought * 0.5) + random.uniform(-0.1, 0.1)
        
        child = SeedGenomeProfile(
            strain_name=new_strain_name,
            species=father.species, # simplified
            drought_tolerance_allele=max(0.0, min(1.0, drought_mix)),
            heat_shock_protein_expression=(father.heat_shock_protein_expression + mother.heat_shock_protein_expression)/2.0,
            pest_resistance_marker=max(father.pest_resistance_marker, mother.pest_resistance_marker) - 0.05,
            yield_vigor_multiplier=max(0.5, (father.yield_vigor_multiplier * mother.yield_vigor_multiplier)),
            generation_num=max(father.generation_num, mother.generation_num) + 1,
            is_crispr_edited=father.is_crispr_edited or mother.is_crispr_edited
        )
        db.session.add(child)
        db.session.commit()
        
        return child
