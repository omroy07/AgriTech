"""
Market and Mandi Price Database Models.
Location: backend/models/market.py
"""

from datetime import datetime
from backend.extensions import db


class MarketPrice(db.Model):
    """Real-time and historical commodity prices across mandis."""
    __tablename__ = 'market_prices'

    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False, index=True)
    commodity_code = db.Column(db.String(50), nullable=True)
    variety = db.Column(db.String(100), default='Local')
    market = db.Column(db.String(150), nullable=False, index=True)
    district = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    modal_price = db.Column(db.Float, nullable=False)   # ₹ per Quintal
    min_price = db.Column(db.Float, nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    arrivals_tonnes = db.Column(db.Float, default=50.0)
    unit = db.Column(db.String(30), default='Quintal')
    price_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "crop_name": self.crop_name,
            "commodity": self.crop_name,
            "variety": self.variety,
            "market": self.market,
            "district": self.district,
            "state": self.state,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "modal_price": self.modal_price,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "arrivals_tonnes": self.arrivals_tonnes,
            "unit": self.unit,
            "price_date": self.price_date.isoformat() if self.price_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PriceWatchlist(db.Model):
    """Farmer price alerts and target watchlist."""
    __tablename__ = 'price_watchlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    crop_name = db.Column(db.String(100), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    mandi_name = db.Column(db.String(150), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(25), nullable=True)
    alert_channel = db.Column(db.String(30), default='SMS')  # SMS | PUSH | WHATSAPP | IN_APP
    alert_enabled = db.Column(db.Boolean, default=True)
    is_triggered = db.Column(db.Boolean, default=False)
    triggered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crop_name": self.crop_name,
            "target_price": self.target_price,
            "mandi_name": self.mandi_name,
            "district": self.district,
            "phone_number": self.phone_number,
            "alert_channel": self.alert_channel,
            "alert_enabled": self.alert_enabled,
            "is_triggered": self.is_triggered,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
