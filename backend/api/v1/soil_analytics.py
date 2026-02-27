from flask import Blueprint, request, jsonify
from backend.services.soil_analytics_service import SoilAnalyticsService
from auth_utils import token_required

soil_analytics_bp = Blueprint("soil_analytics", __name__)


@soil_analytics_bp.route("/health-score/<int:farm_id>", methods=["GET"])
@token_required
def get_health_score(current_user, farm_id):
    from backend.models.soil_health import SoilTest

    latest_test = (
        SoilTest.query.filter_by(farm_id=farm_id)
        .order_by(SoilTest.test_date.desc())
        .first()
    )

    if not latest_test:
        return jsonify(
            {"status": "error", "message": "No soil test data available"}
        ), 404

    health_score = SoilAnalyticsService.calculate_soil_health_score(latest_test)

    return jsonify({"status": "success", "data": health_score})


@soil_analytics_bp.route("/trends/<int:farm_id>", methods=["GET"])
@token_required
def get_trends(current_user, farm_id):
    years = request.args.get("years", 3, type=int)

    trends = SoilAnalyticsService.get_soil_health_trends(farm_id, years)

    return jsonify({"status": "success", "data": trends})


@soil_analytics_bp.route("/comparison/<int:farm_id>", methods=["GET"])
@token_required
def get_comparison(current_user, farm_id):
    comparison = SoilAnalyticsService.get_nutrient_comparison(farm_id)

    if "error" in comparison:
        return jsonify({"status": "error", "message": comparison["error"]}), 404

    return jsonify({"status": "success", "data": comparison})


@soil_analytics_bp.route("/report/<int:farm_id>", methods=["GET"])
@token_required
def get_comprehensive_report(current_user, farm_id):
    report = SoilAnalyticsService.generate_comprehensive_report(farm_id)

    if "error" in report:
        return jsonify({"status": "error", "message": report["error"]}), 404

    return jsonify({"status": "success", "data": report})


@soil_analytics_bp.route("/summary/<int:farm_id>", methods=["GET"])
@token_required
def get_quality_summary(current_user, farm_id):
    summary = SoilAnalyticsService.get_soil_quality_summary(farm_id)

    if "error" in summary:
        return jsonify({"status": "error", "message": summary["error"]}), 404

    return jsonify({"status": "success", "data": summary})
