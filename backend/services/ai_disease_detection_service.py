import google.generativeai as genai
import os
from backend.extensions import db
from backend.models.disease import DiseaseIncident
from datetime import datetime
import logging
import base64

logger = logging.getLogger(__name__)


class AIDiseaseDetectionService:
    DISEASE_DATABASE = {
        "Tomato": {
            "Late Blight": {
                "symptoms": "Water-soaked lesions on leaves, brown spots, white mold on underside",
                "treatment": "Apply copper-based fungicides, remove infected leaves, improve air circulation",
                "severity": "HIGH",
            },
            "Early Blight": {
                "symptoms": "Dark brown circular spots with concentric rings on lower leaves",
                "treatment": "Use fungicides containing chlorothalonil or copper, crop rotation",
                "severity": "MEDIUM",
            },
            "Septoria Leaf Spot": {
                "symptoms": "Small circular spots with dark borders and gray centers on leaves",
                "treatment": "Apply fungicides, remove affected leaves, avoid overhead irrigation",
                "severity": "MEDIUM",
            },
            "Bacterial Spot": {
                "symptoms": "Small water-soaked spots on leaves, stems, and fruits",
                "treatment": "Use copper bactericides, avoid working with wet plants",
                "severity": "HIGH",
            },
        },
        "Wheat": {
            "Rust": {
                "symptoms": "Orange-brown pustules on leaves and stems",
                "treatment": "Apply fungicides, use resistant varieties, crop rotation",
                "severity": "HIGH",
            },
            "Powdery Mildew": {
                "symptoms": "White powdery growth on leaves and stems",
                "treatment": "Apply sulfur or fungicides, improve air circulation",
                "severity": "MEDIUM",
            },
        },
        "Rice": {
            "Blast": {
                "symptoms": "Diamond-shaped lesions on leaves, neck rot",
                "treatment": "Use fungicides like tricyclazole, resistant varieties, proper water management",
                "severity": "HIGH",
            },
            "Bacterial Leaf Blight": {
                "symptoms": "Yellowing along leaf margins, drying of leaves",
                "treatment": "Use resistant varieties, balanced fertilization, avoid excess nitrogen",
                "severity": "HIGH",
            },
        },
        "Cotton": {
            "Verticillium Wilt": {
                "symptoms": "Yellowing and wilting of leaves, vascular discoloration",
                "treatment": "Use resistant varieties, soil solarization, crop rotation",
                "severity": "HIGH",
            },
            "Boll Rot": {
                "symptoms": "Rotting of cotton bolls, wet spots",
                "treatment": "Use fungicides, improve drainage, avoid overhead irrigation",
                "severity": "HIGH",
            },
        },
        "Maize": {
            "Northern Corn Leaf Blight": {
                "symptoms": "Long gray-green lesions on leaves",
                "treatment": "Apply fungicides, use resistant hybrids, crop rotation",
                "severity": "MEDIUM",
            },
            "Gray Leaf Spot": {
                "symptoms": "Rectangular gray lesions on leaves",
                "treatment": "Apply fungicides, crop rotation, residue management",
                "severity": "MEDIUM",
            },
        },
    }

    @staticmethod
    def analyze_crop_image(image_base64, crop_type):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {
                "error": "AI Service not configured",
                "message": "Please configure GEMINI_API_KEY",
            }

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
            Analyze this {crop_type} plant image for diseases.
            
            Identify:
            1. Disease name (if any)
            2. Symptoms observed
            3. Severity level (LOW, MEDIUM, HIGH)
            4. Affected plant parts
            5. Confidence level (0-100%)
            
            If healthy, state "No disease detected".
            
            Provide response in this exact JSON format:
            {{
                "disease_name": "Disease Name or Healthy",
                "symptoms": "description of symptoms",
                "severity": "LOW/MEDIUM/HIGH",
                "affected_parts": ["leaves", "stems"],
                "confidence": 85,
                "is_healthy": false
            }}
            """

            image_data = {"mime_type": "image/jpeg", "data": image_base64}

            response = model.generate_content([prompt, image_data])

            import re

            json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if json_match:
                import json

                diagnosis = json.loads(json_match.group())
                diagnosis = AIDiseaseDetectionService.enhance_diagnosis(
                    diagnosis, crop_type
                )
                return diagnosis
            else:
                return {
                    "error": "Failed to parse AI response",
                    "raw_response": response.text,
                }

        except Exception as e:
            logger.error(f"AI disease detection error: {str(e)}")
            return {"error": "AI analysis failed", "message": str(e)}

    @staticmethod
    def enhance_diagnosis(diagnosis, crop_type):
        if diagnosis.get("is_healthy", False):
            diagnosis["treatment"] = "No treatment needed. Continue regular care."
            diagnosis["recommendation"] = "Monitor plant health regularly."
            return diagnosis

        disease_name = diagnosis.get("disease_name", "Unknown")
        crop_diseases = AIDiseaseDetectionService.DISEASE_DATABASE.get(crop_type, {})

        for disease, info in crop_diseases.items():
            if (
                disease_name.lower() in disease.lower()
                or disease.lower() in disease_name.lower()
            ):
                diagnosis["symptoms"] = info["symptoms"]
                diagnosis["treatment"] = info["treatment"]
                diagnosis["severity"] = info["severity"]
                diagnosis["database_match"] = True
                break

        if "treatment" not in diagnosis:
            diagnosis["treatment"] = (
                "Consult agricultural expert for specific treatment recommendations."
            )
            diagnosis["recommendation"] = "Isolate affected plants and prevent spread."

        if "recommendation" not in diagnosis:
            if diagnosis.get("severity") == "HIGH":
                diagnosis["recommendation"] = (
                    "Immediate action required. Consider contacting agricultural extension services."
                )
            elif diagnosis.get("severity") == "MEDIUM":
                diagnosis["recommendation"] = (
                    "Monitor closely and apply treatment as soon as possible."
                )
            else:
                diagnosis["recommendation"] = (
                    "Apply preventive measures and monitor plant health."
                )

        return diagnosis

    @staticmethod
    def save_diagnosis(user_id, crop_type, diagnosis, image_base64=None, location=None):
        incident = DiseaseIncident(
            incident_id=f"AI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            user_id=user_id,
            disease_name=diagnosis.get("disease_name", "Unknown"),
            crop_affected=crop_type,
            severity_level=diagnosis.get("severity", "MEDIUM"),
            symptoms=diagnosis.get("symptoms", ""),
            latitude=location.get("latitude") if location else None,
            longitude=location.get("longitude") if location else None,
            detection_method="ai_image",
            verification_status="pending",
            images=[image_base64] if image_base64 else [],
            reported_at=datetime.utcnow(),
        )

        db.session.add(incident)
        db.session.commit()

        return incident

    @staticmethod
    def get_disease_history(user_id, crop_type=None, days=30):
        threshold = datetime.utcnow() - timedelta(days=days)
        query = DiseaseIncident.query.filter(
            DiseaseIncident.user_id == user_id, DiseaseIncident.reported_at >= threshold
        )

        if crop_type:
            query = query.filter_by(crop_affected=crop_type)

        return query.order_by(DiseaseIncident.reported_at.desc()).all()

    @staticmethod
    def get_treatment_recommendation(crop_type, disease_name):
        crop_diseases = AIDiseaseDetectionService.DISEASE_DATABASE.get(crop_type, {})

        for disease, info in crop_diseases.items():
            if (
                disease_name.lower() in disease.lower()
                or disease.lower() in disease_name.lower()
            ):
                return {
                    "disease": disease,
                    "treatment": info["treatment"],
                    "symptoms": info["symptoms"],
                    "severity": info["severity"],
                }

        return {
            "disease": disease_name,
            "treatment": "Consult agricultural expert for specific treatment recommendations.",
            "symptoms": "Not available in database",
            "severity": "UNKNOWN",
        }


from datetime import timedelta
