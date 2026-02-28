from datetime import datetime
from backend.extensions import db
from backend.models.livestock import (
    LivestockAnimal,
    LivestockHealthRecord,
    LivestockBreeding,
    LivestockProduction,
    LivestockFeedPlan,
)


class LivestockService:
    @staticmethod
    def add_animal(animal_data):
        animal = LivestockAnimal(
            farm_id=animal_data["farm_id"],
            user_id=animal_data["user_id"],
            animal_type=animal_data["animal_type"],
            breed=animal_data.get("breed"),
            tag_number=animal_data.get("tag_number"),
            date_of_birth=datetime.strptime(
                animal_data.get("date_of_birth"), "%Y-%m-%d"
            ).date()
            if animal_data.get("date_of_birth")
            else None,
            gender=animal_data.get("gender"),
            weight=animal_data.get("weight"),
            location=animal_data.get("location"),
            image=animal_data.get("image"),
        )
        db.session.add(animal)
        db.session.commit()
        return animal

    @staticmethod
    def get_farm_animals(farm_id):
        return LivestockAnimal.query.filter_by(farm_id=farm_id).all()

    @staticmethod
    def add_health_record(health_data):
        record = LivestockHealthRecord(
            animal_id=health_data["animal_id"],
            checkup_date=datetime.strptime(health_data.get("checkup_date"), "%Y-%m-%d")
            if health_data.get("checkup_date")
            else datetime.utcnow(),
            health_status=health_data["health_status"],
            symptoms=health_data.get("symptoms"),
            diagnosis=health_data.get("diagnosis"),
            treatment=health_data.get("treatment"),
            veterinarian=health_data.get("veterinarian"),
            notes=health_data.get("notes"),
        )
        db.session.add(record)

        animal = LivestockAnimal.query.get(health_data["animal_id"])
        if animal:
            animal.status = health_data["health_status"]

        db.session.commit()
        return record

    @staticmethod
    def get_animal_health_history(animal_id):
        return (
            LivestockHealthRecord.query.filter_by(animal_id=animal_id)
            .order_by(LivestockHealthRecord.checkup_date.desc())
            .all()
        )

    @staticmethod
    def record_breeding(breeding_data):
        breeding = LivestockBreeding(
            farm_id=breeding_data["farm_id"],
            male_animal_id=breeding_data.get("male_animal_id"),
            female_animal_id=breeding_data.get("female_animal_id"),
            breeding_date=datetime.strptime(
                breeding_data["breeding_date"], "%Y-%m-%d"
            ).date(),
            expected_birth_date=datetime.strptime(
                breeding_data["expected_birth_date"], "%Y-%m-%d"
            ).date()
            if breeding_data.get("expected_birth_date")
            else None,
            notes=breeding_data.get("notes"),
        )
        db.session.add(breeding)
        db.session.commit()
        return breeding

    @staticmethod
    def get_farm_breeding_records(farm_id):
        return (
            LivestockBreeding.query.filter_by(farm_id=farm_id)
            .order_by(LivestockBreeding.breeding_date.desc())
            .all()
        )

    @staticmethod
    def record_production(production_data):
        production = LivestockProduction(
            animal_id=production_data["animal_id"],
            production_type=production_data["production_type"],
            amount=production_data["amount"],
            unit=production_data.get("unit"),
            notes=production_data.get("notes"),
        )
        db.session.add(production)
        db.session.commit()
        return production

    @staticmethod
    def get_animal_production(animal_id):
        return (
            LivestockProduction.query.filter_by(animal_id=animal_id)
            .order_by(LivestockProduction.record_date.desc())
            .all()
        )

    @staticmethod
    def create_feed_plan(feed_data):
        plan = LivestockFeedPlan(
            farm_id=feed_data["farm_id"],
            animal_type=feed_data["animal_type"],
            feed_type=feed_data["feed_type"],
            daily_quantity=feed_data["daily_quantity"],
            unit=feed_data.get("unit"),
            cost_per_unit=feed_data.get("cost_per_unit"),
            feeding_frequency=feed_data.get("feeding_frequency"),
            start_date=datetime.strptime(feed_data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(feed_data["end_date"], "%Y-%m-%d").date()
            if feed_data.get("end_date")
            else None,
            notes=feed_data.get("notes"),
        )
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def get_farm_feed_plans(farm_id):
        return LivestockFeedPlan.query.filter_by(farm_id=farm_id).all()

    @staticmethod
    def get_livestock_summary(farm_id):
        animals = LivestockService.get_farm_animals(farm_id)

        summary = {
            "total_animals": len(animals),
            "by_type": {},
            "by_status": {},
            "healthy_count": 0,
            "sick_count": 0,
        }

        for animal in animals:
            if animal.animal_type not in summary["by_type"]:
                summary["by_type"][animal.animal_type] = 0
            summary["by_type"][animal.animal_type] += 1

            if animal.status not in summary["by_status"]:
                summary["by_status"][animal.status] = 0
            summary["by_status"][animal.status] += 1

            if animal.status == "healthy":
                summary["healthy_count"] += 1
            else:
                summary["sick_count"] += 1

        return summary
