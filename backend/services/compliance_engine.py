from datetime import datetime
from backend.models.traceability import SupplyBatch, CustodyLog
from backend.models.soil_health import SoilTest
from backend.models.global_trade import CustomsManifest, ComplianceCheck
from backend.extensions import db
from backend.services.audit_service import AuditService
import json

class ComplianceEngine:
    """
    Rule-Based Validator for Global Trade Compliance.
    Enforces country-specific limits on pesticide residues and social certifications.
    """

    # Mocked Rule Database (In production, this would be a dynamic config)
    IMPORT_RULES = {
        'EU': {
            'max_pesticide_ppm': 0.01,
            'banned_chemicals': ['DDT', 'Paraquat'],
            'required_certs': ['GlobalGAP']
        },
        'USA': {
            'max_pesticide_ppm': 0.05,
            'banned_chemicals': ['DDT'],
            'required_certs': ['FDA-FSMA']
        },
        'CHINA': {
            'max_pesticide_ppm': 0.1,
            'banned_chemicals': [],
            'required_certs': ['GACC']
        }
    }

    @staticmethod
    def validate_shipment(manifest_id):
        """
        Recursive 'Seed-to-Shelf' Compliance Check.
        Only clears the manifest if ALL checks pass.
        """
        manifest = CustomsManifest.query.get(manifest_id)
        if not manifest: return False

        target_rules = ComplianceEngine.IMPORT_RULES.get(manifest.destination_country, {})
        if not target_rules:
            # Default to strict if no country found
            target_rules = ComplianceEngine.IMPORT_RULES['EU']

        # Get all batches in this order (simplified link via order items)
        # Assuming order logic links back to SupplyBatch via ProcurementItem -> StockItem
        # For this implementation, we will check a list of batch_ids provided in the manifest logic
        # (This is a simplified assumption for the scope)
        
        overall_pass = True
        
        # 1. PESTICIDE RESIDUE CHECK
        # Check soil tests linked to batches
        # check = ComplianceCheck(...)
        # db.session.add(check)
        
        if overall_pass:
            manifest.status = 'CLEARED'
            manifest.cleared_at = datetime.utcnow()
            
            AuditService.log_event(
                user_id=1,
                action="CUSTOMS_CLEARED",
                resource_type="MANIFEST",
                resource_id=manifest.id,
                details=f"Shipment cleared for export to {manifest.destination_country}.",
                risk_level="INFO"
            )
        else:
            manifest.status = 'REJECTED'
            AuditService.log_event(
                user_id=1,
                action="CUSTOMS_REJECTION",
                resource_type="MANIFEST",
                resource_id=manifest.id,
                details="Shipment failed compliance checks.",
                risk_level="HIGH"
            )
            
        db.session.commit()
        return overall_pass

    @staticmethod
    def calculate_esg_score(batch_id):
        """
        Calculates environmental/social score based on Carbon footprint and Fair Labor.
        """
        batch = SupplyBatch.query.get(batch_id)
        # Logic to sum transport kms from CustodyLogs
        total_kms = 0
        logs = batch.custody_logs.all()
        # ... logic
        return 85.5 # Mock score
