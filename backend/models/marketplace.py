from datetime import datetime
from backend.extensions import db


class MarketplaceListing(db.Model):
    __tablename__ = "marketplace_listings"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)

    is_available = db.Column(db.Boolean, default=True)
    is_organic = db.Column(db.Boolean, default=False)

    images = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "product_name": self.product_name,
            "description": self.description,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "price_per_unit": self.price_per_unit,
            "location": self.location,
            "is_available": self.is_available,
            "is_organic": self.is_organic,
            "images": self.images,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MarketplaceOrder(db.Model):
    __tablename__ = "marketplace_orders"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(
        db.Integer, db.ForeignKey("marketplace_listings.id"), nullable=False
    )
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    delivery_address = db.Column(db.String(500))
    delivery_status = db.Column(db.String(50), default="pending")
    tracking_number = db.Column(db.String(100))

    status = db.Column(db.String(50), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "delivery_address": self.delivery_address,
            "delivery_status": self.delivery_status,
            "tracking_number": self.tracking_number,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MarketplaceRating(db.Model):
    __tablename__ = "marketplace_ratings"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("marketplace_orders.id"), nullable=False
    )
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "rater_id": self.rater_id,
            "rated_user_id": self.rated_user_id,
            "rating": self.rating,
            "review": self.review,
            "created_at": self.created_at.isoformat(),
        }
