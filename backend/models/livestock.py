from datetime import datetime
from backend.extensions import db


class LivestockAnimal(db.Model):
    __tablename__ = "livestock_animals"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    animal_type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100))
    tag_number = db.Column(db.String(100), unique=True)

    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    weight = db.Column(db.Float)

    status = db.Column(db.String(50), default="healthy")
    location = db.Column(db.String(200))

    image = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "user_id": self.user_id,
            "animal_type": self.animal_type,
            "breed": self.breed,
            "tag_number": self.tag_number,
            "date_of_birth": self.date_of_birth.isoformat()
            if self.date_of_birth
            else None,
            "gender": self.gender,
            "weight": self.weight,
            "status": self.status,
            "location": self.location,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class LivestockHealthRecord(db.Model):
    __tablename__ = "livestock_health_records"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(
        db.Integer, db.ForeignKey("livestock_animals.id"), nullable=False
    )

    checkup_date = db.Column(db.DateTime, default=datetime.utcnow)
    health_status = db.Column(db.String(50), nullable=False)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    veterinarian = db.Column(db.String(200))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "checkup_date": self.checkup_date.isoformat(),
            "health_status": self.health_status,
            "symptoms": self.symptoms,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "veterinarian": self.veterinarian,
            "notes": self.notes,
        }


class LivestockBreeding(db.Model):
    __tablename__ = "livestock_breeding"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)

    male_animal_id = db.Column(db.Integer, db.ForeignKey("livestock_animals.id"))
    female_animal_id = db.Column(db.Integer, db.ForeignKey("livestock_animals.id"))

    breeding_date = db.Column(db.Date, nullable=False)
    expected_birth_date = db.Column(db.Date)
    actual_birth_date = db.Column(db.Date)

    offspring_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="in_progress")
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "male_animal_id": self.male_animal_id,
            "female_animal_id": self.female_animal_id,
            "breeding_date": self.breeding_date.isoformat()
            if self.breeding_date
            else None,
            "expected_birth_date": self.expected_birth_date.isoformat()
            if self.expected_birth_date
            else None,
            "actual_birth_date": self.actual_birth_date.isoformat()
            if self.actual_birth_date
            else None,
            "offspring_count": self.offspring_count,
            "status": self.status,
            "notes": self.notes,
        }


class LivestockProduction(db.Model):
    __tablename__ = "livestock_production"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(
        db.Integer, db.ForeignKey("livestock_animals.id"), nullable=False
    )

    production_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))

    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "production_type": self.production_type,
            "amount": self.amount,
            "unit": self.unit,
            "record_date": self.record_date.isoformat(),
            "notes": self.notes,
        }


class LivestockFeedPlan(db.Model):
    __tablename__ = "livestock_feed_plans"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)

    feed_type = db.Column(db.String(100), nullable=False)
    daily_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))

    cost_per_unit = db.Column(db.Float)
    feeding_frequency = db.Column(db.String(50))

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "animal_type": self.animal_type,
            "feed_type": self.feed_type,
            "daily_quantity": self.daily_quantity,
            "unit": self.unit,
            "cost_per_unit": self.cost_per_unit,
            "feeding_frequency": self.feeding_frequency,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "notes": self.notes,
        }
