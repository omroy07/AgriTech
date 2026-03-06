from datetime import datetime, timedelta
from backend.extensions import db


class GovernmentScheme(db.Model):
    __tablename__ = "government_schemes"

    id = db.Column(db.Integer, primary_key=True)
    scheme_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    ministry = db.Column(db.String(150))
    description = db.Column(db.Text)

    # Eligibility Criteria
    farm_size_min = db.Column(db.Float)  # Minimum farm size in acres
    farm_size_max = db.Column(db.Float)  # Maximum farm size in acres
    income_limit = db.Column(db.Float)  # Annual income limit in INR
    required_crops = db.Column(db.Text)  # JSON array of crop types
    region_specific = db.Column(db.Boolean, default=False)
    eligible_states = db.Column(db.Text)  # JSON array of state names

    # Scheme Details
    subsidy_percentage = db.Column(db.Float)
    max_subsidy_amount = db.Column(db.Float)
    application_fee = db.Column(db.Float, default=0)

    # Deadlines
    application_start_date = db.Column(db.Date)
    application_deadline = db.Column(db.Date)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Document Requirements
    required_documents = db.Column(db.Text)  # JSON array of document types

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications = db.relationship(
        "SchemeApplication",
        backref="scheme",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    reminders = db.relationship(
        "SchemeReminder", backref="scheme", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "scheme_code": self.scheme_code,
            "name": self.name,
            "ministry": self.ministry,
            "description": self.description,
            "eligibility": {
                "farm_size_min": self.farm_size_min,
                "farm_size_max": self.farm_size_max,
                "income_limit": self.income_limit,
                "required_crops": json.loads(self.required_crops)
                if self.required_crops
                else [],
                "region_specific": self.region_specific,
                "eligible_states": json.loads(self.eligible_states)
                if self.eligible_states
                else [],
            },
            "benefits": {
                "subsidy_percentage": self.subsidy_percentage,
                "max_subsidy_amount": self.max_subsidy_amount,
                "application_fee": self.application_fee,
            },
            "deadlines": {
                "start_date": self.application_start_date.isoformat()
                if self.application_start_date
                else None,
                "deadline": self.application_deadline.isoformat()
                if self.application_deadline
                else None,
            },
            "required_documents": json.loads(self.required_documents)
            if self.required_documents
            else [],
            "is_active": self.is_active,
        }


class SchemeApplication(db.Model):
    __tablename__ = "scheme_applications"

    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(
        db.Integer, db.ForeignKey("government_schemes.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"))

    # Application Details
    application_number = db.Column(
        db.String(50), unique=True, nullable=False, index=True
    )
    status = db.Column(
        db.String(20), default="draft"
    )  # draft, submitted, under_review, approved, rejected

    # Eligibility Check Results
    eligibility_score = db.Column(db.Float)
    eligibility_notes = db.Column(db.Text)

    # Application Data
    farmer_details = db.Column(db.Text)  # JSON
    farm_details = db.Column(db.Text)  # JSON
    income_proof = db.Column(db.Text)  # JSON with file reference

    # Documents
    submitted_documents = db.Column(
        db.Text
    )  # JSON array of uploaded document references
    documents_verified = db.Column(db.Boolean, default=False)

    # Assistance
    assistance_notes = db.Column(db.Text)
    assistance_contact = db.Column(db.String(100))

    # Timeline
    submitted_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "scheme_id": self.scheme_id,
            "application_number": self.application_number,
            "status": self.status,
            "eligibility_score": self.eligibility_score,
            "eligibility_notes": self.eligibility_notes,
            "submitted_documents": json.loads(self.submitted_documents)
            if self.submitted_documents
            else [],
            "documents_verified": self.documents_verified,
            "assistance_notes": self.assistance_notes,
            "timeline": {
                "submitted_at": self.submitted_at.isoformat()
                if self.submitted_at
                else None,
                "reviewed_at": self.reviewed_at.isoformat()
                if self.reviewed_at
                else None,
                "approved_at": self.approved_at.isoformat()
                if self.approved_at
                else None,
            },
            "rejection_reason": self.rejection_reason,
        }


class SchemeReminder(db.Model):
    __tablename__ = "scheme_reminders"

    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(
        db.Integer, db.ForeignKey("government_schemes.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    reminder_type = db.Column(
        db.String(30)
    )  # deadline_reminder, document_reminder, application_reminder
    reminder_date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text)

    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "scheme_id": self.scheme_id,
            "reminder_type": self.reminder_type,
            "reminder_date": self.reminder_date.isoformat(),
            "message": self.message,
            "is_sent": self.is_sent,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }
