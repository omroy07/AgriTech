"""
Decentralized Biomass-to-Energy Tokenization & Grid Injection Ledger — L3-1636
==============================================================================
Orchestrates algorithmic anaerobic digestion. Mints 1MWh EnergyTokens automatically,
incorporating dynamic supply/demand pricing injected directly into the Double-Entry Ledger.
"""

from datetime import datetime, timedelta
import math
import hashlib
import uuid
import logging
from backend.extensions import db
from backend.models.biomass import BiomassStockpile, BiogasDigesterLog
from backend.models.energy_grid import DecentralizedEnergyGrid, EnergyTokenMint, GridInjectionLog
from backend.models.ledger import LedgerTransaction, LedgerAccount, LedgerEntry, AccountType, EntryType, TransactionType
from backend.models.farm import Farm

logger = logging.getLogger(__name__)

# Constants for digestion efficiency
METHANE_LHV_MJ_PER_M3 = 35.8 # Lower Heating Value
CHP_ELECTRICAL_EFFICIENCY = 0.38 # Typical CHP engine efficiency is 35-40%

class DecentralizedEnergyLedger:
    
    @staticmethod
    def _recalc_grid_feedin_tariff(grid_id: int):
        """
        Dynamically adjusts the regional energy spot price based on grid load vs supply.
        """
        grid = DecentralizedEnergyGrid.query.get(grid_id)
        if not grid:
            return
            
        base_tariff = 0.08 # Starting base $0.08 / kWh
        
        # Algorithmic pricing curve (like automated market maker for power)
        if grid.current_supply_mwh == 0 and grid.current_active_load_mwh == 0:
            grid.dynamic_feed_in_tariff_usd = base_tariff
        else:
            utilization_ratio = grid.current_active_load_mwh / max(1.0, grid.target_capacity_mwh)
            supply_ratio = grid.current_supply_mwh / max(1.0, grid.target_capacity_mwh)
            
            # If load > supply, price spikes (scarcity)
            # If supply > load, price drops (curtailment)
            scarcity_factor = utilization_ratio / max(0.01, supply_ratio)
            
            # Bound multiplier between 0.2 and 5.0 (so tariff is between $0.016 and $0.40)
            multiplier = max(0.2, min(5.0, math.sqrt(scarcity_factor)))
            new_tariff = base_tariff * multiplier
            
            grid.dynamic_feed_in_tariff_usd = round(new_tariff, 4)
            
            if new_tariff > 0.30:
                grid.status = 'BROWNOUT_RISK'
            elif new_tariff < 0.03:
                grid.status = 'CURTAILMENT'
            else:
                grid.status = 'OPERATIONAL'
                
        grid.last_rebalancing = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def log_biomass_combustion_cycle(farm_id: int, stockpile_id: int, consumed_kg: float):
        """
        Calculates theoretical energy output of digesting `consumed_kg` of a stockpile.
        """
        stockpile = BiomassStockpile.query.get(stockpile_id)
        if not stockpile or stockpile.total_mass_kg < consumed_kg:
            raise ValueError("Insufficient biomass in stockpile.")
            
        stockpile.total_mass_kg -= consumed_kg
        
        # Calculate methane yield.
        base_methane_yield_m3_kg = 0.3 # default 0.3 m3/kg for dry matter
        # Adjust for moisture: water doesn't burn
        dry_matter_fraction = max(0.0, 1.0 - (stockpile.moisture_content_pct / 100.0))
        
        methane_yield = consumed_kg * dry_matter_fraction * base_methane_yield_m3_kg
        
        # Convert Methane (m3) -> Energy (MJ) -> kWh
        energy_mj = methane_yield * METHANE_LHV_MJ_PER_M3
        thermal_kwh = energy_mj / 3.6
        
        electricity_kwh = thermal_kwh * CHP_ELECTRICAL_EFFICIENCY
        
        digester_log = BiogasDigesterLog(
            farm_id=farm_id,
            stockpile_id=stockpile_id,
            mass_consumed_kg=consumed_kg,
            digestion_temp_c=38.5, # Mesophilic default
            ph_level=7.2,
            methane_produced_m3=methane_yield,
            electricity_generated_kwh=electricity_kwh,
            status='COMPLETED',
            end_time=datetime.utcnow()
        )
        db.session.add(digester_log)
        db.session.commit()
        
        logger.info(f"🌿 [EnergyLedger] Farm {farm_id} combusted {consumed_kg}kg biomass -> {electricity_kwh:.1f} kWh")
        
        # Inject to the virtual grid
        # Assign to nearest virtual grid randomly
        grid = DecentralizedEnergyGrid.query.first()
        if not grid:
            grid = DecentralizedEnergyGrid(grid_name='Global-VPP-1', region_code='GLOBAL')
            db.session.add(grid)
            db.session.commit()
            
        DecentralizedEnergyLedger.inject_to_grid(farm_id, grid.id, digester_log.id, electricity_kwh)
        return digester_log
        
    @staticmethod
    def inject_to_grid(farm_id: int, grid_id: int, digest_id: int, kwh_vol: float):
        """
        Injects energy into a VPP, recalculates tariff spot price, and potentially mints EnergyTokens (MWh scale).
        """
        # Re-balance pricing right before evaluating
        DecentralizedEnergyLedger._recalc_grid_feedin_tariff(grid_id)
        grid = DecentralizedEnergyGrid.query.get(grid_id)
        
        # Convert kWh to MWh
        mwh = kwh_vol / 1000.0
        
        injection = GridInjectionLog(
            farm_id=farm_id,
            grid_id=grid_id,
            kwh_injected=kwh_vol,
            voltage_v=400.0, # Three-phase low voltage
            frequency_hz=50.0 # Assuming 50Hz grid
        )
        db.session.add(injection)
        
        grid.current_supply_mwh += mwh
        
        # Evaluate Minting threshold
        # We accumulate unminted MWh across recent injections not linked to a token
        # For simplicity, if this specific injection is large enough, or we just mint partial tokens.
        # We will mint a token representing the fractional MWh at the exact spot price
        
        mint_value_usd = mwh * (grid.dynamic_feed_in_tariff_usd * 1000) # $ / kWh * 1000
        
        token_hash = hashlib.sha256(f"{farm_id}-{grid_id}-{digest_id}-{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        token = EnergyTokenMint(
            farm_id=farm_id,
            grid_id=grid_id,
            digester_log_id=digest_id,
            token_hash=token_hash,
            energy_mwh=mwh,
            mint_price_usd=mint_value_usd
        )
        db.session.add(token)
        db.session.flush()

        # Wire to Financial double-entry ledger
        DecentralizedEnergyLedger._post_energy_mint_to_ledger(farm_id, token, mint_value_usd)
        
        db.session.commit()
        logger.info(f"⚡ [EnergyLedger] Tokenized {mwh:.4f} MWh for Farm {farm_id} at ${mint_value_usd:.2f} value.")

    @staticmethod
    def _post_energy_mint_to_ledger(farm_id: int, token: EnergyTokenMint, value_usd: float):
        """
        Credit Farm's energy clearing account when they inject energy.
        """
        # Load necessary accounts
        farm_acct_code = f'FARM-{farm_id}-VPP-ASSET'
        farm_acct = LedgerAccount.query.filter_by(account_code=farm_acct_code).first()
        if not farm_acct:
            farm_acct = LedgerAccount(
                account_code=farm_acct_code,
                name=f'Virtual Power Plant Escrow - Farm {farm_id}',
                account_type=AccountType.ASSET,
                entity_type='farm', entity_id=farm_id
            )
            db.session.add(farm_acct)
            
        system_energy_pool = LedgerAccount.query.filter_by(account_code='GRID-LIABILITY-POOL').first()
        if not system_energy_pool:
            system_energy_pool = LedgerAccount(
                account_code='GRID-LIABILITY-POOL',
                name='Grid Output Liability Pool',
                account_type=AccountType.LIABILITY,
                is_system=True
            )
            db.session.add(system_energy_pool)
            
        db.session.flush()

        # Build Immutable Transaction Log
        txn = LedgerTransaction(
            transaction_id=f"VPP-{uuid.uuid4().hex[:8]}",
            transaction_type=getattr(TransactionType, 'BIOMASS_ENERGY_MINT', TransactionType.FEE),  # Will patch TransactionType
            source_type='energy_token',
            source_id=token.id,
            description=f"Minted Energy Token for {token.energy_mwh:.3f} MWh @ Grid Tariff",
            base_amount=value_usd
        )
        db.session.add(txn)
        db.session.flush()

        # Double Entry: Debit Farm Asset, Credit System Liability
        db.session.add(LedgerEntry(
            transaction_id=txn.id, account_id=farm_acct.id,
            entry_type=EntryType.DEBIT, amount=value_usd, currency='USD', base_amount=value_usd,
            memo=f"Energy Token {token.token_hash[:8]} minted"
        ))
        
        db.session.add(LedgerEntry(
            transaction_id=txn.id, account_id=system_energy_pool.id,
            entry_type=EntryType.CREDIT, amount=value_usd, currency='USD', base_amount=value_usd,
            memo="System liability for injected farm energy"
        ))
        
        # Link token to txn
        token.ledger_txn_id = txn.id

        # Update global firm audit log
        from backend.models.audit_log import AuditLog
        db.session.add(AuditLog(
            action="ENERGY_TOKEN_MINT",
            resource_type="ENERGY_TOKEN",
            resource_id=str(token.id),
            risk_level="MEDIUM",
            is_financial=True,
            financial_impact=value_usd,
            ai_logistics_flag=True, # Subsumed into AI automated action flags
            details=f"Tokenized {token.energy_mwh:.2f} MWh and injected to grid."
        ))
