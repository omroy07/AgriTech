"""
Yield Resilience Service — L3-1630
=====================================
Autonomous "Yield-at-Risk" engine that:

1. Classifies incoming climate telemetry as extreme events (HEAT_WAVE, FROST, etc.)
2. Detects consecutive-day Force Majeure streaks for each farm
3. Triggers Parametric Auto-Settlement of insurance policies without manual claims
4. Applies real-time climate-risk discounts to open ForwardContracts
5. Posts all financial flows through the double-entry ledger

Science / Finance Logic:
  - Yield-at-Risk (YaR) = (streak_days / required_days) × peak_severity_factor × payout_pct
  - Climate-risk discount on futures = YaR × market_volatility_at_lock
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.extensions import db
from backend.models.weather import (
    ClimateTelemetryEvent, ForceMajeureAlert, ParametricPolicyTrigger
)
from backend.models.insurance_v2 import (
    CropPolicy, ParametricAutoSettlement, PolicyStatus
)
from backend.models.market import ForwardContract, PriceHedgingLog
from backend.models.ledger import (
    LedgerTransaction, LedgerEntry, LedgerAccount,
    TransactionType, EntryType, AccountType
)
from backend.models.audit_log import AuditLog
from backend.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

# ─── Parametric Thresholds ─────────────────────────────────────────────────────
FORCE_MAJEURE_RULES = {
    'HEAT_WAVE':  {'field': 'temperature_c',   'op': 'gt', 'default_threshold': 45.0},
    'FROST':      {'field': 'temperature_c',   'op': 'lt', 'default_threshold': 0.0},
    'FLOOD':      {'field': 'rainfall_mm',     'op': 'gt', 'default_threshold': 150.0},
    'DROUGHT':    {'field': 'rainfall_mm',     'op': 'lt', 'default_threshold': 2.0},
    'CYCLONE':    {'field': 'wind_speed_kmh',  'op': 'gt', 'default_threshold': 120.0},
}

# Minimum consecutive days to declare a Force Majeure
DEFAULT_CONSECUTIVE_DAYS = 3


class YieldResilienceEngine:
    """
    Autonomous Parametric Climate Insurance & Futures Risk Engine (L3-1630).
    """

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Telemetry Ingestion & Classification
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def ingest_telemetry(farm_id: int, temperature_c: float, rainfall_mm: float,
                          humidity_pct: float = None, wind_speed_kmh: float = None,
                          solar_radiation_wm2: float = None,
                          source: str = 'IOT_SENSOR') -> ClimateTelemetryEvent:
        """
        Persists a climate telemetry reading, classifies it as extreme if thresholds
        are breached, and triggers streak evaluation.
        """
        extreme_type = None
        is_extreme = False

        for evt_type, rule in FORCE_MAJEURE_RULES.items():
            val = temperature_c if rule['field'] == 'temperature_c' else \
                  rainfall_mm if rule['field'] == 'rainfall_mm' else \
                  (wind_speed_kmh or 0.0)
            threshold = rule['default_threshold']
            breached = val > threshold if rule['op'] == 'gt' else val < threshold
            if breached:
                is_extreme = True
                extreme_type = evt_type
                break  # First matching rule wins

        event = ClimateTelemetryEvent(
            farm_id=farm_id,
            temperature_c=temperature_c,
            rainfall_mm=rainfall_mm,
            humidity_pct=humidity_pct,
            wind_speed_kmh=wind_speed_kmh,
            solar_radiation_wm2=solar_radiation_wm2,
            is_extreme=is_extreme,
            extreme_type=extreme_type,
            source=source
        )
        db.session.add(event)
        db.session.flush()

        if is_extreme:
            YieldResilienceEngine._evaluate_streak(farm_id, extreme_type)

        db.session.commit()
        return event

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Consecutive-Day Streak Detection
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _evaluate_streak(farm_id: int, extreme_type: str):
        """
        Counts how many consecutive calendar days this farm has had extreme
        events of this type. If streak ≥ required days → raise ForceMajeureAlert.
        """
        # Count distinct days in last 14 days with this extreme_type
        cutoff = datetime.utcnow() - timedelta(days=14)
        extreme_days = db.session.query(
            func.date(ClimateTelemetryEvent.recorded_at).label('day')
        ).filter(
            ClimateTelemetryEvent.farm_id == farm_id,
            ClimateTelemetryEvent.extreme_type == extreme_type,
            ClimateTelemetryEvent.recorded_at >= cutoff
        ).distinct().order_by('day').all()

        if not extreme_days:
            return

        # Check for consecutive streak ending today
        dates = [row.day for row in extreme_days]
        streak = 1
        for i in range(len(dates) - 1, 0, -1):
            delta = (dates[i] - dates[i - 1]).days if hasattr(dates[i], 'days') else \
                    (datetime.strptime(str(dates[i]), '%Y-%m-%d') -
                     datetime.strptime(str(dates[i - 1]), '%Y-%m-%d')).days
            if delta == 1:
                streak += 1
            else:
                break

        logger.info(f"[YieldEngine] Farm {farm_id} | {extreme_type} streak: {streak} days")

        # Check against all active triggers for this farm's policies
        policies = CropPolicy.query.filter_by(farm_id=farm_id, 
                                               status=PolicyStatus.ACTIVE.value).all()
        for policy in policies:
            trigger = ParametricPolicyTrigger.query.filter_by(
                policy_id=policy.id,
                trigger_type=extreme_type,
                is_active=True
            ).first()

            required_days = trigger.required_consecutive_days if trigger else DEFAULT_CONSECUTIVE_DAYS

            if streak >= required_days:
                # Check no active alert already raised for this policy + type
                existing = ForceMajeureAlert.query.filter_by(
                    farm_id=farm_id,
                    trigger_type=extreme_type,
                    status='ACTIVE'
                ).first()

                if not existing:
                    YieldResilienceEngine._raise_force_majeure(
                        farm_id, extreme_type, streak, trigger
                    )

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Force Majeure Alert + Parametric Auto-Settlement
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _raise_force_majeure(farm_id: int, trigger_type: str, streak: int,
                              trigger: ParametricPolicyTrigger = None):
        """
        Raises a ForceMajeureAlert and immediately triggers parametric
        auto-settlement for all eligible policies on the farm.
        """
        threshold = trigger.threshold_value if trigger else \
                    FORCE_MAJEURE_RULES[trigger_type]['default_threshold']

        alert = ForceMajeureAlert(
            farm_id=farm_id,
            trigger_type=trigger_type,
            threshold_value=threshold,
            consecutive_days=streak,
            status='ACTIVE'
        )
        db.session.add(alert)
        db.session.flush()
        logger.warning(f"[YieldEngine] 🚨 FORCE MAJEURE raised: Farm {farm_id} | {trigger_type} | {streak}d")

        # Auto-settle all parametric-enabled policies
        policies = CropPolicy.query.filter_by(
            farm_id=farm_id,
            status=PolicyStatus.ACTIVE.value,
            parametric_enabled=True
        ).all()

        for policy in policies:
            payout_pct = trigger.payout_percentage if trigger else 100.0
            YieldResilienceEngine._execute_parametric_settlement(alert, policy, payout_pct)

        # Also cascade: suspend open ForwardContracts
        YieldResilienceEngine._suspend_futures(farm_id, trigger_type)

        # Notify
        NotificationService.create_notification(
            title=f"🌡️ FORCE MAJEURE: {trigger_type}",
            message=(
                f"Autonomous parametric settlement triggered for your farm after "
                f"{streak} consecutive days of {trigger_type.replace('_', ' ').title()}. "
                f"Payouts are being processed without manual claim submission."
            ),
            notification_type="PARAMETRIC_ALERT",
            user_id=farm_id
        )

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Parametric Payout Execution
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _execute_parametric_settlement(alert: ForceMajeureAlert,
                                        policy: CropPolicy,
                                        payout_pct: float):
        """
        Calculates payout, posts a double-entry ledger transaction, and creates
        an immutable ParametricAutoSettlement audit record.
        """
        payout_amount = round(policy.coverage_amount * (payout_pct / 100.0), 2)

        # Gather peak reading for evidence
        recent_readings = ClimateTelemetryEvent.query.filter_by(
            farm_id=alert.farm_id, extreme_type=alert.trigger_type
        ).order_by(ClimateTelemetryEvent.temperature_c.desc()).limit(10).all()
        peak_temp = max((r.temperature_c for r in recent_readings), default=0.0)

        # Build tamper-proof evidence hash
        evidence = {
            'policy_id': policy.id,
            'alert_id': alert.id,
            'trigger_type': alert.trigger_type,
            'streak_days': alert.consecutive_days,
            'payout_amount': payout_amount,
            'timestamp': datetime.utcnow().isoformat()
        }
        evidence_hash = hashlib.sha256(
            json.dumps(evidence, sort_keys=True).encode()
        ).hexdigest()

        # Post ledger transaction
        ledger_txn_id = YieldResilienceEngine._post_settlement_ledger(
            farm_id=alert.farm_id,
            policy_id=policy.id,
            payout_amount=payout_amount,
            description=(
                f"Parametric auto-settlement: {alert.trigger_type} | "
                f"{alert.consecutive_days}d streak | Policy {policy.id}"
            )
        )

        settlement = ParametricAutoSettlement(
            policy_id=policy.id,
            alert_id=alert.id,
            coverage_amount=policy.coverage_amount,
            payout_percentage=payout_pct,
            payout_amount=payout_amount,
            trigger_type=alert.trigger_type,
            consecutive_days_observed=alert.consecutive_days,
            peak_temperature_c=peak_temp,
            evidence_hash=evidence_hash,
            ledger_transaction_id=ledger_txn_id
        )
        db.session.add(settlement)

        # Mark alert as settled
        alert.auto_settled = True
        alert.status = 'AUTO_SETTLED'
        alert.resolved_at = datetime.utcnow()
        alert.settlement_ledger_txn_id = ledger_txn_id

        # Update policy yield-at-risk
        policy.yield_at_risk_pct = payout_pct
        policy.last_climate_check = datetime.utcnow()

        # Audit log
        db.session.add(AuditLog(
            action="PARAMETRIC_AUTO_SETTLEMENT",
            resource_type="INSURANCE_POLICY",
            resource_id=str(policy.id),
            new_values=json.dumps({
                'payout': payout_amount,
                'trigger': alert.trigger_type,
                'evidence_hash': evidence_hash[:16]
            }),
            risk_level="HIGH",
            is_financial=True,
            financial_impact=payout_amount,
            autonomous_decision_flag=True
        ))
        logger.info(
            f"[YieldEngine] ✅ Auto-settlement posted: Policy {policy.id} | "
            f"${payout_amount:.2f} | Hash {evidence_hash[:16]}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Futures Mark-to-Market: Climate-Risk Discount
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _suspend_futures(farm_id: int, trigger_type: str):
        """
        Applies real-time climate-risk discount to all open ForwardContracts
        for this farm and suspends SIGNED contracts under Force Majeure.
        """
        open_contracts = ForwardContract.query.filter(
            ForwardContract.farm_id == farm_id,
            ForwardContract.status.in_(['OPEN', 'SIGNED']),
            ForwardContract.force_majeure_suspended == False  # noqa
        ).all()

        for contract in open_contracts:
            # YaR-driven discount: up to 15% price reduction
            yar_discount = min(0.15, contract.yield_at_risk_pct / 100.0 * 0.30)
            contract.climate_risk_discount = round(yar_discount * 100, 2)
            contract.force_majeure_suspended = True

            db.session.add(PriceHedgingLog(
                farm_id=farm_id,
                action="CLIMATE_RISK_SUSPENSION",
                old_hedge_ratio=contract.hedge_ratio or 0,
                new_hedge_ratio=(contract.hedge_ratio or 0) * (1 - yar_discount),
                trigger_reason=f"Force Majeure: {trigger_type} auto-suspension",
                market_price_snapshot=contract.locked_price_per_unit
            ))

            # Post YIELD_RISK_ADJUSTMENT ledger entry
            discount_amount = round(
                contract.locked_price_per_unit * contract.estimated_quantity * yar_discount, 2
            )
            if discount_amount > 0:
                YieldResilienceEngine._post_yield_risk_ledger(
                    farm_id, contract.id, discount_amount, trigger_type
                )

            logger.info(
                f"[YieldEngine] Contract {contract.id} suspended | "
                f"Discount: {contract.climate_risk_discount:.1f}%"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Yield-at-Risk Calculator (public)
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def compute_yield_at_risk(farm_id: int) -> dict:
        """
        Computes the current Yield-at-Risk profile for a farm:
        - Active extreme-event streaks
        - Open contract exposure
        - Aggregate financial exposure (USD)
        """
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent_extremes = ClimateTelemetryEvent.query.filter(
            ClimateTelemetryEvent.farm_id == farm_id,
            ClimateTelemetryEvent.is_extreme == True,  # noqa
            ClimateTelemetryEvent.recorded_at >= cutoff
        ).all()

        active_alerts = ForceMajeureAlert.query.filter_by(
            farm_id=farm_id, status='ACTIVE'
        ).all()

        open_contracts = ForwardContract.query.filter(
            ForwardContract.farm_id == farm_id,
            ForwardContract.status.in_(['OPEN', 'SIGNED'])
        ).all()

        total_locked_value = sum(
            c.locked_price_per_unit * c.estimated_quantity for c in open_contracts
        )
        max_exposure = sum(
            c.locked_price_per_unit * c.estimated_quantity * (c.climate_risk_discount / 100.0)
            for c in open_contracts if c.climate_risk_discount
        )

        return {
            'farm_id': farm_id,
            'extreme_events_7d': len(recent_extremes),
            'active_force_majeure_alerts': len(active_alerts),
            'open_contract_value_usd': round(total_locked_value, 2),
            'max_climate_exposure_usd': round(max_exposure, 2),
            'risk_tier': (
                'CRITICAL' if active_alerts else
                'HIGH' if len(recent_extremes) >= 5 else
                'MODERATE' if len(recent_extremes) >= 2 else
                'LOW'
            )
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Ledger Helpers
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _post_settlement_ledger(farm_id, policy_id, payout_amount, description) -> int | None:
        """DR Insurance Liability / CR Farm Cash — parametric payout."""
        try:
            insurer_acct = LedgerAccount.query.filter_by(
                account_code='PLATFORM-INSURANCE-LIABILITY'
            ).first()
            if not insurer_acct:
                insurer_acct = LedgerAccount(
                    account_code='PLATFORM-INSURANCE-LIABILITY',
                    name='Platform Parametric Insurance Liability',
                    account_type=AccountType.LIABILITY,
                    currency='USD', is_system=True
                )
                db.session.add(insurer_acct)
                db.session.flush()

            farm_cash_acct = LedgerAccount.query.filter_by(
                account_code=f'FARM-{farm_id}-CASH'
            ).first()
            if not farm_cash_acct:
                farm_cash_acct = LedgerAccount(
                    account_code=f'FARM-{farm_id}-CASH',
                    name=f'Farm {farm_id} Operating Cash',
                    account_type=AccountType.ASSET,
                    currency='USD', entity_type='farm', entity_id=farm_id
                )
                db.session.add(farm_cash_acct)
                db.session.flush()

            txn = LedgerTransaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=TransactionType.PARAMETRIC_SETTLEMENT,
                source_type='parametric_insurance',
                source_id=policy_id,
                description=description,
                base_currency='USD',
                base_amount=payout_amount
            )
            db.session.add(txn)
            db.session.flush()

            db.session.add(LedgerEntry(
                transaction_id=txn.id, account_id=insurer_acct.id,
                entry_type=EntryType.DEBIT, amount=payout_amount,
                currency='USD', base_amount=payout_amount, base_currency='USD',
                memo=description
            ))
            db.session.add(LedgerEntry(
                transaction_id=txn.id, account_id=farm_cash_acct.id,
                entry_type=EntryType.CREDIT, amount=payout_amount,
                currency='USD', base_amount=payout_amount, base_currency='USD',
                memo="Parametric payout received"
            ))
            db.session.flush()
            return txn.id
        except Exception as e:
            logger.error(f"[YieldEngine] Ledger error: {e}", exc_info=True)
            return None

    @staticmethod
    def _post_yield_risk_ledger(farm_id, contract_id, discount_amount, trigger_type):
        """CR Forward Contract Asset / DR Climate Risk Expense — mark-to-market."""
        try:
            risk_expense_acct = LedgerAccount.query.filter_by(
                account_code=f'FARM-{farm_id}-CLIMATE-RISK-EXPENSE'
            ).first()
            if not risk_expense_acct:
                risk_expense_acct = LedgerAccount(
                    account_code=f'FARM-{farm_id}-CLIMATE-RISK-EXPENSE',
                    name=f'Farm {farm_id} Climate Risk Expense',
                    account_type=AccountType.EXPENSE,
                    currency='USD', entity_type='farm', entity_id=farm_id
                )
                db.session.add(risk_expense_acct)
                db.session.flush()

            futures_acct = LedgerAccount.query.filter_by(
                account_code=f'FARM-{farm_id}-FUTURES-ASSET'
            ).first()
            if not futures_acct:
                futures_acct = LedgerAccount(
                    account_code=f'FARM-{farm_id}-FUTURES-ASSET',
                    name=f'Farm {farm_id} Forward Contracts Asset',
                    account_type=AccountType.ASSET,
                    currency='USD', entity_type='farm', entity_id=farm_id
                )
                db.session.add(futures_acct)
                db.session.flush()

            txn = LedgerTransaction(
                transaction_id=str(uuid.uuid4()),
                transaction_type=TransactionType.YIELD_RISK_ADJUSTMENT,
                source_type='forward_contract',
                source_id=contract_id,
                description=f"Climate-risk mark-to-market: {trigger_type}",
                base_currency='USD',
                base_amount=discount_amount
            )
            db.session.add(txn)
            db.session.flush()

            db.session.add(LedgerEntry(
                transaction_id=txn.id, account_id=risk_expense_acct.id,
                entry_type=EntryType.DEBIT, amount=discount_amount,
                currency='USD', base_amount=discount_amount, base_currency='USD',
                memo=f"YaR discount applied — {trigger_type}"
            ))
            db.session.add(LedgerEntry(
                transaction_id=txn.id, account_id=futures_acct.id,
                entry_type=EntryType.CREDIT, amount=discount_amount,
                currency='USD', base_amount=discount_amount, base_currency='USD',
                memo="Forward contract value reduced"
            ))
            db.session.flush()
        except Exception as e:
            logger.error(f"[YieldEngine] YaR ledger error: {e}", exc_info=True)
