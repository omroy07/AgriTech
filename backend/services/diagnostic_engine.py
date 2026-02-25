"""
AI Diagnostic Service — L3-1643
==============================
Simulates a computer vision pipeline for identifying crop diseases.
"""

from datetime import datetime
import random
from backend.extensions import db
from backend.models.ai_diagnostics import CropDiagnosticReport
import logging

logger = logging.getLogger(__name__)

# Simulated Pathogen Knowledge Base
PATHOGEN_DATABASE = {
    "RICE_BLAST": {
        "treatment": "Apply Fungicide (Tricyclazole 75% WP). Improve water management.",
        "yield_loss_risk": 0.35
    },
    "BACTERIAL_BLIGHT": {
        "treatment": "Spray Streptocycline (1g in 10L water). Avoid nitrogen overdose.",
        "yield_loss_risk": 0.25
    },
    "BROWN_PLANTHOPPER": {
        "treatment": "Apply Pemetrozine 50% WG. Ensure early detection.",
        "yield_loss_risk": 0.60
    }
}

class DiagnosticEngine:
    
    @staticmethod
    def process_image(user_id: int, farm_id: int, image_url: str):
        """
        Simulates AI inference on a plant leaf image.
        """
        # Randomly select a pathogen for simulation
        pathogen_key = random.choice(list(PATHOGEN_DATABASE.keys()))
        info = PATHOGEN_DATABASE[pathogen_key]
        
        confidence = random.uniform(0.72, 0.98)
        severity = random.uniform(0.1, 0.8)
        
        report = CropDiagnosticReport(
            user_id=user_id,
            farm_id=farm_id,
            image_url=image_url,
            identified_pathogen=pathogen_key,
            confidence_score=confidence,
            severity_index=severity,
            recommended_treatment=info['treatment'],
            estimated_yield_loss_pct=info['yield_loss_risk'] * severity,
            status='PENDING'
        )
        db.session.add(report)
        db.session.commit()
        
        logger.info(f"AI Diagnostic complete for user {user_id}. Detected: {pathogen_key} ({confidence*100:.1f}%)")
        return report

    @staticmethod
    def resolve_report(report_id: int, resolution: str):
        """
        Marks a diagnostic report as actioned.
        """
        report = CropDiagnosticReport.query.get(report_id)
        if report:
            report.status = 'RESOLVED'
            db.session.commit()
            return True
        return False
