"""
Database migration script for Geospatial Early Warning System (GEWS) feature.
Run this script to create the necessary database tables for disease outbreak tracking.
"""

from flask import Flask
from backend.extensions import db
from backend.models import User, DiseaseIncident, OutbreakZone, OutbreakAlert
from datetime import datetime
import os
import sys

def init_app():
    """Initialize Flask app with database configuration"""
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///agritech.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app


def create_tables():
    """Create all GEWS database tables"""
    app = init_app()
    
    with app.app_context():
        print("="*60)
        print("Geospatial Early Warning System (GEWS) - Database Migration")
        print("="*60)
        print("\nCreating GEWS database tables...")
        
        # Create all tables
        db.create_all()
        
        print("\n✓ Tables created successfully!")
        print("\nCreated/Updated tables:")
        print("  - users (added geospatial fields)")
        print("    * farm_latitude, farm_longitude")
        print("    * farm_location (PostGIS POINT geometry)")
        print("    * farm_address")
        print("  - disease_incidents (new)")
        print("  - outbreak_zones (new)")
        print("  - outbreak_alerts (new)")
        
        # Display index information
        print("\nCreated spatial indexes:")
        print("  - idx_incident_location (GIST index on disease_incidents)")
        print("  - idx_user_farm_location (GIST index on users)")
        print("  - idx_outbreak_zone_location (GIST index on outbreak_zones)")
        
        print("\n" + "="*60)
        print("✓ GEWS Database migration completed successfully!")
        print("="*60)
        
        print("\nNext steps:")
        print("  1. Configure Celery beat schedule for outbreak detection")
        print("  2. Set up GEMINI_API_KEY for AI-powered reports")
        print("  3. Enable PostGIS extension if using PostgreSQL")
        print("  4. Update user profiles with farm locations")
        print("  5. Test disease incident reporting API")


def add_sample_data():
    """Add sample geospatial data for testing (optional)"""
    app = init_app()
    
    with app.app_context():
        print("\nAdding sample geospatial test data...")
        
        # Update sample users with farm locations
        farmers = User.query.filter_by(role='farmer').all()
        
        if not farmers:
            print("No farmers found. Run traceability migration first.")
            return
        
        # Sample coordinates in Maharashtra, India
        sample_locations = [
            (18.5204, 73.8567, "Pune District"),
            (18.4500, 73.8000, "Near Pune"),
            (18.6000, 73.9000, "Northeast Pune"),
        ]
        
        for idx, farmer in enumerate(farmers[:3]):
            if not farmer.farm_latitude:
                lat, lon, address = sample_locations[idx % len(sample_locations)]
                farmer.farm_latitude = lat
                farmer.farm_longitude = lon
                farmer.farm_address = address
                print(f"  ✓ Updated {farmer.username} with farm location: {address}")
        
        # Add sample disease incidents
        if farmers and DiseaseIncident.query.count() == 0:
            print("\nCreating sample disease incidents...")
            
            incidents = [
                DiseaseIncident(
                    incident_id="INC-SAMPLE001",
                    user_id=farmers[0].id,
                    disease_name="Late Blight",
                    crop_affected="Tomato",
                    severity_level="high",
                    symptoms="Brown spots on leaves and stems",
                    latitude=18.5204,
                    longitude=73.8567,
                    affected_area=2.5,
                    detection_method="manual",
                    verification_status="verified"
                ),
                DiseaseIncident(
                    incident_id="INC-SAMPLE002",
                    user_id=farmers[0].id,
                    disease_name="Powdery Mildew",
                    crop_affected="Wheat",
                    severity_level="medium",
                    symptoms="White powdery coating on leaves",
                    latitude=18.4500,
                    longitude=73.8000,
                    affected_area=1.8,
                    detection_method="manual",
                    verification_status="pending"
                )
            ]
            
            for inc in incidents:
                db.session.add(inc)
            
            print(f"  ✓ Created {len(incidents)} sample disease incidents")
        
        db.session.commit()
        print("\n✓ Sample data added successfully!")


def drop_gews_tables():
    """Drop GEWS tables (WARNING: This will delete all GEWS data!)"""
    app = init_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("WARNING: Drop GEWS Tables")
        print("="*60)
        print("\nThis will delete:")
        print("  - All disease incidents")
        print("  - All outbreak zones")
        print("  - All outbreak alerts")
        print("  - User farm location data")
        
        response = input("\nAre you absolutely sure? (type 'DELETE' to confirm): ")
        
        if response == 'DELETE':
            print("\nDropping GEWS tables...")
            
            # Drop tables in correct order (respecting foreign keys)
            OutbreakAlert.__table__.drop(db.engine, checkfirst=True)
            OutbreakZone.__table__.drop(db.engine, checkfirst=True)
            DiseaseIncident.__table__.drop(db.engine, checkfirst=True)
            
            print("✓ GEWS tables dropped successfully!")
        else:
            print("Operation cancelled.")


def show_stats():
    """Display GEWS database statistics"""
    app = init_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("GEWS Database Statistics")
        print("="*60)
        
        users_with_location = User.query.filter(
            User.farm_latitude.isnot(None),
            User.farm_longitude.isnot(None)
        ).count()
        
        total_incidents = DiseaseIncident.query.count()
        verified_incidents = DiseaseIncident.query.filter_by(verification_status='verified').count()
        active_outbreaks = OutbreakZone.query.filter_by(status='active').count()
        total_alerts = OutbreakAlert.query.count()
        
        print(f"\nUsers with farm locations: {users_with_location}")
        print(f"Total disease incidents: {total_incidents}")
        print(f"  - Verified: {verified_incidents}")
        print(f"  - Pending: {total_incidents - verified_incidents}")
        print(f"Active outbreak zones: {active_outbreaks}")
        print(f"Total alerts sent: {total_alerts}")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--drop':
            drop_gews_tables()
        elif command == '--sample':
            add_sample_data()
        elif command == '--stats':
            show_stats()
        elif command == '--help':
            print("\nGEWS Database Migration Tool")
            print("="*60)
            print("\nUsage:")
            print("  python init_gews_db.py          # Create tables")
            print("  python init_gews_db.py --sample # Add sample data")
            print("  python init_gews_db.py --stats  # Show statistics")
            print("  python init_gews_db.py --drop   # Drop GEWS tables")
            print("  python init_gews_db.py --help   # Show this help")
            print()
        else:
            print(f"Unknown command: {command}")
            print("Use --help to see available commands")
    else:
        create_tables()
