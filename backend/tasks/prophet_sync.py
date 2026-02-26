from backend.celery_app import celery_app
from backend.services.prophet_engine import YieldProphetEngine
from backend.services.arbitrage_service import AlgorithmicArbitrageMatrix
from backend.models.spatial_yield import SpatialYieldGrid
import logging
import random

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.prophet_global_extrapolation')
def prophet_global_extrapolation():
    """
    Runs every 6 hours. Iterates through spatial yield grids invoking the neural network
    Prophet engine to dynamically rebuild growth acceleration vectors.
    """
    logger.info("🤖 🌍 [L3-1635] Initializing Prophet Global Extrapolation Sweep...")
    grids = SpatialYieldGrid.query.all()
    
    updated = 0
    # Simulate batch data injection from orbiting constellation
    for grid in grids:
        # Minor fluctuations mimicking sat NDVI variance
        new_ndvi = max(0.1, min(1.0, (grid.normalized_difference_vegetation_index or 0.5) + random.uniform(-0.02, 0.02)))
        new_ct = max(10, min(50, (grid.canopy_temperature_c or 25.0) + random.uniform(-1.5, 1.5)))
        new_moisture = max(0, min(100, (grid.avg_soil_moisture_pct or 40.0) + random.uniform(-5, 5)))
        
        YieldProphetEngine.ingest_spatial_satellite_data(
            grid.region_id, new_ndvi, new_ct, new_moisture
        )
        updated += 1
        
    logger.info(f"✅ Extrapolated {updated} grid indices globally.")
    return {"status": "success", "grids_updated": updated}

@celery_app.task(name='tasks.arbitrage_matrix_resolution')
def arbitrage_matrix_resolution():
    """
    Runs hourly. After yield prophet rebuilds supply density estimations, 
    the arbitrage bot hunts for inefficiencies and executes trades.
    """
    logger.info("🤑 📈 [L3-1635] Resolving Global Algorithmic Arbitrage Matrix...")
    stats = AlgorithmicArbitrageMatrix.identify_arbitrage_vectors()
    logger.info(f"Arbitrage Sweep Complete: Detected: {stats.get('vectors_detected')}, Executed: {stats.get('trades_executed')}")
    return stats
