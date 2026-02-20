from backend.models.circular import WasteInventory, BioEnergyOutput, CircularCredit
from backend.models.sustainability import CarbonLedger, SustainabilityScore
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class TransformerLogic:
    """
    Logic for transforming bio-mass waste into energy and credits.
    Implements the circular economy "Waste-to-Credit" chain of custody.
    """

    # Efficiency Constants (kWh per kg)
    EFFICIENCY_MAP = {
        'Organic Bio-Mass': 1.2,
        'Crop Residue': 0.8,
        'Animal Waste': 1.5
    }

    @staticmethod
    def transform_waste_to_energy(waste_id, energy_type='ELECTRICITY'):
        """
        Processes a waste batch into energy.
        """
        waste = WasteInventory.query.get(waste_id)
        if not waste or waste.status != 'PENDING_TRANSFORMATION':
            return None

        # 1. Calculate energy output
        base_efficiency = TransformerLogic.EFFICIENCY_MAP.get(waste.waste_type, 1.0)
        energy_amount = waste.quantity_kg * base_efficiency
        
        # 2. Calculate carbon offset (Simulated fossil fuel reduction)
        # Average CO2 offset: 0.5kg per kWh
        carbon_offset = energy_amount * 0.5
        
        # 3. Create Energy Output Record
        output = BioEnergyOutput(
            farm_id=waste.farm_id,
            waste_id=waste.id,
            energy_type=energy_type,
            amount_kwh=energy_amount,
            efficiency_ratio=base_efficiency,
            carbon_offset_kg=carbon_offset
        )
        db.session.add(output)

        # 4. Update Waste Status
        waste.status = 'TRANSFORMED'
        
        # 5. Issue Circular Credits (1 credit per 10kg waste transformed)
        credits_earned = waste.quantity_kg / 10.0
        credit = CircularCredit(
            user_id=1, # Default or linked to farm owner
            farm_id=waste.farm_id,
            credit_amount=credits_earned,
            source_type='ENERGY_GENERATION'
        )
        db.session.add(credit)

        # 6. Update Sustainability Score Bonus
        score = SustainabilityScore.query.filter_by(farm_id=waste.farm_id).first()
        if score:
            score.circular_economy_bonus += (credits_earned * 0.1) # Weighted bonus
        
        db.session.commit()
        return output

    @staticmethod
    def apply_recursive_nutrient_recovery(waste_id):
        """
        L3 Requirement: Reusing waste on farm reduces Scope 3 footprint.
        If organic waste is returned to the soil, it offsets fertilizer production emissions.
        """
        waste = WasteInventory.query.get(waste_id)
        if not waste or waste.is_reused_on_farm:
            return False

        # Mark as reused
        waste.is_reused_on_farm = True
        waste.status = 'UTILIZED_ON_FARM'

        # Update Carbon Ledger (Reduce Scope 3)
        ledger = CarbonLedger.query.filter_by(farm_id=waste.farm_id).order_by(CarbonLedger.recorded_at.desc()).first()
        if ledger:
            # Fertilizer offset: 3kg CO2e per kg organic waste reused
            offset_amount = waste.quantity_kg * 3.0
            ledger.scope_3_supply_chain = max(0.0, ledger.scope_3_supply_chain - offset_amount)
            ledger.net_carbon_balance -= offset_amount
            
            # Grant credits for nutrient recovery
            credit = CircularCredit(
                user_id=1,
                farm_id=waste.farm_id,
                credit_amount=waste.quantity_kg / 5.0, # Higher reward for soil health
                source_type='NUTRIENT_RECOVERY'
            )
            db.session.add(credit)

        db.session.commit()
        return True
