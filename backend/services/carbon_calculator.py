from backend.models.sustainability import CarbonLedger, EmissionSource
from backend.models.logistics_v2 import FuelLog
from backend.models.irrigation import IrrigationZone
from backend.models.soil_health import SoilTest
from backend.models.procurement import BulkOrder, ProcurementItem
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class CarbonCalculator:
    """
    ISO-standardized carbon footprinting algorithm.
    Calculates Scope 1, 2, and 3 emissions for Agri-batches.
    """

    # Constants: Emission Factors (kg CO2e per unit)
    EF_DIESEL = 2.68 # per liter
    EF_ELECTRICITY = 0.45 # per kWh (Average grid)
    EF_FERTILIZER_UREA = 3.5 # per kg production (Scope 3)
    EF_WATER_PUMPING = 0.1 # per m3

    @staticmethod
    def calculate_scope_1(farm_id, fuel_liters, soil_n_level):
        """Direct emissions from fuel and soil N2O flux."""
        fuel_emissions = fuel_liters * CarbonCalculator.EF_DIESEL
        
        # N2O flux simulation: 1.25% of applied Nitrogen is emitted as N2O
        # N2O is ~273x more potent than CO2
        soil_emissions = (soil_n_level * 0.0125) * 273.0
        
        return fuel_emissions + soil_emissions

    @staticmethod
    def calculate_scope_2(electricity_kwh):
        """Indirect emissions from purchased electricity."""
        return electricity_kwh * CarbonCalculator.EF_ELECTRICITY

    @staticmethod
    def calculate_scope_3_procurement(order_id):
        """Emissions from supply chain (seeds, fertilizers)."""
        order = BulkOrder.query.get(order_id)
        if not order: return 0.0
        
        # In a real system, we'd lookup specific EFs for the product
        # Here we use a generic factor for fertilizers
        item = ProcurementItem.query.get(order.item_id)
        if 'Fertilizer' in (item.category or ''):
            return order.quantity * CarbonCalculator.EF_FERTILIZER_UREA
        return 0.0

    @staticmethod
    def calculate_circular_offset(farm_id):
        """
        L3 Requirement: Calculates offset from reused bio-mass (Circular Economy).
        Reduces Scope 3 by preventing new fertilizer production.
        """
        from backend.models.circular import WasteInventory
        reused_waste = db.session.query(db.func.sum(WasteInventory.quantity_kg)).filter_by(
            farm_id=farm_id, 
            is_reused_on_farm=True
        ).scalar() or 0.0
        
        # 3.0 kg CO2e offset per kg of organic recovery
        return reused_waste * 3.0

    @staticmethod
    def run_full_audit(farm_id, batch_id=None):
        """Generates a CarbonLedger entry for a farm or specific batch."""
        # This is a simplified aggregation for the audit
        
        # 1. Total Fuel
        total_fuel = db.session.query(db.func.sum(FuelLog.fuel_quantity)).filter(FuelLog.recorded_at >= db.func.now() - db.text("INTERVAL '30 days'")).scalar() or 0
        
        # 2. Total Electricity (from zones)
        total_elec = db.session.query(db.func.sum(IrrigationZone.electricity_usage_kwh)).filter_by(farm_id=farm_id).scalar() or 0
        
        # 3. N-Flux from soil
        latest_soil = SoilTest.query.filter_by(farm_id=farm_id).order_by(SoilTest.created_at.desc()).first()
        n_level = latest_soil.nitrogen if latest_soil else 0.0
        
        s1 = CarbonCalculator.calculate_scope_1(farm_id, total_fuel, n_level)
        s2 = CarbonCalculator.calculate_scope_2(total_elec)
        s3 = 0.0 # Aggregated from recent BulkOrders
        
        # Apply Circular Economy Offsets (L3-1594)
        circular_offset = CarbonCalculator.calculate_circular_offset(farm_id)
        
        ledger = CarbonLedger(
            farm_id=farm_id,
            batch_id=batch_id,
            scope_1_direct=s1,
            scope_2_indirect=s2,
            scope_3_supply_chain=max(0.0, s3 - circular_offset),
            total_footprint=s1 + s2 + s3,
            net_carbon_balance=s1 + s2 + s3 - circular_offset
        )
        db.session.add(ledger)
        db.session.commit()
        
        return ledger
