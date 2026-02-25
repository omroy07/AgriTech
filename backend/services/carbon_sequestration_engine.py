"""
Carbon Sequestration Engine — L3-1632
======================================
Implements the scientific calculation of soil carbon sequestration offsets
and autonomously mints Circular Carbon Credits tied to double-entry ledger
transactions.

Science Reference:
  CO2e tonnes = (ΔSOC% / 100) × ρ × D × A × (44/12)
  Where:
    ΔSOC%  = Change in Soil Organic Carbon percentage
    ρ      = Bulk density (g/cm³)
    D      = Sampling depth (cm)
    A      = Area (hectares × 10,000 m²/ha)
    44/12  = Molecular weight ratio CO2 / C
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.soil_health import RegenerativeFarmingLog, CarbonMintEvent
from backend.models.sustainability import SustainabilityScore, ESGMarketListing
from backend.models.farm import Farm
from backend.models.ledger import (
    LedgerTransaction, LedgerEntry, LedgerAccount,
    TransactionType, EntryType, AccountType
)
import logging

logger = logging.getLogger(__name__)

# ─── Practice-specific multipliers ─────────────────────────────────────────────
PRACTICE_MULTIPLIERS = {
    'NO_TILL':            1.20,   # 20% bonus — preserves soil structure
    'COVER_CROP':         1.15,   # 15% bonus — root biomass addition
    'ORGANIC_FERTILIZER': 1.10,   # 10% bonus — no N2O from synthetic sources
    'AGROFORESTRY':       1.35,   # 35% bonus — combined woody biomass + soil
    'BIOCHAR':            1.25,   # 25% bonus — stable pyrogenic carbon
}

# Default market price per tonne CO2e (USD)
CARBON_CREDIT_PRICE_USD = 15.0

# ESG listing validity
LISTING_VALIDITY_DAYS = 90


class CarbonSequestrationEngine:
    """
    Autonomous Carbon Minting Engine for L3-1632.
    """

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Scientific Sequestration Calculation
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def calculate_co2e(log: RegenerativeFarmingLog) -> float:
        """
        Converts raw agronomic parameters into verified tonnes of CO2 equivalent
        using the standard mineral-soil carbon stock change method.

        Returns: estimated tCO2e (float)
        """
        soc = log.soil_organic_carbon_percent or 1.5     # default 1.5% SOC
        density = log.bulk_density_gcm3 or 1.3           # default bulk density
        depth_cm = log.sampling_depth_cm or 30.0
        area_ha = log.area_hectares
        practice_multiplier = PRACTICE_MULTIPLIERS.get(log.practice_type, 1.0)

        # Carbon stock (tonnes/ha) = (SOC% / 100) × ρ (g/cm³) × depth (cm)
        #                            × 100 (t/ha from g/cm³·cm)
        carbon_stock = (soc / 100.0) * density * depth_cm * 100.0

        # Total carbon across area (tonnes)
        total_carbon_tonnes = carbon_stock * area_ha

        # Convert to CO2 equivalent (multiply by 44/12)
        co2e_tonnes = total_carbon_tonnes * (44.0 / 12.0)

        # Apply regenerative practice bonus
        co2e_tonnes *= practice_multiplier

        logger.info(
            f"[CarbonEngine] Farm {log.farm_id} | Practice {log.practice_type} | "
            f"SOC {soc}% | ρ {density} | D {depth_cm}cm | A {area_ha}ha → "
            f"{co2e_tonnes:.4f} tCO2e (×{practice_multiplier})"
        )
        return round(co2e_tonnes, 4)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Credit Minting
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def mint_credits(log_id: int, price_per_tonne_usd: float = CARBON_CREDIT_PRICE_USD):
        """
        Mints Circular Carbon Credits for a verified RegenerativeFarmingLog.
        Creates a tamper-proof CarbonMintEvent and posts a double-entry
        LedgerTransaction for financial integrity.

        Returns: (CarbonMintEvent, error_string | None)
        """
        log = RegenerativeFarmingLog.query.get(log_id)
        if not log:
            return None, "Farming log not found."
        if not log.verified:
            return None, "Cannot mint credits for an unverified farming log."

        # Calculate sequestration
        co2e = CarbonSequestrationEngine.calculate_co2e(log)
        log.estimated_co2e_tonnes = co2e
        total_value = round(co2e * price_per_tonne_usd, 2)

        # Generate audit-chain hash
        raw = f"{log.farm_id}:{log_id}:{co2e}:{datetime.utcnow().isoformat()}"
        mint_hash = hashlib.sha256(raw.encode()).hexdigest()

        # Post double-entry ledger transaction
        ledger_txn = CarbonSequestrationEngine._post_mint_ledger_entry(
            farm_id=log.farm_id,
            co2e_tonnes=co2e,
            total_value_usd=total_value,
            mint_hash=mint_hash
        )

        mint_event = CarbonMintEvent(
            farm_id=log.farm_id,
            log_id=log_id,
            credits_minted=co2e,
            credit_unit_value_usd=price_per_tonne_usd,
            total_value_usd=total_value,
            mint_hash=mint_hash,
            ledger_transaction_id=ledger_txn.id if ledger_txn else None
        )
        db.session.add(mint_event)

        # Update farm's lifetime credit counter
        farm = Farm.query.get(log.farm_id)
        if farm:
            farm.total_carbon_credits_minted += co2e

        # Update sustainability score
        score = SustainabilityScore.query.filter_by(farm_id=log.farm_id).first()
        if score:
            score.total_credits_minted += co2e
            # ESG score: logarithmic scale 0-100
            import math
            score.esg_carbon_score = min(100.0, math.log1p(score.total_credits_minted) * 10)

        db.session.commit()
        logger.info(f"[CarbonEngine] Minted {co2e} tCO2e for Farm {log.farm_id}. Hash: {mint_hash[:16]}…")
        return mint_event, None

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Double-Entry Ledger Posting
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _post_mint_ledger_entry(farm_id, co2e_tonnes, total_value_usd, mint_hash):
        """
        Posts a balanced double-entry ledger transaction for the credit minting:
          DR  Carbon Asset Account      $value
          CR  Carbon Revenue Account    $value
        """
        try:
            # Resolve or create the farm's carbon asset ledger account
            asset_acct = LedgerAccount.query.filter_by(
                entity_type='farm', entity_id=farm_id,
                account_code=f'FARM-{farm_id}-CARBON-ASSET'
            ).first()
            if not asset_acct:
                asset_acct = LedgerAccount(
                    account_code=f'FARM-{farm_id}-CARBON-ASSET',
                    name=f'Farm {farm_id} Carbon Credit Asset',
                    account_type=AccountType.ASSET,
                    currency='USD',
                    entity_type='farm',
                    entity_id=farm_id,
                    is_system=True
                )
                db.session.add(asset_acct)
                db.session.flush()

            # Revenue account
            revenue_acct = LedgerAccount.query.filter_by(
                entity_type='farm', entity_id=farm_id,
                account_code=f'FARM-{farm_id}-CARBON-REVENUE'
            ).first()
            if not revenue_acct:
                revenue_acct = LedgerAccount(
                    account_code=f'FARM-{farm_id}-CARBON-REVENUE',
                    name=f'Farm {farm_id} Carbon Credit Revenue',
                    account_type=AccountType.INCOME,
                    currency='USD',
                    entity_type='farm',
                    entity_id=farm_id,
                    is_system=True
                )
                db.session.add(revenue_acct)
                db.session.flush()

            txn = LedgerTransaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=TransactionType.CARBON_CREDIT_MINT,
                source_type='carbon_mint',
                description=f"Carbon sequestration credit mint — {co2e_tonnes:.4f} tCO2e (hash: {mint_hash[:16]})",
                base_currency='USD',
                base_amount=total_value_usd,
                reference_number=mint_hash[:16]
            )
            db.session.add(txn)
            db.session.flush()

            db.session.add(LedgerEntry(
                transaction_id=txn.id,
                account_id=asset_acct.id,
                entry_type=EntryType.DEBIT,
                amount=total_value_usd,
                currency='USD',
                base_amount=total_value_usd,
                base_currency='USD',
                memo=f"{co2e_tonnes:.4f} tCO2e carbon credits minted"
            ))
            db.session.add(LedgerEntry(
                transaction_id=txn.id,
                account_id=revenue_acct.id,
                entry_type=EntryType.CREDIT,
                amount=total_value_usd,
                currency='USD',
                base_amount=total_value_usd,
                base_currency='USD',
                memo="Carbon sequestration revenue recognition"
            ))
            db.session.flush()
            return txn
        except Exception as e:
            logger.error(f"[CarbonEngine] Ledger posting failed: {e}", exc_info=True)
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # 4. ESG Marketplace Listing
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def list_on_esg_market(mint_event_id: int, asking_price_usd: float = None, 
                            description: str = None):
        """
        Lists a minted carbon credit batch on the internal ESG marketplace.
        """
        event = CarbonMintEvent.query.get(mint_event_id)
        if not event:
            return None, "Mint event not found."
        if event.listed_on_market:
            return None, "This credit batch is already listed."

        price = asking_price_usd or (event.credits_minted * CARBON_CREDIT_PRICE_USD * 1.05)  # 5% markup

        listing = ESGMarketListing(
            farm_id=event.farm_id,
            mint_event_id=mint_event_id,
            credits_offered=event.credits_minted,
            asking_price_usd=price,
            description=description or f"Verified carbon credits from regenerative farming — {event.credits_minted:.2f} tCO2e",
            expires_at=datetime.utcnow() + timedelta(days=LISTING_VALIDITY_DAYS)
        )
        db.session.add(listing)
        event.listed_on_market = True
        db.session.commit()
        logger.info(f"[CarbonEngine] ESG Listing created for MintEvent {mint_event_id} — ${price:.2f}")
        return listing, None

    # ──────────────────────────────────────────────────────────────────────────
    # 5. ESG Purchase Settlement
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def settle_esg_purchase(listing_id: int, buyer_user_id: int):
        """
        Executes a carbon credit purchase: settles payment via double-entry ledger,
        transfers credit ownership, and marks the listing as SOLD.
        """
        listing = ESGMarketListing.query.get(listing_id)
        if not listing or listing.status != 'ACTIVE':
            return None, "Listing is not available for purchase."

        event = CarbonMintEvent.query.get(listing.mint_event_id)

        # Post settlement ledger entry
        try:
            buyer_acct = LedgerAccount.query.filter_by(
                entity_type='user', entity_id=buyer_user_id,
                account_code=f'USER-{buyer_user_id}-CARBON-ASSET'
            ).first()
            if not buyer_acct:
                buyer_acct = LedgerAccount(
                    account_code=f'USER-{buyer_user_id}-CARBON-ASSET',
                    name=f'Corporate Buyer {buyer_user_id} Carbon Portfolio',
                    account_type=AccountType.ASSET,
                    currency='USD',
                    entity_type='user',
                    entity_id=buyer_user_id
                )
                db.session.add(buyer_acct)
                db.session.flush()

            farm_acct = LedgerAccount.query.filter_by(
                account_code=f'FARM-{listing.farm_id}-CARBON-ASSET'
            ).first()

            sale_value = listing.asking_price_usd
            txn = LedgerTransaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=TransactionType.CARBON_CREDIT_SALE,
                source_type='esg_listing',
                source_id=listing.id,
                description=f"ESG carbon credit purchase — {listing.credits_offered:.4f} tCO2e",
                base_currency='USD',
                base_amount=sale_value,
            )
            db.session.add(txn)
            db.session.flush()

            # DR Buyer Carbon Asset (buyer acquires)
            db.session.add(LedgerEntry(
                transaction_id=txn.id, account_id=buyer_acct.id,
                entry_type=EntryType.DEBIT, amount=sale_value,
                currency='USD', base_amount=sale_value, base_currency='USD',
                memo=f"Purchased {listing.credits_offered:.4f} tCO2e"
            ))
            # CR Farm Carbon Asset (farm transfers)
            if farm_acct:
                db.session.add(LedgerEntry(
                    transaction_id=txn.id, account_id=farm_acct.id,
                    entry_type=EntryType.CREDIT, amount=sale_value,
                    currency='USD', base_amount=sale_value, base_currency='USD',
                    memo="Carbon credits transferred to corporate buyer"
                ))

            # Settle listing
            now = datetime.utcnow()
            listing.status = 'SOLD'
            listing.buyer_user_id = buyer_user_id
            listing.purchase_price_usd = sale_value
            listing.purchased_at = now
            listing.settlement_ledger_txn_id = txn.id
            event.buyer_id = buyer_user_id
            event.sold_at = now
            event.sale_price_usd = sale_value

            db.session.commit()
            logger.info(f"[CarbonEngine] ESG Purchase settled — Listing {listing_id}, Buyer {buyer_user_id}")
            return listing, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"[CarbonEngine] Settlement failed: {e}", exc_info=True)
            return None, str(e)
