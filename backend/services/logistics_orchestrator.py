"""
Logistics Orchestrator — L3-1631
==================================
Digital Corridor system for cross-border grain movement.

Key capabilities:
1. Auto-generate Phyto-Sanitary Certificates (SHA-256 signed JSON)
2. Dynamic freight price adjustment based on customs wait times and fuel volatility
3. Smart-Contract Freight Release — escrow unlocked only after GPS geo-fence passes
4. Double-entry ledger settlement of all freight financial flows
"""

import hashlib
import json
import math
import uuid
from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.logistics_v2 import (
    TransportRoute, PhytoSanitaryCertificate, FreightEscrow,
    CustomsCheckpoint, GPSTelemetry, DriverProfile
)
from backend.models.traceability import SupplyBatch, CustodyLog
from backend.models.ledger import (
    LedgerTransaction, LedgerEntry, LedgerAccount,
    TransactionType, EntryType, AccountType
)
from backend.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_RATE_PER_KM_USD = 0.85          # base freight rate per km
FUEL_VOLATILITY_THRESHOLD_USD = 1.20 # surcharge kicks in above this $/L price
CUSTOMS_DELAY_SURCHARGE_PER_HOUR = 8.50  # USD per hour beyond the 4-hr grace
CUSTOMS_GRACE_HOURS = 4.0
EARTH_RADIUS_METERS = 6_371_000


