from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.soil_health import (
    SoilTest,
    FertilizerRecommendation,
    ApplicationLog,
)
from backend.utils.nutrient_formulas import NutrientFormulas


class SoilAnalyticsService:
    @staticmethod
    def calculate_soil_health_score(soil_test):
        score = 100
        deductions = []

        if soil_test.ph_level < 5.5 or soil_test.ph_level > 7.5:
            deduction = 20
            score -= deduction
            deductions.append(f"pH out of range: {-deduction}")

        if soil_test.nitrogen < 20:
            deduction = 15
            score -= deduction
            deductions.append(f"Low nitrogen: {-deduction}")
        elif soil_test.nitrogen > 50:
            deduction = 10
            score -= deduction
            deductions.append(f"High nitrogen: {-deduction}")

        if soil_test.phosphorus < 15:
            deduction = 15
            score -= deduction
            deductions.append(f"Low phosphorus: {-deduction}")

        if soil_test.potassium < 100:
            deduction = 15
            score -= deduction
            deductions.append(f"Low potassium: {-deduction}")

        if soil_test.organic_matter and soil_test.organic_matter < 2:
            deduction = 20
            score -= deduction
            deductions.append(f"Low organic matter: {-deduction}")

        return {
            "score": max(0, score),
            "health_level": "Excellent"
            if score >= 90
            else "Good"
            if score >= 70
            else "Fair"
            if score >= 50
            else "Poor",
            "deductions": deductions,
        }

    @staticmethod
    def get_soil_health_trends(farm_id, years=3):
        threshold = datetime.utcnow() - timedelta(days=years * 365)
        soil_tests = (
            SoilTest.query.filter(
                SoilTest.farm_id == farm_id, SoilTest.test_date >= threshold
            )
            .order_by(SoilTest.test_date.asc())
            .all()
        )

        trends = {
            "ph_level": [],
            "nitrogen": [],
            "phosphorus": [],
            "potassium": [],
            "organic_matter": [],
            "dates": [],
        }

        health_scores = []

        for test in soil_tests:
            trends["ph_level"].append(test.ph_level)
            trends["nitrogen"].append(test.nitrogen)
            trends["phosphorus"].append(test.phosphorus)
            trends["potassium"].append(test.potassium)
            trends["organic_matter"].append(test.organic_matter)
            trends["dates"].append(test.test_date.isoformat())

            health_score = SoilAnalyticsService.calculate_soil_health_score(test)
            health_scores.append(health_score["score"])

        return {
            "trends": trends,
            "health_scores": health_scores,
            "current_score": health_scores[-1] if health_scores else None,
            "average_score": sum(health_scores) / len(health_scores)
            if health_scores
            else None,
        }

    @staticmethod
    def get_nutrient_comparison(farm_id):
        recent_tests = (
            SoilTest.query.filter_by(farm_id=farm_id)
            .order_by(SoilTest.test_date.desc())
            .limit(2)
            .all()
        )

        if len(recent_tests) < 2:
            return {"error": "Need at least 2 soil tests for comparison"}

        latest = recent_tests[0]
        previous = recent_tests[1]

        comparison = {
            "ph_level": {
                "previous": previous.ph_level,
                "current": latest.ph_level,
                "change": latest.ph_level - previous.ph_level,
                "trend": "improving"
                if abs(latest.ph_level - 7) < abs(previous.ph_level - 7)
                else "declining",
            },
            "nitrogen": {
                "previous": previous.nitrogen,
                "current": latest.nitrogen,
                "change": latest.nitrogen - previous.nitrogen,
                "trend": "improving"
                if latest.nitrogen > previous.nitrogen
                else "declining",
            },
            "phosphorus": {
                "previous": previous.phosphorus,
                "current": latest.phosphorus,
                "change": latest.phosphorus - previous.phosphorus,
                "trend": "improving"
                if latest.phosphorus > previous.phosphorus
                else "declining",
            },
            "potassium": {
                "previous": previous.potassium,
                "current": latest.potassium,
                "change": latest.potassium - previous.potassium,
                "trend": "improving"
                if latest.potassium > previous.potassium
                else "declining",
            },
        }

        return {
            "comparison_date_previous": previous.test_date.isoformat(),
            "comparison_date_latest": latest.test_date.isoformat(),
            "metrics": comparison,
        }

    @staticmethod
    def generate_comprehensive_report(farm_id):
        latest_test = (
            SoilTest.query.filter_by(farm_id=farm_id)
            .order_by(SoilTest.test_date.desc())
            .first()
        )

        if not latest_test:
            return {"error": "No soil test data available"}

        health_score = SoilAnalyticsService.calculate_soil_health_score(latest_test)
        trends = SoilAnalyticsService.get_soil_health_trends(farm_id)
        comparison = SoilAnalyticsService.get_nutrient_comparison(farm_id)

        recommendations = FertilizerRecommendation.query.filter_by(
            soil_test_id=latest_test.id
        ).all()

        return {
            "test_date": latest_test.test_date.isoformat(),
            "health_score": health_score,
            "trends": trends,
            "comparison": comparison,
            "recommendations": [r.to_dict() for r in recommendations],
            "generated_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def get_soil_quality_summary(farm_id):
        soil_tests = (
            SoilTest.query.filter_by(farm_id=farm_id)
            .order_by(SoilTest.test_date.desc())
            .all()
        )

        if not soil_tests:
            return {"error": "No soil test data available"}

        latest_test = soil_tests[0]
        health_score = SoilAnalyticsService.calculate_soil_health_score(latest_test)

        summary = {
            "latest_test_date": latest_test.test_date.isoformat(),
            "health_level": health_score["health_level"],
            "health_score": health_score["score"],
            "total_tests": len(soil_tests),
            "nutrient_status": {
                "nitrogen": "Adequate"
                if 20 <= latest_test.nitrogen <= 50
                else "Low"
                if latest_test.nitrogen < 20
                else "High",
                "phosphorus": "Adequate"
                if 15 <= latest_test.phosphorus <= 40
                else "Low"
                if latest_test.phosphorus < 15
                else "High",
                "potassium": "Adequate"
                if 100 <= latest_test.potassium <= 250
                else "Low"
                if latest_test.potassium < 100
                else "High",
                "ph": "Optimal"
                if 6.0 <= latest_test.ph_level <= 7.5
                else "Acidic"
                if latest_test.ph_level < 6.0
                else "Alkaline",
            },
        }

        return summary
