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
from .equipment import equipment_bp
from .bookings import bookings_bp
from .farms import farms_bp
from .farm_members import farm_members_bp
from .advisories import advisories_bp
from .sustainability import sustainability_bp
from .credits import credits_bp
from .procurement import procurement_bp
from .vendors import vendors_bp
from .irrigation import irrigation_bp
from .processing import processing_bp
from .insurance_portal import insurance_v2_bp
from .machinery import machinery_bp
from .soil_analysis import soil_bp
from .loan_repayment import loan_repayment_bp
from .warehouse import warehouse_bp
from .climate_control import climate_bp
from .labor_management import labor_bp
from .logistics_portal import logistics_portal_bp
from .audit import audit_bp
from .gews import gews_bp
from .transparency import transparency_bp
from .barter import barter_bp
from .financials import financials_bp
from .futures import futures_bp
from .circular import circular_bp
from .biosecurity import biosecurity_bp
from .vaults import vaults_bp
from .arbitrage import arbitrage_bp
from .spatial_yield import spatial_yield_bp
from .carbon import carbon_bp
from .logistics import smart_freight_bp
from .genomics import genomics_bp
from .virulence import virulence_bp

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
api_v1.register_blueprint(weather_bp)
api_v1.register_blueprint(traceability_bp)
api_v1.register_blueprint(disease_bp)
api_v1.register_blueprint(insurance_bp)
api_v1.register_blueprint(questions_bp, url_prefix='/questions')
api_v1.register_blueprint(answers_bp, url_prefix='/answers')
api_v1.register_blueprint(equipment_bp, url_prefix='/equipment')
api_v1.register_blueprint(bookings_bp, url_prefix='/bookings')
api_v1.register_blueprint(farms_bp, url_prefix='/farms')
api_v1.register_blueprint(farm_members_bp, url_prefix='/farm_teams')
api_v1.register_blueprint(advisories_bp, url_prefix='/advisories')
api_v1.register_blueprint(sustainability_bp, url_prefix='/sustainability')
api_v1.register_blueprint(credits_bp, url_prefix='/credits')
api_v1.register_blueprint(procurement_bp, url_prefix='/procurement')
api_v1.register_blueprint(vendors_bp, url_prefix='/vendors')
api_v1.register_blueprint(irrigation_bp, url_prefix='/irrigation')
api_v1.register_blueprint(processing_bp, url_prefix='/processing')
api_v1.register_blueprint(insurance_v2_bp, url_prefix='/insurance-v2')
api_v1.register_blueprint(machinery_bp, url_prefix='/machinery')
api_v1.register_blueprint(soil_bp, url_prefix='/soil')
api_v1.register_blueprint(loan_repayment_bp, url_prefix='/loans')
api_v1.register_blueprint(warehouse_bp, url_prefix='/warehouse')
api_v1.register_blueprint(climate_bp, url_prefix='/climate')
api_v1.register_blueprint(labor_bp, url_prefix='/labor')
api_v1.register_blueprint(carbon_bp, url_prefix='/carbon')
api_v1.register_blueprint(smart_freight_bp, url_prefix='/freight')
api_v1.register_blueprint(logistics_portal_bp, url_prefix='/logistics-v2')
api_v1.register_blueprint(audit_bp)
api_v1.register_blueprint(gews_bp, url_prefix='/gews')
api_v1.register_blueprint(transparency_bp, url_prefix='/transparency')
api_v1.register_blueprint(barter_bp, url_prefix='/barter')
api_v1.register_blueprint(financials_bp, url_prefix='/financials')
api_v1.register_blueprint(futures_bp, url_prefix='/futures')
api_v1.register_blueprint(circular_bp, url_prefix='/circular')
api_v1.register_blueprint(biosecurity_bp, url_prefix='/biosecurity')
api_v1.register_blueprint(vaults_bp, url_prefix='/vaults')
api_v1.register_blueprint(arbitrage_bp, url_prefix='/arbitrage')
api_v1.register_blueprint(spatial_yield_bp, url_prefix='/spatial-yield')
api_v1.register_blueprint(carbon_bp, url_prefix='/carbon')
api_v1.register_blueprint(genomics_bp, url_prefix='/genomics')
api_v1.register_blueprint(virulence_bp, url_prefix='/virulence')
