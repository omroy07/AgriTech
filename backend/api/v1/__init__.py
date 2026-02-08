from flask import Blueprint
from .loan import loan_bp
from .config import config_bp
from .tasks import tasks_bp
from .notifications import notifications_bp
from .assets import assets_bp
from .logistics import logistics_bp
from .forum import forum_bp
from .pools import pools_bp
from .contributions import contributions_bp
from .market import market_bp
from .risk import risk_bp
from .schemes import schemes_bp
from .weather import weather_bp
from .traceability import traceability_bp
from .disease import disease_bp
from .insurance import insurance_bp
from .questions import questions_bp
from .answers import answers_bp

# Create v1 API blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
api_v1.register_blueprint(loan_bp)
api_v1.register_blueprint(config_bp)
api_v1.register_blueprint(tasks_bp)
api_v1.register_blueprint(notifications_bp)
api_v1.register_blueprint(assets_bp)
api_v1.register_blueprint(logistics_bp)
api_v1.register_blueprint(forum_bp)
api_v1.register_blueprint(pools_bp)
api_v1.register_blueprint(contributions_bp)
api_v1.register_blueprint(market_bp)
api_v1.register_blueprint(risk_bp)
api_v1.register_blueprint(schemes_bp)
api_v1.register_blueprint(weather_bp) # Weather endpoints relocated/updated
api_v1.register_blueprint(traceability_bp)
api_v1.register_blueprint(disease_bp)
api_v1.register_blueprint(insurance_bp)
api_v1.register_blueprint(questions_bp, url_prefix='/questions')
api_v1.register_blueprint(answers_bp, url_prefix='/answers')
