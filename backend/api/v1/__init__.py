from flask import Blueprint
from .loan import loan_bp
from .config import config_bp
from .tasks import tasks_bp
from .notifications import notifications_bp
from .assets import assets_bp
from .logistics import logistics_bp

# Create v1 API blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
api_v1.register_blueprint(loan_bp)
api_v1.register_blueprint(config_bp)
api_v1.register_blueprint(tasks_bp)
api_v1.register_blueprint(notifications_bp)
api_v1.register_blueprint(assets_bp)
api_v1.register_blueprint(logistics_bp)

