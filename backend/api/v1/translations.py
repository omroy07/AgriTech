"""
API Endpoints for Server-Side Multilingual Support & Dynamic Content Localization.
Handles dynamic translation for blogs, crop data, advisory resources, and on-demand UI text.
"""

from flask import Blueprint, request, jsonify
from backend.services.translation_service import TranslationService
import logging

logger = logging.getLogger(__name__)

translation_bp = Blueprint("translation", __name__)
content_bp = Blueprint("dynamic_content", __name__)

# Sample/Default Dynamic Content Repositories for AgriTech
DYNAMIC_BLOGS = [
    {
        "id": 1,
        "title": "Sustainable Farming Practices for 2025",
        "category": "Organic Farming",
        "author": "Dr. Ramesh Sharma",
        "date": "2025-01-15",
        "readTime": "5 min read",
        "summary": "Explore modern techniques for zero-budget natural farming, bio-fertilizers, and regenerative agriculture.",
        "content": "Sustainable agriculture integrates biological and ecological processes such as nutrient cycling, soil regeneration, and nitrogen fixation into agricultural production."
    },
    {
        "id": 2,
        "title": "AI in Agriculture: The Next Revolution",
        "category": "Technology",
        "author": "Ananya Patel",
        "date": "2025-02-10",
        "readTime": "7 min read",
        "summary": "How computer vision, satellite imagery, and drone analytics are revolutionizing crop disease prevention.",
        "content": "Machine learning models and multispectral satellite data empower farmers to detect foliar diseases days before symptoms become visible to the naked eye."
    },
    {
        "id": 3,
        "title": "Water-Saving Irrigation Techniques",
        "category": "Irrigation",
        "author": "Sunil Kumar",
        "date": "2025-03-01",
        "readTime": "4 min read",
        "summary": "Drip irrigation, subsurface sensors, and IoT-driven irrigation controllers saving up to 40% water.",
        "content": "Precision irrigation adjusts water delivery according to real-time soil moisture tension, minimizing percolation loss and maximizing crop transpiration efficiency."
    },
    {
        "id": 4,
        "title": "Seasonal Crop Planning for Better Yield",
        "category": "Crop Planning",
        "author": "Dr. M. S. Swaminathan Foundation",
        "date": "2025-03-12",
        "readTime": "6 min read",
        "summary": "Optimal sowing calendars, companion planting, and soil nutrient cycling strategies for Kharif and Rabi.",
        "content": "Strategic crop rotations disrupt pest lifecycles, build soil organic carbon, and stabilize farm revenues across varying monsoonal cycles."
    }
]

DYNAMIC_CROPS = [
    {
        "id": "wheat",
        "name": "Wheat",
        "variety": "HD-2967 / Sharbati",
        "idealSeason": "Rabi (Oct - Nov)",
        "waterRequirement": "Moderate (450-650 mm)",
        "soilType": "Loamy, Clay Loam",
        "growthDuration": "120 - 150 days",
        "advisory": "Ensure first irrigation at Crown Root Initiation (CRI) stage 20-25 days after sowing."
    },
    {
        "id": "rice",
        "name": "Rice",
        "variety": "Basmati 1509 / PR-126",
        "idealSeason": "Kharif (June - July)",
        "waterRequirement": "High (1200-1500 mm)",
        "soilType": "Clayey, Alluvial",
        "growthDuration": "110 - 140 days",
        "advisory": "Adopt Alternate Wetting and Drying (AWD) to reduce methane emissions and conserve groundwater."
    },
    {
        "id": "maize",
        "name": "Maize",
        "variety": "HQPM-1 / Bio-9681",
        "idealSeason": "Kharif & Rabi",
        "waterRequirement": "Medium (500-800 mm)",
        "soilType": "Well-drained Fertile Loam",
        "growthDuration": "90 - 110 days",
        "advisory": "Monitor for Fall Armyworm (FAW) egg masses on the underside of whorl leaves."
    },
    {
        "id": "cotton",
        "name": "Cotton",
        "variety": "Bt Cotton Hybrid",
        "idealSeason": "Kharif (May - June)",
        "waterRequirement": "Medium (700-1200 mm)",
        "soilType": "Deep Black Soils (Regur)",
        "growthDuration": "150 - 180 days",
        "advisory": "Use pheromone traps for early monitoring of pink bollworm infestations."
    }
]

