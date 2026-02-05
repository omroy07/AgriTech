import pytest
from app import app
from backend.extensions import db
from backend.models import User, Equipment, RentalBooking
from backend.services.rental_service import RentalService
from datetime import datetime, timedelta
import threading
import time

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def setup_data(test_client):
    with app.app_context():
        owner = User(username='owner', email='owner@test.com', role='farmer')
        renter1 = User(username='renter1', email='renter1@test.com', role='farmer')
        renter2 = User(username='renter2', email='renter2@test.com', role='farmer')
        db.session.add_all([owner, renter1, renter2])
        db.session.commit()
        
        tractor = Equipment(
            owner_id=owner.id,
            name='John Deere Tractor',
            category='Tractor',
            hourly_rate=100.0,
            daily_rate=1500.0,
            location='Punjab'
        )
        db.session.add(tractor)
        db.session.commit()
        return tractor.id, renter1.id, renter2.id

def test_booking_collision_prevention(setup_data):
    tractor_id, renter1_id, renter2_id = setup_data
    
    start = datetime.utcnow() + timedelta(days=5)
    end = start + timedelta(days=2)
    
    # 1. Create first booking
    booking1, error = RentalService.create_booking(tractor_id, renter1_id, start, end)
    assert error is None
    assert booking1.status == 'PENDING'
    
    # 2. Attempt overlapping booking (exact same range)
    booking2, error = RentalService.create_booking(tractor_id, renter2_id, start, end)
    assert booking2 is None
    assert "already booked" in error
    
    # 3. Attempt partially overlapping booking (start inside)
    partial_start = start + timedelta(days=1)
    partial_end = end + timedelta(days=1)
    booking3, error = RentalService.create_booking(tractor_id, renter2_id, partial_start, partial_end)
    assert booking3 is None
    assert "already booked" in error

def test_booking_state_machine(setup_data):
    tractor_id, renter1_id, _ = setup_data
    
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(days=1)
    
    booking, _ = RentalService.create_booking(tractor_id, renter1_id, start, end)
    
    # Advance to PAID
    booking, error = RentalService.update_booking_status(booking.id, 'PAID', renter1_id)
    assert error is None
    assert booking.status == 'PAID'
    assert booking.escrow.status == 'HELD'
    
    # Advance to PICKED_UP (must be owner)
    owner_id = Equipment.query.get(tractor_id).owner_id
    booking, error = RentalService.update_booking_status(booking.id, 'PICKED_UP', owner_id)
    assert error is None
    assert booking.status == 'PICKED_UP'
    
    # Try illegal transition
    _, error = RentalService.update_booking_status(booking.id, 'PAID', owner_id)
    assert "Cannot transition" in error

def test_race_condition_simulation(setup_data):
    """
    Simulate multiple threads attempting to book the same slot simultaneously.
    Note: SQLite in memory might not handle threads perfectly, but we test the logic.
    """
    tractor_id, renter1_id, renter2_id = setup_data
    
    start = datetime.utcnow() + timedelta(days=10)
    end = start + timedelta(days=1)
    
    results = []
    
    def try_booking(uid):
        # We need a new app context for each thread
        with app.app_context():
            # In a real DB, we'd use SELECT FOR UPDATE or a lock
            # Here we test if our service level check holds up
            b, err = RentalService.create_booking(tractor_id, uid, start, end)
            results.append((b, err))

    t1 = threading.Thread(target=try_booking, args=(renter1_id,))
    t2 = threading.Thread(target=try_booking, args=(renter2_id,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # Only one should have succeeded
    successes = [r for r in results if r[0] is not None]
    assert len(successes) == 1
    
    errors = [r for r in results if r[1] is not None]
    assert len(errors) == 1
    assert "already booked" in errors[0][1]
