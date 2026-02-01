"""
Database migration script for Smart Collaborative Farming & Multi-Owner Yield-Share Pool feature.
Run this script to create the necessary database tables.
"""

from flask import Flask
from backend.extensions import db
from backend.models import YieldPool, PoolContribution, ResourceShare,  PoolVote
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
    """Create all yield pool database tables"""
    app = init_app()
    
    with app.app_context():
        print("="*70)
        print("Smart Collaborative Farming & Yield-Share Pool - Database Migration")
        print("="*70)
        print("\nCreating yield pool database tables...")
        
        # Create all tables
        db.create_all()
        
        print("\n✓ Tables created successfully!")
        print("\nCreated/Updated tables:")
        print("  - yield_pools (new)")
        print("  - pool_contributions (new)")
        print("  - resource_shares (new)")
        print("  - pool_votes (new)")
        
        print("\n" + "="*70)
        print("✓ Yield Pool Database migration completed successfully!")
        print("="*70)
        
        print("\nNext steps:")
        print("  1. Configure Celery beat for periodic pool checks")
        print("  2. Register SocketIO pool events in app.py")
        print("  3. Test pool creation and contribution APIs")
        print("  4. Set up buyer offer voting workflow")
        print("  5. Test profit distribution calculations")


def add_sample_data():
    """Add sample pools and contributions for testing (optional)"""
    app = init_app()
    
    with app.app_context():
        print("\nAdding sample yield pool test data...")
        
        from backend.models import User
        
        # Check if pools already exist
        if YieldPool.query.count() > 0:
            print("Sample data already exists. Skipping...")
            return
        
        # Create sample pool
        pool = YieldPool(
            pool_id="POOL-SAMPLE001",
            pool_name="Maharashtra Wheat Cooperative 2024",
            crop_type="Wheat",
            target_quantity=100.0,
            current_quantity=0.0,
            min_price_per_ton=25000.0,
            collection_location="Pune District Warehouse",
            logistics_overhead_percent=5.0,
            status='OPEN'
        )
        
        db.session.add(pool)
        db.session.flush()
        
        print(f"  ✓ Created sample pool: {pool.pool_id}")
        
        # Add sample contributions (if users exist)
        users = User.query.limit(3).all()
        
        if users:
            contributions_data = [
                (25.0, 'A'),
                (35.0, 'A'),
                (20.0, 'B')
            ]
            
            for idx, user in enumerate(users):
                if idx < len(contributions_data):
                    quantity, grade = contributions_data[idx]
                    
                    contribution = PoolContribution(
                        pool_id=pool.id,
                        user_id=user.id,
                        quantity_tons=quantity,
                        quality_grade=grade
                    )
                    
                    db.session.add(contribution)
                    pool.current_quantity += quantity
                    
                    print(f"  ✓ Added contribution: {user.username} - {quantity} tons")
            
            # Recalculate percentages
            for contribution in pool.contributions:
                contribution.contribution_percentage = (
                    contribution.quantity_tons / pool.current_quantity * 100
                )
        
        db.session.commit()
        print("\n✓ Sample data added successfully!")
        print(f"  Pool: {pool.pool_name}")
        print(f"  Current quantity: {pool.current_quantity}/{pool.target_quantity} tons")
        print(f"  Fill percentage: {pool.current_quantity/pool.target_quantity*100:.1f}%")


def show_stats():
    """Display yield pool database statistics"""
    app = init_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("Yield Pool Database Statistics")
        print("="*70)
        
        total_pools = YieldPool.query.count()
        open_pools = YieldPool.query.filter_by(status='OPEN').count()
        locked_pools = YieldPool.query.filter_by(status='LOCKED').count()
        completed_pools = YieldPool.query.filter_by(status='COMPLETED').count()
        distributed_pools = YieldPool.query.filter_by(status='DISTRIBUTED').count()
        
        total_contributions = PoolContribution.query.count()
        total_quantity = db.session.query(db.func.sum(PoolContribution.quantity_tons)).scalar() or 0
        total_paid = db.session.query(db.func.sum(PoolContribution.actual_payout)).filter(
            PoolContribution.payout_status == 'PAID'
        ).scalar() or 0
        
        unique_contributors = db.session.query(
            db.func.count(db.func.distinct(PoolContribution.user_id))
        ).scalar()
        
        total_resources = ResourceShare.query.count()
        total_votes = PoolVote.query.count()
        
        print(f"\nTotal pools: {total_pools}")
        print(f"  - Open: {open_pools}")
        print(f"  - Locked: {locked_pools}")
        print(f"  - Completed: {completed_pools}")
        print(f"  - Distributed: {distributed_pools}")
        
        print(f"\nTotal contributions: {total_contributions}")
        print(f"  - Total quantity: {total_quantity:.2f} tons")
        print(f"  - Total paid out: ₹{total_paid:.2f}")
        print(f"  - Unique contributors: {unique_contributors}")
        
        print(f"\nShared resources: {total_resources}")
        print(f"Total votes cast: {total_votes}")
        
        print("\n" + "="*70)


def drop_pool_tables():
    """Drop yield pool tables (WARNING: This will delete all pool data!)"""
    app = init_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("WARNING: Drop Yield Pool Tables")
        print("="*70)
        print("\nThis will delete:")
        print("  - All yield pools")
        print("  - All pool contributions")
        print("  - All resource shares")
        print("  - All pool votes")
        
        response = input("\nAre you absolutely sure? (type 'DELETE' to confirm): ")
        
        if response == 'DELETE':
            print("\nDropping pool tables...")
            
            # Drop tables in correct order (respecting foreign keys)
            PoolVote.__table__.drop(db.engine, checkfirst=True)
            ResourceShare.__table__.drop(db.engine, checkfirst=True)
            PoolContribution.__table__.drop(db.engine, checkfirst=True)
            YieldPool.__table__.drop(db.engine, checkfirst=True)
            
            print("✓ Yield pool tables dropped successfully!")
        else:
            print("Operation cancelled.")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--drop':
            drop_pool_tables()
        elif command == '--sample':
            add_sample_data()
        elif command == '--stats':
            show_stats()
        elif command == '--help':
            print("\nYield Pool Database Migration Tool")
            print("="*70)
            print("\nUsage:")
            print("  python init_yield_pools_db.py          # Create tables")
            print("  python init_yield_pools_db.py --sample # Add sample data")
            print("  python init_yield_pools_db.py --stats  # Show statistics")
            print("  python init_yield_pools_db.py --drop   # Drop pool tables")
            print("  python init_yield_pools_db.py --help   # Show this help")
            print()
        else:
            print(f"Unknown command: {command}")
            print("Use --help to see available commands...")
    else:
        create_tables()