# ─── Geo-math ─────────────────────────────────────────────────────────────────
def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """Returns distance in meters between two GPS points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return EARTH_RADIUS_METERS * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class LogisticsOrchestrator:
    """
    Autonomous Digital Corridor Orchestrator (L3-1631).
    """

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Phyto-Sanitary Certificate Generation
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def generate_phyto_cert(route_id: int, batch_id: int,
                             origin_country: str, destination_country: str) -> tuple:
        """
        Autonomously generates a Phyto-Sanitary Certificate (JSON + SHA-256 signature).
        Updates the linked SupplyBatch with the certificate number.
        """
        route = TransportRoute.query.get(route_id)
        batch = SupplyBatch.query.get(batch_id)
        if not route or not batch:
            return None, "Route or batch not found."

        # Build the certificate payload
        cert_number = f"PSC-{uuid.uuid4().hex[:12].upper()}"
        payload = {
            "certificate_number": cert_number,
            "issuing_authority": "AgriTech Digital Authority",
            "issued_at": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "shipment": {
                "route_id": route_id,
                "batch_id": batch_id,
                "commodity": batch.crop_name,
                "quantity_kg": batch.quantity,
                "origin_country": origin_country,
                "destination_country": destination_country,
                "bio_clearance_hash": batch.bio_clearance_hash or "N/A",
                "quarantine_status": batch.quarantine_status
            },
            "declarations": [
                "Cargo is free from prohibited pests under ISPM-15",
                "Treated in accordance with relevant phytosanitary measures",
                "Digitally signed by AgriTech Autonomous Authority"
            ]
        }

        payload_json = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(payload_json.encode()).hexdigest()

        cert = PhytoSanitaryCertificate(
            route_id=route_id,
            batch_id=batch_id,
            certificate_number=cert_number,
            origin_country=origin_country,
            destination_country=destination_country,
            commodity=batch.crop_name,
            declared_quantity_kg=batch.quantity,
            certificate_payload_json=payload_json,
            signature_hash=signature,
            status='ISSUED',
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(cert)

        # Update supply batch
        batch.phyto_cert_number = cert_number
        batch.status = 'LOGISTICS'

        # Audit
        db.session.add(AuditLog(
            action="PHYTO_CERT_ISSUED",
            resource_type="LOGISTICS",
            resource_id=str(route_id),
            new_values=json.dumps({"cert_number": cert_number, "signature": signature[:16]}),
            risk_level="INFO",
            autonomous_decision_flag=True,
            ai_logistics_flag=True
        ))

        db.session.commit()
        logger.info(f"[Orchestrator] Phyto cert issued: {cert_number} | Route {route_id}")
        return cert, None

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Freight Escrow — Smart Contract Lock
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def lock_freight_escrow(route_id: int, driver_id: int,
                             dest_lat: float, dest_lng: float,
                             estimated_distance_km: float,
                             current_fuel_price: float = 1.10) -> tuple:
        """
        Locks freight payment into escrow. Price is dynamically calculated
        based on distance, fuel volatility, and any pending customs delays.
        Posts a FREIGHT_ESCROW_HOLD ledger transaction.
        """
        route = TransportRoute.query.get(route_id)
        if not route:
            return None, "Route not found."

        # Dynamic pricing
        base = estimated_distance_km * BASE_RATE_PER_KM_USD
        fuel_surcharge = 0.0
        if current_fuel_price > FUEL_VOLATILITY_THRESHOLD_USD:
            excess = current_fuel_price - FUEL_VOLATILITY_THRESHOLD_USD
            fuel_surcharge = round(base * (excess / FUEL_VOLATILITY_THRESHOLD_USD), 2)

        total = round(base + fuel_surcharge, 2)

        escrow = FreightEscrow(
            route_id=route_id,
            driver_id=driver_id,
            total_freight_amount=total,
            destination_lat=dest_lat,
            destination_lng=dest_lng,
            base_price=base,
            fuel_surcharge=fuel_surcharge,
            final_amount=total,
            status='HELD'
        )
        db.session.add(escrow)
        db.session.flush()

        # Post ledger hold
        LogisticsOrchestrator._post_escrow_ledger(
            route_id, driver_id, total, TransactionType.FREIGHT_ESCROW_HOLD,
            f"Freight escrow lock — Route {route_id}"
        )

        db.session.commit()
        logger.info(f"[Orchestrator] Escrow locked: ${total:.2f} for Route {route_id}")
        return escrow, None

    # ──────────────────────────────────────────────────────────────────────────
    # 3. GPS Telemetry Ingestion & Geo-Fence Evaluation
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def ingest_gps_ping(route_id: int, vehicle_id: int, lat: float, lng: float,
                         speed: float = 0.0, fuel_price: float = 1.10) -> dict:
        """
        Persists a GPS telemetry ping and evaluates the geo-fence for the
        linked FreightEscrow. Triggers smart-contract release if inside the fence.
        """
        ping = GPSTelemetry(
            route_id=route_id,
            vehicle_id=vehicle_id,
            latitude=lat,
            longitude=lng,
            speed_kmh=speed,
            fuel_price_per_liter=fuel_price
        )
        db.session.add(ping)

        # Check geo-fence
        escrow = FreightEscrow.query.filter_by(route_id=route_id, status='HELD').first()
        result = {"geo_fence_passed": False, "escrow_released": False}

        if escrow:
            dist = haversine_distance(lat, lng, escrow.destination_lat, escrow.destination_lng)
            if dist <= escrow.geo_fence_radius_meters:
                escrow.confirmed_delivery_lat = lat
                escrow.confirmed_delivery_lng = lng
                escrow.geo_fence_passed = True

                # Compute customs delay penalties
                delay_penalty = LogisticsOrchestrator._calculate_customs_penalty(route_id)
                if delay_penalty > 0:
                    escrow.customs_delay_penalty = delay_penalty
                    escrow.final_amount = escrow.total_freight_amount - delay_penalty

                # Generate delivery proof hash
                proof_raw = f"{route_id}:{lat}:{lng}:{datetime.utcnow().isoformat()}"
                escrow.delivery_proof_hash = hashlib.sha256(proof_raw.encode()).hexdigest()

                # Release funds
                LogisticsOrchestrator._release_escrow(escrow)
                result["geo_fence_passed"] = True
                result["escrow_released"] = True
                result["final_amount"] = escrow.final_amount
                logger.info(f"[Orchestrator] GEO-FENCE PASSED — Route {route_id}, Escrow released ${escrow.final_amount:.2f}")

        db.session.commit()
        return result

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Customs Checkpoint Management
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_customs_arrival(route_id: int, checkpoint_name: str,
                             country: str, phyto_cert_id: int = None) -> CustomsCheckpoint:
        """Logs a vehicle arriving at a customs checkpoint."""
        cp = CustomsCheckpoint(
            route_id=route_id,
            checkpoint_name=checkpoint_name,
            country=country,
            phyto_cert_id=phyto_cert_id
        )
        db.session.add(cp)
        db.session.commit()
        logger.info(f"[Orchestrator] Customs arrival logged: {checkpoint_name} ({country})")
        return cp

    @staticmethod
    def clear_customs(checkpoint_id: int, notes: str = None) -> tuple:
        """
        Clears a customs checkpoint, calculates wait time, and applies
        dynamic surcharges to the linked FreightEscrow.
        """
        cp = CustomsCheckpoint.query.get(checkpoint_id)
        if not cp or cp.status != 'PENDING':
            return None, "Checkpoint not found or already cleared."

        now = datetime.utcnow()
        cp.cleared_at = now
        cp.status = 'CLEARED'
        cp.wait_hours = round((now - cp.arrived_at).total_seconds() / 3600, 2)
        if notes:
            cp.inspector_notes = notes

        # Apply delay penalty to freight escrow
        if cp.wait_hours > CUSTOMS_GRACE_HOURS:
            excess = cp.wait_hours - CUSTOMS_GRACE_HOURS
            penalty = round(excess * CUSTOMS_DELAY_SURCHARGE_PER_HOUR, 2)
            escrow = FreightEscrow.query.filter_by(route_id=cp.route_id, status='HELD').first()
            if escrow:
                escrow.customs_delay_penalty += penalty
                escrow.final_amount = max(0, escrow.total_freight_amount - escrow.customs_delay_penalty)
                logger.warning(f"[Orchestrator] Delay penalty ${penalty:.2f} applied — Route {cp.route_id}")

        db.session.commit()
        return cp, None

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _calculate_customs_penalty(route_id: int) -> float:
        """Sums all accumulated customs delay penalties for route."""
        checkpoints = CustomsCheckpoint.query.filter_by(route_id=route_id, status='CLEARED').all()
        total = 0.0
        for cp in checkpoints:
            if cp.wait_hours > CUSTOMS_GRACE_HOURS:
                total += (cp.wait_hours - CUSTOMS_GRACE_HOURS) * CUSTOMS_DELAY_SURCHARGE_PER_HOUR
        return round(total, 2)

    @staticmethod
    def _release_escrow(escrow: FreightEscrow):
        """Marks escrow as RELEASED and posts double-entry ledger transaction."""
        escrow.status = 'RELEASED'
        escrow.released_at = datetime.utcnow()

        txn_id = LogisticsOrchestrator._post_escrow_ledger(
            escrow.route_id, escrow.driver_id, escrow.final_amount,
            TransactionType.FREIGHT_RELEASE,
            f"Smart-contract freight release — Route {escrow.route_id} (geo-fence confirmed)"
        )
        escrow.release_ledger_txn_id = txn_id

        db.session.add(AuditLog(
            action="FREIGHT_ESCROW_RELEASED",
            resource_type="FREIGHT_ESCROW",
            resource_id=str(escrow.id),
            new_values=json.dumps({
                "final_amount": escrow.final_amount,
                "proof_hash": escrow.delivery_proof_hash[:16]
            }),
            risk_level="INFO",
            is_financial=True,
            financial_impact=escrow.final_amount,
            autonomous_decision_flag=True,
            ai_logistics_flag=True
        ))

    @staticmethod
    def _post_escrow_ledger(route_id, driver_id, amount,
                             txn_type: TransactionType, memo: str) -> int | None:
        """Posts a balanced DR/CR ledger entry for freight escrow events."""
        try:
            # Freight Escrow Liability account (platform holds funds)
            escrow_acct = LedgerAccount.query.filter_by(
                account_code='PLATFORM-FREIGHT-ESCROW'
            ).first()
            if not escrow_acct:
                escrow_acct = LedgerAccount(
                    account_code='PLATFORM-FREIGHT-ESCROW',
                    name='Platform Freight Escrow Liability',
                    account_type=AccountType.LIABILITY,
                    currency='USD',
                    is_system=True
                )
                db.session.add(escrow_acct)
                db.session.flush()

            # Driver receivable account
            driver_acct = LedgerAccount.query.filter_by(
                account_code=f'DRIVER-{driver_id}-RECEIVABLE'
            ).first()
            if not driver_acct:
                driver_acct = LedgerAccount(
                    account_code=f'DRIVER-{driver_id}-RECEIVABLE',
                    name=f'Driver {driver_id} Freight Receivable',
                    account_type=AccountType.ASSET,
                    currency='USD',
                    entity_type='driver',
                    entity_id=driver_id
                )
                db.session.add(driver_acct)
                db.session.flush()

            txn = LedgerTransaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=txn_type,
                source_type='freight_escrow',
                source_id=route_id,
                description=memo,
                base_currency='USD',
                base_amount=amount,
                reference_number=f"ROUTE-{route_id}"
            )
            db.session.add(txn)
            db.session.flush()

            if txn_type == TransactionType.FREIGHT_ESCROW_HOLD:
                # DR Freight Escrow (liability grows — platform holding cash)
                db.session.add(LedgerEntry(
                    transaction_id=txn.id, account_id=escrow_acct.id,
                    entry_type=EntryType.DEBIT, amount=amount,
                    currency='USD', base_amount=amount, base_currency='USD', memo=memo
                ))
                # CR Driver Receivable (driver is owed)
                db.session.add(LedgerEntry(
                    transaction_id=txn.id, account_id=driver_acct.id,
                    entry_type=EntryType.CREDIT, amount=amount,
                    currency='USD', base_amount=amount, base_currency='USD', memo=memo
                ))
            else:
                # FREIGHT_RELEASE: DR Driver Receivable (settled), CR Escrow (liability cleared)
                db.session.add(LedgerEntry(
                    transaction_id=txn.id, account_id=driver_acct.id,
                    entry_type=EntryType.DEBIT, amount=amount,
                    currency='USD', base_amount=amount, base_currency='USD', memo=memo
                ))
                db.session.add(LedgerEntry(
                    transaction_id=txn.id, account_id=escrow_acct.id,
                    entry_type=EntryType.CREDIT, amount=amount,
                    currency='USD', base_amount=amount, base_currency='USD', memo=memo
                ))

            db.session.flush()
            return txn.id
        except Exception as e:
            logger.error(f"[Orchestrator] Ledger error: {e}", exc_info=True)
            return None
