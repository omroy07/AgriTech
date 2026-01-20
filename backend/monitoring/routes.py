from flask import Blueprint, jsonify, Response
from backend.monitoring import health_checker, metrics

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def liveness():
    """
    Liveness probe endpoint.
    Used by Kubernetes/Docker to check if the app is running.
    Always returns 200 if the server can respond.
    """
    result = health_checker.liveness_check()
    return jsonify(result), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness():
    """
    Readiness probe endpoint.
    Used by Kubernetes/Docker to check if the app is ready to receive traffic.
    Checks all dependencies (Redis, API keys, ML models).
    """
    result = health_checker.readiness_check()
    
    status_code = 200
    if result['status'] == 'unhealthy':
        status_code = 503  # Service Unavailable
    elif result['status'] == 'degraded':
        status_code = 200  # Still accept traffic but with degraded service
    
    return jsonify(result), status_code


@health_bp.route('/health/live', methods=['GET'])
def live():
    """Alias for liveness check."""
    return liveness()


@health_bp.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    metrics_output = metrics.to_prometheus()
    return Response(metrics_output, mimetype='text/plain')


@health_bp.route('/health/details', methods=['GET'])
def health_details():
    """
    Detailed health check with all component statuses.
    Useful for debugging and dashboards.
    """
    result = health_checker.readiness_check()
    result['version'] = '1.0.0'
    result['environment'] = 'development'
    
    return jsonify(result), 200
