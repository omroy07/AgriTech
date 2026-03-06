from flask import Blueprint, request, jsonify
from backend.services.ai_disease_detection_service import AIDiseaseDetectionService
from auth_utils import token_required

ai_disease_bp = Blueprint("ai_disease", __name__)


@ai_disease_bp.route("/analyze", methods=["POST"])
@token_required
def analyze_image(current_user):
    data = request.get_json()
    if not data or "image" not in data or "crop_type" not in data:
        return jsonify(
            {
                "status": "error",
                "message": "Missing required fields: image and crop_type",
            }
        ), 400

    diagnosis = AIDiseaseDetectionService.analyze_crop_image(
        data["image"], data["crop_type"]
    )

    if "error" in diagnosis:
        return jsonify({"status": "error", "message": diagnosis["error"]}), 500

    location = {"latitude": data.get("latitude"), "longitude": data.get("longitude")}

    incident = AIDiseaseDetectionService.save_diagnosis(
        user_id=current_user.id,
        crop_type=data["crop_type"],
        diagnosis=diagnosis,
        image_base64=data["image"],
        location=location,
    )

    return jsonify(
        {
            "status": "success",
            "diagnosis": diagnosis,
            "incident_id": incident.incident_id,
        }
    )


@ai_disease_bp.route("/history", methods=["GET"])
@token_required
def get_history(current_user):
    crop_type = request.args.get("crop_type")
    days = request.args.get("days", 30, type=int)

    incidents = AIDiseaseDetectionService.get_disease_history(
        user_id=current_user.id, crop_type=crop_type, days=days
    )

    return jsonify({"status": "success", "data": [i.to_dict() for i in incidents]})


@ai_disease_bp.route("/treatment", methods=["GET"])
def get_treatment():
    crop_type = request.args.get("crop_type")
    disease_name = request.args.get("disease_name")

    if not crop_type or not disease_name:
        return jsonify(
            {"status": "error", "message": "crop_type and disease_name required"}
        ), 400

    treatment = AIDiseaseDetectionService.get_treatment_recommendation(
        crop_type, disease_name
    )

    return jsonify({"status": "success", "data": treatment})
