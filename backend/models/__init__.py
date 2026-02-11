"""
Database models package.
"""
from .user import User, UserRole
from .loan_request import LoanRequest
from .prediction_history import PredictionHistory
from .misc import Notification, File, YieldPool, PoolContribution, ResourceShare, PoolVote
from .gews import DiseaseIncident, OutbreakZone, OutbreakAlert
from .traceability import SupplyBatch, CustodyLog, QualityGrade, BatchStatus
from .insurance import InsurancePolicy, ClaimRequest as LegacyClaim, RiskScoreHistory
from .forum import ForumCategory, ForumThread, PostComment, Upvote, UserReputation
from .knowledge import Question, Answer, KnowledgeVote, Badge, UserBadge, UserExpertise
from .equipment import Equipment, RentalBooking, AvailabilityCalendar, PaymentEscrow
from .farm import Farm, FarmMember, FarmAsset, FarmRole
from .weather import WeatherData, CropAdvisory, AdvisorySubscription
from .sustainability import CarbonPractice, CreditLedger, AuditRequest
from .vendor_profile import VendorProfile
from .procurement import ProcurementItem, BulkOrder, OrderEvent
from .irrigation import IrrigationZone, SensorLog, ValveStatus, IrrigationSchedule
from .processing import ProcessingBatch, StageLog, QualityCheck, ProcessingStage
from .insurance_v2 import CropPolicy, ClaimRequest, PayoutLedger, AdjusterNote
from .machinery import EngineHourLog, MaintenanceCycle, DamageReport, RepairOrder
from .soil_health import SoilTest, FertilizerRecommendation, ApplicationLog
from .loan_v2 import RepaymentSchedule, PaymentHistory, DefaultRiskScore, CollectionNote
from .warehouse import WarehouseLocation, StockItem, StockMovement, ReconciliationLog
from .climate import ClimateZone, SensorNode, TelemetryLog, AutomationTrigger

__all__ = [
    'User', 'UserRole', 'LoanRequest', 'PredictionHistory', 
    'Notification', 'File', 'YieldPool', 'PoolContribution', 
    'ResourceShare', 'PoolVote', 'DiseaseIncident', 'OutbreakZone', 'OutbreakAlert',
    'SupplyBatch', 'CustodyLog', 'QualityGrade', 'BatchStatus',
    'InsurancePolicy', 'LegacyClaim', 'RiskScoreHistory',
    'ForumCategory', 'ForumThread', 'PostComment', 'Upvote', 'UserReputation',
    'Question', 'Answer', 'KnowledgeVote', 'Badge', 'UserBadge', 'UserExpertise',
    'Equipment', 'RentalBooking', 'AvailabilityCalendar', 'PaymentEscrow',
    'Farm', 'FarmMember', 'FarmAsset', 'FarmRole',
    'WeatherData', 'CropAdvisory', 'AdvisorySubscription',
    'CarbonPractice', 'CreditLedger', 'AuditRequest',
    'VendorProfile', 'ProcurementItem', 'BulkOrder', 'OrderEvent',
    'IrrigationZone', 'SensorLog', 'ValveStatus', 'IrrigationSchedule',
    'ProcessingBatch', 'StageLog', 'QualityCheck', 'ProcessingStage',
    'CropPolicy', 'ClaimRequest', 'PayoutLedger', 'AdjusterNote',
    'EngineHourLog', 'MaintenanceCycle', 'DamageReport', 'RepairOrder',
    'SoilTest', 'FertilizerRecommendation', 'ApplicationLog',
    'RepaymentSchedule', 'PaymentHistory', 'DefaultRiskScore', 'CollectionNote',
    'WarehouseLocation', 'StockItem', 'StockMovement', 'ReconciliationLog',
    'ClimateZone', 'SensorNode', 'TelemetryLog', 'AutomationTrigger'
]
