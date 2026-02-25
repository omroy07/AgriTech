from backend.celery_app import celery_app
from backend.models.energy_grid import DecentralizedEnergyGrid
from backend.services.energy_token_service import DecentralizedEnergyLedger
import logging
import random

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.virtual_power_plant_rebalance')
def rebalance_grid_load_and_pricing():
    """
    Runs every 15 minutes. Algorithmic Automated Market Maker (AMM) logic for the Energy Grid.
    Adjusts spot prices based on fluctuating consumer load vs farm-provided supply.
    """
    logger.info("🔌 ⚖️ [L3-1636] Rebalancing VPP Grid State & Dynamic Spot Feed-In Tariffs...")
    grids = DecentralizedEnergyGrid.query.all()
    
    for grid in grids:
        # Simulate local consumer power consumption shifting rapidly (e.g., peak evening load)
        load_fluctuation = random.uniform(-10.0, 15.0) 
        new_load = max(0.0, grid.current_active_load_mwh + load_fluctuation)
        
        # Grid continually decays over-supply as energy is consumed
        consumption = min(new_load, grid.current_supply_mwh)
        grid.current_supply_mwh = max(0.0, grid.current_supply_mwh - consumption)
        
        grid.current_active_load_mwh = new_load
        
        DecentralizedEnergyLedger._recalc_grid_feedin_tariff(grid.id)
        
    logger.info(f"✅ VPP Grids fully rebalanced and AMM tariffs recalibrated.")
    return True
