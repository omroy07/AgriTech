from backend.extensions import db
from backend.models.farm import Farm, FarmMember, FarmAsset, FarmRole
import json
import logging

logger = logging.getLogger(__name__)

class FarmService:
    @staticmethod
    def create_farm(user_id, name, location, acreage=0, description=None, soil_details=None):
        """Register a new farm and assign the creator as the Owner"""
        try:
            farm = Farm(
                name=name,
                location=location,
                acreage=acreage,
                description=description,
                soil_details=json.dumps(soil_details or {})
            )
            db.session.add(farm)
            db.session.flush() # Get farm ID
            
            # Make the creator the owner
            membership = FarmMember(
                farm_id=farm.id,
                user_id=user_id,
                role=FarmRole.OWNER.value
            )
            db.session.add(membership)
            db.session.commit()
            return farm, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create farm: {str(e)}")
            return None, str(e)

    @staticmethod
    def add_member(farm_id, user_id, role, invited_by_id):
        """Add a team member to a farm with a specific role"""
        try:
            # Check if already a member
            existing = FarmMember.query.filter_by(farm_id=farm_id, user_id=user_id).first()
            if existing:
                return None, "User is already a member of this farm"
                
            member = FarmMember(
                farm_id=farm_id,
                user_id=user_id,
                role=role,
                invited_by_id=invited_by_id
            )
            db.session.add(member)
            db.session.commit()
            return member, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_user_farms(user_id):
        """Retrieve all farms a user belongs to"""
        return Farm.query.join(FarmMember).filter(FarmMember.user_id == user_id).all()

    @staticmethod
    def add_asset(farm_id, name, category, purchase_value=0, purchase_date=None):
        """Register a new asset/equipment under a farm"""
        try:
            asset = FarmAsset(
                farm_id=farm_id,
                name=name,
                category=category,
                purchase_value=purchase_value,
                purchase_date=purchase_date,
                current_valuation=purchase_value # Initially same as purchase
            )
            db.session.add(asset)
            db.session.commit()
            return asset, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_asset_condition(asset_id, new_condition):
        """Update maintenance status of an asset"""
        asset = FarmAsset.query.get(asset_id)
        if asset:
            asset.condition = new_condition
            asset.last_maintenance = db.func.now()
            db.session.commit()
            return True
        return False
