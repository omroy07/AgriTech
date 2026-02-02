"""
Database Migration Script for Asset & Logistics System
Initializes FarmAsset, MaintenanceLog, and LogisticsOrder tables.

Run this after updating models.py to create the new tables.
"""
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extensions import db
from app import create_app
from models import FarmAsset, MaintenanceLog, LogisticsOrder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_assets_logistics_tables():
    """
    Initialize asset and logistics tables in the database.
    Creates FarmAsset, MaintenanceLog, and LogisticsOrder tables.
    """
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            logger.info("Starting asset & logistics database initialization...")
            
            # Create tables if they don't exist
            db.create_all()
            
            logger.info("✓ Database tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['farm_assets', 'maintenance_logs', 'logistics_orders']
            
            for table in required_tables:
                if table in tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.warning(f"⚠ Table '{table}' not found!")
            
            # Optional: Add sample data for testing
            if '--with-samples' in sys.argv:
                logger.info("Adding sample data...")
                add_sample_data()
            
            logger.info("Database initialization complete!")
            return True
            
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        return False


def add_sample_data():
    """
    Add sample assets and logistics orders for testing.
    Only run with --with-samples flag.
    """
    try:
        from datetime import datetime, timedelta
        from models import User
        
        # Find a test user (or use ID 1)
        user = User.query.first()
        
        if not user:
            logger.warning("No users found. Skipping sample data.")
            return
        
        logger.info(f"Adding sample data for user: {user.id}")
        
        # Sample Asset 1: Tractor
        asset1 = FarmAsset(
            asset_id=f"AST-SAMPLE-TRACTOR-001",
            user_id=user.id,
            asset_type="tractor",
            asset_name="John Deere 5075E Sample Tractor",
            manufacturer="John Deere",
            model="5075E",
            serial_number="JD5075E-SAMPLE-001",
            purchase_date=datetime.utcnow() - timedelta(days=730),  # 2 years ago
            purchase_price=45000.00,
            health_score=78.5,
            total_runtime_hours=1850.0,
            last_maintenance_date=datetime.utcnow() - timedelta(days=45),
            next_maintenance_due=datetime.utcnow() + timedelta(days=15),
            status='ACTIVE'
        )
        
        # Sample Asset 2: Pump
        asset2 = FarmAsset(
            asset_id=f"AST-SAMPLE-PUMP-001",
            user_id=user.id,
            asset_type="pump",
            asset_name="Honda Irrigation Pump",
            manufacturer="Honda",
            model="WB30XT",
            serial_number="HONDA-WB30-SAMPLE-001",
            purchase_date=datetime.utcnow() - timedelta(days=365),  # 1 year ago
            purchase_price=15000.00,
            health_score=92.0,
            total_runtime_hours=450.0,
            last_maintenance_date=datetime.utcnow() - timedelta(days=20),
            next_maintenance_due=datetime.utcnow() + timedelta(days=80),
            status='ACTIVE'
        )
        
        db.session.add_all([asset1, asset2])
        db.session.flush()  # Get IDs
        
        # Sample Maintenance Log
        maint_log = MaintenanceLog(
            log_id=f"MAINT-SAMPLE-001",
            asset_id=asset1.id,
            maintenance_type="ROUTINE",
            description="Regular oil change and filter replacement",
            cost=250.00,
            pre_maintenance_health=75.0,
            post_maintenance_health=78.5,
            technician_name="Sample Technician",
            technician_notes="All systems checked. No major issues found.",
            scheduled_date=datetime.utcnow() - timedelta(days=46),
            completed_date=datetime.utcnow() - timedelta(days=45),
            status="COMPLETED"
        )
        
        db.session.add(maint_log)
        
        # Sample Logistics Order 1: Wheat pickup
        order1 = LogisticsOrder(
            order_id=f"LOG-SAMPLE-001",
            user_id=user.id,
            crop_type="wheat",
            quantity_tons=8.5,
            pickup_location="Farm Site A, Village Sample",
            pickup_latitude=28.6139,
            pickup_longitude=77.2090,
            destination_location="Market Hub Delhi Sample",
            destination_latitude=28.7041,
            destination_longitude=77.1025,
            requested_pickup_date=datetime.utcnow() + timedelta(days=2),
            base_cost=2500.00,
            final_cost=2500.00,
            distance_km=45.5,
            status='PENDING',
            priority='NORMAL'
        )
        
        # Sample Logistics Order 2: Rice pickup
        order2 = LogisticsOrder(
            order_id=f"LOG-SAMPLE-002",
            user_id=user.id,
            crop_type="rice",
            quantity_tons=12.0,
            pickup_location="Farm Site B, Village Sample",
            pickup_latitude=28.6200,
            pickup_longitude=77.2150,
            destination_location="Processing Center Sample",
            destination_latitude=28.6500,
            destination_longitude=77.2300,
            requested_pickup_date=datetime.utcnow() + timedelta(days=3),
            base_cost=1800.00,
            final_cost=1800.00,
            distance_km=35.0,
            status='PENDING',
            priority='HIGH'
        )
        
        db.session.add_all([order1, order2])
        db.session.commit()
        
        logger.info("✓ Sample data added successfully!")
        logger.info(f"  - 2 sample assets created")
        logger.info(f"  - 1 sample maintenance log created")
        logger.info(f"  - 2 sample logistics orders created")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding sample data: {str(e)}")


def drop_tables():
    """
    Drop asset and logistics tables (use with caution!).
    Only run with --drop flag.
    """
    try:
        app = create_app()
        
        with app.app_context():
            logger.warning("⚠ Dropping asset & logistics tables...")
            
            # Drop tables
            LogisticsOrder.__table__.drop(db.engine, checkfirst=True)
            MaintenanceLog.__table__.drop(db.engine, checkfirst=True)
            FarmAsset.__table__.drop(db.engine, checkfirst=True)
            
            logger.info("✓ Tables dropped successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Asset & Logistics Database Migration')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables (CAUTION!)')
    parser.add_argument('--with-samples', action='store_true', help='Add sample data for testing')
    
    args = parser.parse_args()
    
    if args.drop:
        confirm = input("⚠ Are you sure you want to drop the tables? This will delete all data! (yes/no): ")
        if confirm.lower() == 'yes':
            if drop_tables():
                logger.info("Proceeding with re-initialization...")
                init_assets_logistics_tables()
        else:
            logger.info("Drop operation cancelled.")
    else:
        init_assets_logistics_tables()
