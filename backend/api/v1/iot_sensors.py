from flask import Blueprint, request, jsonify
from backend.services.iot_sensor_service import IoTSensorService
from auth_utils import token_required

iot_bp = Blueprint("iot", __name__)


@iot_bp.route("/sensors", methods=["GET"])
@token_required
def get_sensors(current_user):
    sensors = IoTSensorService.get_user_sensors(current_user.id)
    return jsonify({"status": "success", "data": [s.to_dict() for s in sensors]})


@iot_bp.route("/sensors", methods=["POST"])
@token_required
def register_sensor(current_user):
    data = request.get_json()
    if (
        not data
        or "sensor_id" not in data
        or "farm_id" not in data
        or "sensor_type" not in data
        or "location" not in data
    ):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    sensor = IoTSensorService.register_sensor(
        user_id=current_user.id,
        farm_id=data["farm_id"],
        sensor_id=data["sensor_id"],
        sensor_type=data["sensor_type"],
        location=data["location"],
    )

    return jsonify(
        {
            "status": "success",
            "message": "Sensor registered successfully",
            "data": sensor.to_dict(),
        }
    ), 201


@iot_bp.route("/sensors/<int:sensor_id>", methods=["GET"])
@token_required
def get_sensor(current_user, sensor_id):
    sensor = IoTSensorService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({"status": "error", "message": "Sensor not found"}), 404

    if sensor.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    return jsonify({"status": "success", "data": sensor.to_dict()})


@iot_bp.route("/sensors/<int:sensor_id>", methods=["DELETE"])
@token_required
def delete_sensor(current_user, sensor_id):
    sensor = IoTSensorService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({"status": "error", "message": "Sensor not found"}), 404

    if sensor.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    IoTSensorService.delete_sensor(sensor_id)

    return jsonify({"status": "success", "message": "Sensor deleted successfully"})


@iot_bp.route("/sensors/<int:sensor_id>/readings", methods=["POST"])
@token_required
def receive_reading(current_user, sensor_id):
    sensor = IoTSensorService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({"status": "error", "message": "Sensor not found"}), 404

    if sensor.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No reading data provided"}), 400

    reading = IoTSensorService.receive_reading(sensor_id, data)

    return jsonify(
        {"status": "success", "message": "Reading received", "data": reading.to_dict()}
    ), 201


@iot_bp.route("/sensors/<int:sensor_id>/readings", methods=["GET"])
@token_required
def get_readings(current_user, sensor_id):
    sensor = IoTSensorService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({"status": "error", "message": "Sensor not found"}), 404

    if sensor.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    hours = request.args.get("hours", 24, type=int)
    readings = IoTSensorService.get_sensor_readings(sensor_id, hours)

    return jsonify({"status": "success", "data": [r.to_dict() for r in readings]})


@iot_bp.route("/sensors/<int:sensor_id>/history", methods=["GET"])
@token_required
def get_history(current_user, sensor_id):
    sensor = IoTSensorService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({"status": "error", "message": "Sensor not found"}), 404

    if sensor.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    days = request.args.get("days", 7, type=int)
    history = IoTSensorService.get_historical_data(sensor_id, days)

    return jsonify({"status": "success", "data": history})


@iot_bp.route("/alerts", methods=["GET"])
@token_required
def get_alerts(current_user):
    alerts = IoTSensorService.get_user_alerts(current_user.id)
    return jsonify({"status": "success", "data": [a.to_dict() for a in alerts]})


@iot_bp.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
@token_required
def resolve_alert(current_user, alert_id):
    alert = IoTSensorService.resolve_alert(alert_id)
    if not alert:
        return jsonify({"status": "error", "message": "Alert not found"}), 404

    if alert.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Access denied"}), 403

    return jsonify(
        {
            "status": "success",
            "message": "Alert resolved successfully",
            "data": alert.to_dict(),
        }
    )
