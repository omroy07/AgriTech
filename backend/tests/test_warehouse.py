import pytest
from app import app
from backend.extensions import db
from backend.models import User, WarehouseLocation, StockItem, StockMovement
from backend.services.inventory_service import InventoryService
from backend.utils.stock_formulas import StockFormulas
from datetime import date, timedelta

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
def setup_warehouse():
    with app.app_context():
        u = User(username='warehouse_mgr', email='wm@test.com')
        db.session.add(u)
        db.session.commit()
        
        wh = WarehouseLocation(name="Central Depot", manager_id=u.id)
        db.session.add(wh)
        db.session.commit()
        
        item = StockItem(
            warehouse_id=wh.id,
            item_name="Urea Fertilizer",
            category="Fertilizers",
            sku="FERT-UREA-001",
            current_quantity=1000.0,
            unit="kg",
            reorder_point=200.0
        )
        db.session.add(item)
        db.session.commit()
        return wh.id, item.id, u.id

def test_fifo_stock_movement(setup_warehouse):
    wh_id, item_id, user_id = setup_warehouse
    with app.app_context():
        # Stock IN
        movement, err = InventoryService.record_stock_in(item_id, 500.0, "PO-12345", user_id)
        assert err is None
        
        item = StockItem.query.get(item_id)
        assert item.current_quantity == 1500.0
        
        # Stock OUT
        movement, err = InventoryService.record_stock_out(item_id, 300.0, "INV-67890", user_id)
        assert err is None
        assert item.current_quantity == 1200.0
        
        # Insufficient stock
        movement, err = InventoryService.record_stock_out(item_id, 2000.0, "INV-99999", user_id)
        assert err == "Insufficient stock"

def test_reconciliation_and_shrinkage(setup_warehouse):
    wh_id, item_id, user_id = setup_warehouse
    with app.app_context():
        # Physical count shows 950kg instead of 1000kg (50kg shrinkage)
        physical_counts = {item_id: 950.0}
        log, err = InventoryService.perform_reconciliation(wh_id, user_id, physical_counts)
        
        assert err is None
        assert log.discrepancies_found == 1
        assert log.shrinkage_value == 50.0
        
        # Verify stock adjusted
        item = StockItem.query.get(item_id)
        assert item.current_quantity == 950.0

def test_stock_formulas():
    # EOQ calculation
    eoq = StockFormulas.calculate_eoq(
        annual_demand=12000,
        ordering_cost=50,
        holding_cost_per_unit=2
    )
    # sqrt((2 * 12000 * 50) / 2) = sqrt(600000) ≈ 774.6
    assert 770 < eoq < 780
    
    # Reorder point
    rop = StockFormulas.calculate_reorder_point(
        daily_demand=10,
        lead_time_days=7,
        safety_stock=20
    )
    assert rop == 90.0  # (10 * 7) + 20
    
    # Shrinkage percentage
    shrinkage = StockFormulas.calculate_shrinkage_percentage(1000, 950)
    assert shrinkage == 5.0  # ((1000-950)/1000) * 100
