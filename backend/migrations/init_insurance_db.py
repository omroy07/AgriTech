"""
Migration script to create insurance-related tables.
Run this script to set up the insurance and risk scoring database schema.
"""

from backend.models import db
from backend.app import create_app

def init_insurance_db():
    """Initialize insurance-related database tables."""
    print("Starting insurance database migration...")
    
    app = create_app()
    with app.app_context():
        try:
            # Import models to register them
            from backend.models import (
                RiskScoreHistory,
                InsurancePolicy,
                ClaimRequest
            )
            
            # Create tables
            print("Creating RiskScoreHistory table...")
            db.create_all(tables=[RiskScoreHistory.__table__])
            
            print("Creating InsurancePolicy table...")
            db.create_all(tables=[InsurancePolicy.__table__])
            
            print("Creating ClaimRequest table...")
            db.create_all(tables=[ClaimRequest.__table__])
            
            print("✓ Insurance database tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['risk_score_history', 'insurance_policies', 'claim_requests']
            existing = [t for t in required_tables if t in tables]
            
            print(f"\nVerified tables: {', '.join(existing)}")
            
            if len(existing) == len(required_tables):
                print("✓ All insurance tables verified successfully!")
                return True
            else:
                missing = [t for t in required_tables if t not in tables]
                print(f"⚠ Warning: Missing tables: {', '.join(missing)}")
                return False
                
        except Exception as e:
            print(f"✗ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_insurance_db()
    if success:
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test insurance APIs: POST /api/v1/insurance/policies")
        print("2. Test risk scoring: GET /api/v1/risk/score")
        print("3. Review created tables in your database")
    else:
        print("\n✗ Migration failed. Please check errors above.")
