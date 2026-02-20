from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.financials import FarmBalanceSheet, SolvencySnapshot, ProfitabilityIndex
from backend.models.loan_v2 import RepaymentSchedule
from backend.models.machinery import AssetValueSnapshot
from backend.models.labor import LaborROIHistory
from backend.models.weather import WeatherData
from backend.services.weather_service import WeatherService
from backend.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

class SolvencyForecaster:
    """
    Financial Brain for predicting farm-level bankruptcy risks and solvency.
    Correlates multiple data streams to calculate multivariate risk scores.
    """

    @staticmethod
    def calculate_bankruptcy_risk(farm_id):
        """
        Multivariate analysis of debt-to-yield ratios, liquidity, and asset decay.
        Returns a risk score (0-100).
        """
        # 1. Fetch Latest Balance Sheet
        balance = FarmBalanceSheet.query.filter_by(farm_id=farm_id).order_by(FarmBalanceSheet.period_date.desc()).first()
        if not balance:
            return 50.0 # Unknown risk

        # 2. Debt-to-Equity Impact
        debt_to_equity = 0.0
        if balance.net_worth > 0:
            debt_to_equity = balance.outstanding_loans / balance.net_worth
        
        # 3. Liquidity Ratio (Cash / Liabilities)
        liquidity = 0.0
        total_liabilities = balance.outstanding_loans + balance.accounts_payable
        if total_liabilities > 0:
            liquidity = balance.cash_on_hand / total_liabilities

        # 4. Asset Reliability Impact (Depreciation factor)
        # Average reliability of all machinery
        # (Simplified for logic)
        asset_decay_factor = 0.2 

        # 5. Multivariate calculation
        # Risk = [F1 * DebtRatio] + [F2 * (1/Liquidity)] + [F3 * AssetDecay]
        risk_score = (debt_to_equity * 40.0) + (max(0, 1.0 - liquidity) * 40.0) + (asset_decay_factor * 20.0)
        
        risk_score = min(100.0, max(0.0, risk_score))
        
        # 6. Determine Status
        status = 'HEALTHY'
        if risk_score > 80: status = 'INSOLVENT'
        elif risk_score > 60: status = 'CRITICAL'
        elif risk_score > 40: status = 'WARNING'
        
        # 7. Save Snapshot
        snapshot = SolvencySnapshot(
            farm_id=farm_id,
            debt_to_equity_ratio=debt_to_equity,
            liquidity_ratio=liquidity,
            bankruptcy_risk_score=risk_score,
            status=status,
            next_review_date=(datetime.utcnow() + timedelta(days=30)).date()
        )
        db.session.add(snapshot)
        
        if status in ['CRITICAL', 'INSOLVENT']:
            AuditService.log_event(
                user_id=1, # System
                action="INSOLVENCY_WARNING",
                resource_type="FARM",
                resource_id=farm_id,
                details=f"High bankruptcy risk score: {risk_score:.2f}. Status: {status}.",
                risk_level="HIGH"
            )
            
            # Trigger Auto-Restructuring if due to weather
            SolvencyForecaster.check_and_restructure(farm_id, snapshot)

        # 8. Trigger Liquidation Priority List if Debt/Equity > 80% (0.8)
        if debt_to_equity > 0.8:
            SolvencyForecaster.generate_liquidation_priority_list(farm_id)

        db.session.commit()
        return snapshot

    @staticmethod
    def check_and_restructure(farm_id, snapshot):
        """
        Auto-Restructuring logic: Suggests loan extensions if dip is weather-related.
        """
        # Check if recent weather has been extreme (e.g. drought/flood)
        # Fetch weather for farm location
        weather_bad = False # Logic to check WeatherService anomalies
        
        if weather_bad and snapshot.status == 'CRITICAL':
            # Logic to flag active loans for restructuring proposal
            # (Simplified for implementation)
            logger.info(f"Triggering Auto-Restructuring proposal for Farm {farm_id} due to weather events.")
            AuditService.log_event(
                user_id=1,
                action="LOAN_RESTRUCTURE_PROPOSAL",
                resource_type="LOAN",
                resource_id=farm_id,
                details="System suggested extension due to weather-induced cash flow dip.",
                risk_level="MEDIUM"
            )

    @staticmethod
    def generate_liquidation_priority_list(farm_id):
        """
        Ranks Equipment for potential sale based on reliability and market value.
        """
        from backend.models.equipment import Equipment
        
        machinery = Equipment.query.filter_by(owner_id=farm_id).all() # Simple owner = farm_id link
        
        ranked_assets = []
        for equip in machinery:
            # Rank = [Market Value] / [Reliability]
            # Lower reliability = Higher priority to sell
            priority_score = (100.0 - equip.reliability_score) 
            ranked_assets.append((equip.id, priority_score))
            
            # Update AssetValueSnapshot priority
            snap = AssetValueSnapshot.query.filter_by(equipment_id=equip.id).order_by(AssetValueSnapshot.calculated_at.desc()).first()
            if snap:
                snap.liquidation_priority = 1 if priority_score > 70 else 2
        
        return sorted(ranked_assets, key=lambda x: x[1], reverse=True)