DYNAMIC_RESOURCES = [
    {
        "id": "soil-testing-guide",
        "title": "Soil Health Management Guide",
        "description": "Comprehensive steps for collecting soil samples, interpreting NPK ratios, and applying micronutrients.",
        "category": "Soil Science",
        "downloadUrl": "/assets/guides/soil_health.pdf"
    },
    {
        "id": "ipm-toolkit",
        "title": "Integrated Pest Management (IPM) Toolkit",
        "description": "Biological controls, neem-based formulations, and threshold-based pesticide application charts.",
        "category": "Pest Management",
        "downloadUrl": "/assets/guides/ipm_toolkit.pdf"
    },
    {
        "id": "pm-kisan-guide",
        "title": "Government Schemes & Subsidy Handbook",
        "description": "Step-by-step application walkthrough for PM-KISAN, PMFBY insurance, and drip irrigation subsidies.",
        "category": "Financial Advisory",
        "downloadUrl": "/assets/guides/gov_schemes_2025.pdf"
    }
]


def _get_target_lang() -> str:
    """Extract target language from query params, headers, or default to en."""
    lang = request.args.get("lang") or request.headers.get("X-Language")
    if not lang:
        accept = request.headers.get("Accept-Language", "en")
        lang = accept.split(",")[0].split("-")[0].strip().lower()
    return lang.lower().strip()


# ==================== TRANSLATION ENDPOINTS ====================

@translation_bp.route("/translate", methods=["POST"])
def translate():
    """
    Translate text, batch of texts, or dictionary data via Google Cloud Translation API.
    Request JSON format:
      - { "text": "...", "target_lang": "hi" }
      - { "texts": ["..."], "target_lang": "kn" }
      - { "data": { ... }, "fields": ["title", "content"], "target_lang": "hi" }
    """
    payload = request.get_json(silent=True) or {}
    target_lang = payload.get("target_lang") or payload.get("target") or "en"
    source_lang = payload.get("source_lang") or payload.get("source") or "auto"

    # 1. Single text translation
    if "text" in payload:
        text = payload["text"]
        translated = TranslationService.translate_text(
            text, target_lang=target_lang, source_lang=source_lang
        )
        return jsonify({
            "status": "success",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translated_text": translated,
            "original_text": text
        })

    # 2. Batch text translation
    elif "texts" in payload:
        texts = payload["texts"]
        if not isinstance(texts, list):
            return jsonify({"status": "error", "message": "'texts' must be an array"}), 400

        translated_texts = TranslationService.translate_batch(
            texts, target_lang=target_lang, source_lang=source_lang
        )
        return jsonify({
            "status": "success",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translated_texts": translated_texts
        })

    # 3. Structured Object translation
    elif "data" in payload:
        data = payload["data"]
        fields = payload.get("fields")
        translated_data = TranslationService.translate_dict(
            data, target_lang=target_lang, fields=fields, source_lang=source_lang
        )
        return jsonify({
            "status": "success",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "data": translated_data
        })

    return jsonify({"status": "error", "message": "Missing 'text', 'texts', or 'data' field"}), 400


@translation_bp.route("/languages", methods=["GET"])
def get_languages():
    """Return the list of supported languages."""
    languages = TranslationService.get_supported_languages()
    return jsonify({
        "status": "success",
        "languages": languages
    })


# ==================== DYNAMIC CONTENT ENDPOINTS ====================

@content_bp.route("/blogs", methods=["GET"])
def get_localized_blogs():
    """
    Get dynamic blog posts localized to the requested language.
    Query param `lang` (e.g., `?lang=hi`, `?lang=kn`, `?lang=en`).
    """
    target_lang = _get_target_lang()
    translated_blogs = TranslationService.translate_list_of_dicts(
        DYNAMIC_BLOGS,
        target_lang=target_lang,
        fields=["title", "category", "summary", "content"]
    )
    return jsonify({
        "status": "success",
        "lang": target_lang,
        "count": len(translated_blogs),
        "blogs": translated_blogs
    })


@content_bp.route("/crops", methods=["GET"])
def get_localized_crops():
    """
    Get dynamic crop dataset localized to the requested language.
    Query param `lang` (e.g., `?lang=hi`, `?lang=kn`, `?lang=en`).
    """
    target_lang = _get_target_lang()
    translated_crops = TranslationService.translate_list_of_dicts(
        DYNAMIC_CROPS,
        target_lang=target_lang,
        fields=["name", "idealSeason", "waterRequirement", "soilType", "growthDuration", "advisory"]
    )
    return jsonify({
        "status": "success",
        "lang": target_lang,
        "count": len(translated_crops),
        "crops": translated_crops
    })


@content_bp.route("/resources", methods=["GET"])
def get_localized_resources():
    """
    Get dynamic agricultural resources & guides localized to the requested language.
    Query param `lang` (e.g., `?lang=hi`, `?lang=kn`, `?lang=en`).
    """
    target_lang = _get_target_lang()
    translated_resources = TranslationService.translate_list_of_dicts(
        DYNAMIC_RESOURCES,
        target_lang=target_lang,
        fields=["title", "description", "category"]
    )
    return jsonify({
        "status": "success",
        "lang": target_lang,
        "count": len(translated_resources),
        "resources": translated_resources
    })
