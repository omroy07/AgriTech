from flask import Blueprint, request, jsonify
from backend.services.livestock_service import LivestockService
from auth_utils import token_required

livestock_bp = Blueprint("livestock", __name__)


@livestock_bp.route("/animals", methods=["POST"])
@token_required
def add_animal(current_user):
    data = request.get_json()
    if not data or "farm_id" not in data or "animal_type" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    data["user_id"] = current_user.id
    animal = LivestockService.add_animal(data)

    return jsonify(
        {
            "status": "success",
            "message": "Animal added successfully",
            "data": animal.to_dict(),
        }
    ), 201


@livestock_bp.route("/animals/<int:farm_id>", methods=["GET"])
@token_required
def get_animals(current_user, farm_id):
    animals = LivestockService.get_farm_animals(farm_id)

    return jsonify({"status": "success", "data": [a.to_dict() for a in animals]})


@livestock_bp.route("/health-record", methods=["POST"])
@token_required
def add_health_record(current_user):
    data = request.get_json()
    if not data or "animal_id" not in data or "health_status" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    record = LivestockService.add_health_record(data)

    return jsonify(
        {
            "status": "success",
            "message": "Health record added successfully",
            "data": record.to_dict(),
        }
    ), 201


@livestock_bp.route("/health-history/<int:animal_id>", methods=["GET"])
@token_required
def get_health_history(current_user, animal_id):
    history = LivestockService.get_animal_health_history(animal_id)

    return jsonify({"status": "success", "data": [r.to_dict() for r in history]})


@livestock_bp.route("/breeding", methods=["POST"])
@token_required
def record_breeding(current_user):
    data = request.get_json()
    if not data or "farm_id" not in data or "breeding_date" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    breeding = LivestockService.record_breeding(data)

    return jsonify(
        {
            "status": "success",
            "message": "Breeding recorded successfully",
            "data": breeding.to_dict(),
        }
    ), 201


@livestock_bp.route("/breeding/<int:farm_id>", methods=["GET"])
@token_required
def get_breeding_records(current_user, farm_id):
    records = LivestockService.get_farm_breeding_records(farm_id)

    return jsonify({"status": "success", "data": [r.to_dict() for r in records]})


@livestock_bp.route("/production", methods=["POST"])
@token_required
def record_production(current_user):
    data = request.get_json()
    if (
        not data
        or "animal_id" not in data
        or "production_type" not in data
        or "amount" not in data
    ):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    production = LivestockService.record_production(data)

    return jsonify(
        {
            "status": "success",
            "message": "Production recorded successfully",
            "data": production.to_dict(),
        }
    ), 201


@livestock_bp.route("/production/<int:animal_id>", methods=["GET"])
@token_required
def get_production(current_user, animal_id):
    production = LivestockService.get_animal_production(animal_id)

    return jsonify({"status": "success", "data": [p.to_dict() for p in production]})


@livestock_bp.route("/feed-plan", methods=["POST"])
@token_required
def create_feed_plan(current_user):
    data = request.get_json()
    if (
        not data
        or "farm_id" not in data
        or "animal_type" not in data
        or "feed_type" not in data
        or "daily_quantity" not in data
    ):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    plan = LivestockService.create_feed_plan(data)

    return jsonify(
        {
            "status": "success",
            "message": "Feed plan created successfully",
            "data": plan.to_dict(),
        }
    ), 201


@livestock_bp.route("/feed-plans/<int:farm_id>", methods=["GET"])
@token_required
def get_feed_plans(current_user, farm_id):
    plans = LivestockService.get_farm_feed_plans(farm_id)

    return jsonify({"status": "success", "data": [p.to_dict() for p in plans]})


@livestock_bp.route("/summary/<int:farm_id>", methods=["GET"])
@token_required
def get_summary(current_user, farm_id):
    summary = LivestockService.get_livestock_summary(farm_id)

    return jsonify({"status": "success", "data": summary})
