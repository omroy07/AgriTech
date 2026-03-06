from datetime import datetime, timedelta
from backend.models.government_schemes import (
    GovernmentScheme,
    SchemeApplication,
    SchemeReminder,
)
from backend.models.user import User
from backend.models.farm import Farm
from backend.extensions import db
import json


class GovernmentSchemeService:
    def __init__(self):
        pass

    def get_all_schemes(self, filters=None):
        query = GovernmentScheme.query.filter_by(is_active=True)

        if filters:
            if filters.get("ministry"):
                query = query.filter(GovernmentScheme.ministry == filters["ministry"])
            if filters.get("region"):
                state = filters.get("region")
                query = query.filter(
                    db.or_(
                        GovernmentScheme.region_specific == False,
                        GovernmentScheme.eligible_states.like(f"%{state}%"),
                    )
                )
            if filters.get("deadline_from"):
                query = query.filter(
                    GovernmentScheme.application_deadline >= filters["deadline_from"]
                )
            if filters.get("deadline_to"):
                query = query.filter(
                    GovernmentScheme.application_deadline <= filters["deadline_to"]
                )

        schemes = query.order_by(GovernmentScheme.application_deadline.asc()).all()
        return [scheme.to_dict() for scheme in schemes]

    def get_scheme_by_id(self, scheme_id):
        scheme = GovernmentScheme.query.get(scheme_id)
        return scheme.to_dict() if scheme else None

    def check_eligibility(self, scheme_id, user_id, farm_id=None):
        scheme = GovernmentScheme.query.get(scheme_id)
        if not scheme:
            return {"eligible": False, "reason": "Scheme not found"}

        user = User.query.get(user_id)
        if not user:
            return {"eligible": False, "reason": "User not found"}

        notes = []
        score = 0
        total_criteria = 0

        total_criteria += 1
        if scheme.farm_size_min or scheme.farm_size_max:
            if farm_id:
                farm = Farm.query.get(farm_id)
                if farm and farm.area_hectares:
                    area_acres = farm.area_hectares * 2.47105
                    if scheme.farm_size_min and area_acres < scheme.farm_size_min:
                        notes.append(
                            f"Farm size {area_acres:.2f} acres is below minimum {scheme.farm_size_min} acres"
                        )
                    elif scheme.farm_size_max and area_acres > scheme.farm_size_max:
                        notes.append(
                            f"Farm size {area_acres:.2f} acres exceeds maximum {scheme.farm_size_max} acres"
                        )
                    else:
                        score += 1
            else:
                notes.append("Farm size verification required")
        else:
            score += 1

        total_criteria += 1
        if scheme.income_limit:
            if hasattr(user, "annual_income") and user.annual_income:
                if user.annual_income <= scheme.income_limit:
                    score += 1
                else:
                    notes.append(f"Income exceeds limit of {scheme.income_limit} INR")
            else:
                notes.append("Income verification required")
        else:
            score += 1

        total_criteria += 1
        if scheme.region_specific and scheme.eligible_states:
            if user.location:
                eligible = False
                states = json.loads(scheme.eligible_states)
                for state in states:
                    if state.lower() in user.location.lower():
                        eligible = True
                        break
                if eligible:
                    score += 1
                else:
                    notes.append(f"Location {user.location} not in eligible states")
            else:
                notes.append("Location verification required")
        else:
            score += 1

        eligibility_percentage = (
            (score / total_criteria) * 100 if total_criteria > 0 else 0
        )

        return {
            "eligible": eligibility_percentage >= 70,
            "score": eligibility_percentage,
            "notes": notes,
        }

    def get_application_assistance(self, scheme_id):
        scheme = GovernmentScheme.query.get(scheme_id)
        if not scheme:
            return None

        documents = (
            json.loads(scheme.required_documents) if scheme.required_documents else []
        )

        assistance = {
            "application_steps": [
                "Complete eligibility check",
                "Gather required documents",
                "Fill application form with accurate details",
                "Upload supporting documents",
                "Submit application before deadline",
                "Track application status",
            ],
            "document_checklist": documents,
            "timeline_suggestions": {
                "recommended_submission": scheme.application_deadline
                - timedelta(days=7)
                if scheme.application_deadline
                else None,
                "last_submission": scheme.application_deadline,
            },
            "contact_information": {
                "ministry": scheme.ministry,
                "scheme_code": scheme.scheme_code,
                "application_portal": f"/schemes/{scheme_id}/apply",
            },
            "tips": [
                "Double-check all document uploads are clear and readable",
                "Ensure farm details match land records",
                "Keep application number for tracking",
                "Apply well before deadline to avoid last-minute issues",
                "Contact scheme helpline if you face any issues",
            ],
        }

        return assistance

    def create_application(
        self, scheme_id, user_id, farm_id=None, application_data=None
    ):
        scheme = GovernmentScheme.query.get(scheme_id)
        if not scheme:
            return {"success": False, "message": "Scheme not found"}

        eligibility = self.check_eligibility(scheme_id, user_id, farm_id)

        application = SchemeApplication(
            scheme_id=scheme_id,
            user_id=user_id,
            farm_id=farm_id,
            application_number=f"SCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="draft",
            eligibility_score=eligibility.get("score"),
            eligibility_notes=json.dumps(eligibility.get("notes", [])),
            farmer_details=json.dumps(application_data.get("farmer_details", {}))
            if application_data
            else "{}",
            farm_details=json.dumps(application_data.get("farm_details", {}))
            if application_data
            else "{}",
            submitted_documents=json.dumps(application_data.get("documents", []))
            if application_data
            else "[]",
        )

        db.session.add(application)
        db.session.commit()

        return {
            "success": True,
            "application_id": application.id,
            "application_number": application.application_number,
            "eligibility": eligibility,
        }

    def submit_application(self, application_id):
        application = SchemeApplication.query.get(application_id)
        if not application:
            return {"success": False, "message": "Application not found"}

        application.status = "submitted"
        application.submitted_at = datetime.utcnow()
        db.session.commit()

        return {"success": True, "message": "Application submitted successfully"}

    def get_user_applications(self, user_id, status=None):
        query = SchemeApplication.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        applications = query.order_by(SchemeApplication.created_at.desc()).all()
        return [app.to_dict() for app in applications]

    def create_deadline_reminders(self, scheme_id, user_id):
        scheme = GovernmentScheme.query.get(scheme_id)
        if not scheme or not scheme.application_deadline:
            return []

        reminders = []
        deadline = scheme.application_deadline

        reminder_dates = [
            (deadline - timedelta(days=30), "30 days before deadline"),
            (deadline - timedelta(days=15), "15 days before deadline"),
            (deadline - timedelta(days=7), "1 week before deadline"),
            (deadline - timedelta(days=3), "3 days before deadline"),
            (deadline - timedelta(days=1), "Last day reminder"),
        ]

        for reminder_date, reminder_type in reminder_dates:
            if datetime.now().date() <= reminder_date.date():
                reminder = SchemeReminder(
                    scheme_id=scheme_id,
                    user_id=user_id,
                    reminder_type="deadline_reminder",
                    reminder_date=datetime.combine(reminder_date, datetime.min.time()),
                    message=f"Reminder: {scheme.name} application deadline is on {deadline.strftime('%Y-%m-%d')}",
                )
                db.session.add(reminder)
                reminders.append(reminder)

        db.session.commit()
        return reminders

    def get_upcoming_deadlines(self, days=30):
        cutoff_date = datetime.now().date() + timedelta(days=days)
        schemes = (
            GovernmentScheme.query.filter(
                GovernmentScheme.is_active == True,
                GovernmentScheme.application_deadline.isnot(None),
                GovernmentScheme.application_deadline >= datetime.now().date(),
                GovernmentScheme.application_deadline <= cutoff_date,
            )
            .order_by(GovernmentScheme.application_deadline.asc())
            .all()
        )

        return [scheme.to_dict() for scheme in schemes]

    def search_schemes(self, keyword):
        keyword = f"%{keyword}%"
        schemes = GovernmentScheme.query.filter(
            db.or_(
                GovernmentScheme.name.ilike(keyword),
                GovernmentScheme.description.ilike(keyword),
                GovernmentScheme.ministry.ilike(keyword),
                GovernmentScheme.scheme_code.ilike(keyword),
            ),
            GovernmentScheme.is_active == True,
        ).all()

        return [scheme.to_dict() for scheme in schemes]


government_scheme_service = GovernmentSchemeService()
