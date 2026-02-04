from flask import Blueprint
from .loan import loan_bp
from .config import config_bp
from .tasks import tasks_bp
from .notifications import notifications_bp
from .pools import pools_bp
from .contributions import contributions_bp
from .equipment import equipment_bp
from .bookings import bookings_bp

# Create v1 API blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
api_v1.register_blueprint(loan_bp)
api_v1.register_blueprint(config_bp)
api_v1.register_blueprint(tasks_bp)
api_v1.register_blueprint(notifications_bp)
api_v1.register_blueprint(pools_bp)
api_v1.register_blueprint(contributions_bp)
api_v1.register_blueprint(equipment_bp, url_prefix='/equipment')
api_v1.register_blueprint(bookings_bp, url_prefix='/bookings')
