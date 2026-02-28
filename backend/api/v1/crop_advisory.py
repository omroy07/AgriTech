from flask import Blueprint, request, jsonify
from backend.services.crop_advisory_service import CropAdvisoryService
from backend.services.weather_service import WeatherService
from auth_utils import token_required

advisory_bp = Blueprint("crop_advisory", __name__)


@advisory_bp.route("/recommendations", methods=["GET"])
@token_required
def get_recommendations(current_user):
    location = request.args.get("location")
    soil_type = request.args.get("soil_type")

    if not location:
        return jsonify({"status": "error", "message": "Location required"}), 400

    recommendations = CropAdvisoryService.get_crop_recommendations(location, soil_type)

    return jsonify({"status": "success", "data": recommendations})


@advisory_bp.route("/alerts", methods=["GET"])
@token_required
def get_advisory_alerts(current_user):
    alerts = CropAdvisoryService.get_planting_alerts(current_user.id)

    return jsonify({"status": "success", "data": alerts})


@advisory_bp.route("/climate-analysis", methods=["GET"])
@token_required
def get_climate_analysis(current_user):
    location = request.args.get("location")
    days = request.args.get("days", 30, type=int)

    if not location:
        return jsonify({"status": "error", "message": "Location required"}), 400

    analysis = CropAdvisoryService.analyze_climate_patterns(location, days)

    return jsonify({"status": "success", "data": analysis})


@advisory_bp.route("/seasonal-plan", methods=["GET"])
@token_required
def get_seasonal_plan(current_user):
    location = request.args.get("location")
    crop_name = request.args.get("crop_name")

    if not location or not crop_name:
        return jsonify(
            {"status": "error", "message": "Location and crop_name required"}
        ), 400

    plan = CropAdvisoryService.get_seasonal_plan(location, crop_name)

    return jsonify({"status": "success", "data": plan})


@advisory_bp.route("/subscribe", methods=["POST"])
@token_required
def subscribe_advisory(current_user):
    data = request.get_json()
    if not data or "crop_name" not in data or "location" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    sub = WeatherService.subscribe_user(
        user_id=current_user.id,
        crop_name=data["crop_name"],
        location=data["location"],
        soil_type=data.get("soil_type"),
        sowing_date=data.get("sowing_date"),
    )

    return jsonify(
        {
            "status": "success",
            "message": "Subscribed to crop advisories",
            "data": sub.to_dict(),
        }
    ), 201
