from flask import Blueprint, request, jsonify
from backend.services.government_scheme_service import government_scheme_service
from backend.models.government_schemes import GovernmentScheme, SchemeApplication
from backend.extensions import db
from datetime import datetime

gov_schemes_bp = Blueprint("gov_schemes", __name__)


@gov_schemes_bp.route("/government-schemes", methods=["GET"])
def get_schemes():
    filters = {
        "ministry": request.args.get("ministry"),
        "region": request.args.get("region"),
        "deadline_from": datetime.strptime(
            request.args.get("deadline_from"), "%Y-%m-%d"
        ).date()
        if request.args.get("deadline_from")
        else None,
        "deadline_to": datetime.strptime(
            request.args.get("deadline_to"), "%Y-%m-%d"
        ).date()
        if request.args.get("deadline_to")
        else None,
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    schemes = government_scheme_service.get_all_schemes(filters)

    return jsonify({"status": "success", "count": len(schemes), "data": schemes}), 200


@gov_schemes_bp.route("/government-schemes/search", methods=["GET"])
def search_schemes():
    keyword = request.args.get("q", "")
    if not keyword:
        return jsonify({"status": "error", "message": "Search keyword required"}), 400

    schemes = government_scheme_service.search_schemes(keyword)

    return jsonify({"status": "success", "count": len(schemes), "data": schemes}), 200


@gov_schemes_bp.route("/government-schemes/<int:scheme_id>", methods=["GET"])
def get_scheme(scheme_id):
    scheme = government_scheme_service.get_scheme_by_id(scheme_id)

    if not scheme:
        return jsonify({"status": "error", "message": "Scheme not found"}), 404

    return jsonify({"status": "success", "data": scheme}), 200


@gov_schemes_bp.route(
    "/government-schemes/<int:scheme_id>/eligibility", methods=["POST"]
)
def check_eligibility(scheme_id):
    data = request.get_json()
    user_id = data.get("user_id")
    farm_id = data.get("farm_id")

    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400

    eligibility = government_scheme_service.check_eligibility(
        scheme_id, user_id, farm_id
    )

    return jsonify({"status": "success", "data": eligibility}), 200


@gov_schemes_bp.route("/government-schemes/<int:scheme_id>/assistance", methods=["GET"])
def get_assistance(scheme_id):
    assistance = government_scheme_service.get_application_assistance(scheme_id)

    if not assistance:
        return jsonify({"status": "error", "message": "Scheme not found"}), 404

    return jsonify({"status": "success", "data": assistance}), 200


@gov_schemes_bp.route("/government-schemes/applications", methods=["POST"])
def create_application():
    data = request.get_json()
    scheme_id = data.get("scheme_id")
    user_id = data.get("user_id")
    farm_id = data.get("farm_id")
    application_data = data.get("application_data")

    if not scheme_id or not user_id:
        return jsonify(
            {"status": "error", "message": "Scheme ID and User ID required"}
        ), 400

    result = government_scheme_service.create_application(
        scheme_id, user_id, farm_id, application_data
    )

    if result.get("success"):
        return jsonify({"status": "success", "data": result}), 201
    else:
        return jsonify({"status": "error", "message": result.get("message")}), 400


@gov_schemes_bp.route(
    "/government-schemes/applications/<int:application_id>/submit", methods=["POST"]
)
def submit_application(application_id):
    result = government_scheme_service.submit_application(application_id)

    if result.get("success"):
        return jsonify({"status": "success", "message": result.get("message")}), 200
    else:
        return jsonify({"status": "error", "message": result.get("message")}), 400


@gov_schemes_bp.route(
    "/government-schemes/applications/user/<int:user_id>", methods=["GET"]
)
def get_user_applications(user_id):
    status = request.args.get("status")

    applications = government_scheme_service.get_user_applications(user_id, status)

    return jsonify(
        {"status": "success", "count": len(applications), "data": applications}
    ), 200


@gov_schemes_bp.route(
    "/government-schemes/applications/<int:application_id>", methods=["GET"]
)
def get_application(application_id):
    application = SchemeApplication.query.get(application_id)

    if not application:
        return jsonify({"status": "error", "message": "Application not found"}), 404

    return jsonify({"status": "success", "data": application.to_dict()}), 200


@gov_schemes_bp.route("/government-schemes/deadlines", methods=["GET"])
def get_upcoming_deadlines():
    days = request.args.get("days", 30, type=int)

    schemes = government_scheme_service.get_upcoming_deadlines(days)

    return jsonify({"status": "success", "count": len(schemes), "data": schemes}), 200


@gov_schemes_bp.route("/government-schemes/<int:scheme_id>/reminders", methods=["POST"])
def create_reminders(scheme_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "User ID required"}), 400

    reminders = government_scheme_service.create_deadline_reminders(scheme_id, user_id)

    return jsonify(
        {
            "status": "success",
            "count": len(reminders),
            "message": f"Created {len(reminders)} deadline reminders",
        }
    ), 201
