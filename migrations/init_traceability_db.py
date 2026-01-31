"""
Database migration script for Supply Chain Traceability feature.
Run this script to create the necessary database tables.
"""

from flask import Flask
from backend.extensions import db
from backend.models import User, ProduceBatch, AuditTrail, BatchStatus, UserRole
from datetime import datetime
import os

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
    """Create all database tables"""
    app = init_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✓ Tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - produce_batches")
        print("  - audit_trails")
        print("  - notifications")
        print("  - files")
        
        # Create sample users if none exist
        if User.query.count() == 0:
            print("\nCreating sample users...")
            
            sample_users = [
                User(
                    username="farmer_john",
                    email="farmer.john@example.com",
                    role=UserRole.FARMER
                ),
                User(
                    username="shopkeeper_mary",
                    email="shopkeeper.mary@example.com",
                    role=UserRole.SHOPKEEPER
                ),
                User(
                    username="admin_user",
                    email="admin@agritech.com",
                    role=UserRole.ADMIN
                )
            ]
            
            for user in sample_users:
                db.session.add(user)
            
            db.session.commit()
            print("✓ Sample users created!")
            print("  - farmer_john (Farmer)")
            print("  - shopkeeper_mary (Shopkeeper)")
            print("  - admin_user (Admin)")
        
        print("\n" + "="*50)
        print("Database migration completed successfully!")
        print("="*50)


def drop_tables():
    """Drop all database tables (WARNING: This will delete all data!)"""
    app = init_app()
    
    with app.app_context():
        response = input("WARNING: This will delete all data. Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            print("Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped successfully!")
        else:
            print("Operation cancelled.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        drop_tables()
    else:
        create_tables()
