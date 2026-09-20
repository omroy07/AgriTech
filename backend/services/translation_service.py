"""
Google Cloud Translation Service for AgriTech Backend.
Provides high-performance server-side translation of static and dynamic content
(blogs, crop data, advisory resources, community posts) with intelligent caching
and multi-tier fallback support (Google Cloud Translation API -> deep-translator -> dictionary).
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional, Union
from functools import lru_cache

logger = logging.getLogger(__name__)

# Supported language definitions
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "nativeName": "English", "flag": "🇺🇸"},
    {"code": "hi", "name": "Hindi", "nativeName": "हिन्दी", "flag": "🇮🇳"},
    {"code": "kn", "name": "Kannada", "nativeName": "ಕನ್ನಡ", "flag": "🇮🇳"},
    {"code": "te", "name": "Telugu", "nativeName": "తెలుగు", "flag": "🇮🇳"},
    {"code": "bn", "name": "Bengali", "nativeName": "বাংলা", "flag": "🇮🇳"},
    {"code": "mr", "name": "Marathi", "nativeName": "मराठी", "flag": "🇮🇳"},
    {"code": "ta", "name": "Tamil", "nativeName": "தமிழ்", "flag": "🇮🇳"},
    {"code": "gu", "name": "Gujarati", "nativeName": "ગુજરાતી", "flag": "🇮🇳"},
    {"code": "ml", "name": "Malayalam", "nativeName": "മലയാളം", "flag": "🇮🇳"},
    {"code": "pa", "name": "Punjabi", "nativeName": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
]

# Quick static fallback dictionary for core terms across primary languages
STATIC_FALLBACKS: Dict[str, Dict[str, str]] = {
    "hi": {
        "Sustainable Farming Practices for 2025": "2025 के लिए सतत कृषि पद्धतियाँ",
        "AI in Agriculture: The Next Revolution": "कृषि में AI: अगली क्रांति",
        "Organic Pest Control Methods": "जैविक कीट नियंत्रण विधियाँ",
        "Soil Health Basics Every Farmer Should Know": "मृदा स्वास्थ्य की बुनियादी बातें जो हर किसान को जाननी चाहिए",
        "Water-Saving Irrigation Techniques": "जल-बचत सिंचाई तकनीकें",
        "Seasonal Crop Planning for Better Yield": "बेहतर उपज के लिए मौसमी फसल योजना",
        "Maximize Yield with Crop Rotation": "फसल चक्र के साथ उपज अधिकतम करें",
        "Agri-Market Trends: Wheat Prices Soar": "कृषि बाजार के रुझान: गेहूं की कीमतों में उछाल",
        "Wheat": "गेहूं",
        "Rice": "चावल",
        "Maize": "मक्का",
        "Cotton": "कपास",
        "Sugarcane": "गन्ना",
        "Tomato": "टमाटर",
        "Potato": "आलू",
    },
    "kn": {
        "Sustainable Farming Practices for 2025": "2025 ರ ಸುಸ್ಥಿರ ಕೃಷಿ ಪದ್ಧತಿಗಳು",
        "AI in Agriculture: The Next Revolution": "ಕೃಷಿಯಲ್ಲಿ AI: ಮುಂದಿನ ಕ್ರಾಂತಿ",
        "Organic Pest Control Methods": "ಸಾವಯವ ಕೀಟ ನಿಯಂತ್ರಣ ವಿಧಾನಗಳು",
        "Soil Health Basics Every Farmer Should Know": "ಪ್ರತಿಯೊಬ್ಬ ರೈತ ತಿಳಿದಿರಬೇಕಾದ ಮಣ್ಣಿನ ಆರೋಗ್ಯದ ಮೂಲಭೂತ ಅಂಶಗಳು",
        "Water-Saving Irrigation Techniques": "ನೀರು ಉಳಿಸುವ ನೀರಾವರಿ ತಂತ್ರಗಳು",
        "Seasonal Crop Planning for Better Yield": "ಉತ್ತಮ ಇಳುವರಿಗಾಗಿ ಕಾಲೋಚಿತ ಬೆಳೆ ಯೋಜನೆ",
        "Maximize Yield with Crop Rotation": "ಬೆಳೆ ಪರಿವರ್ತನೆಯೊಂದಿಗೆ ಇಳುವರಿ ಹೆಚ್ಚಿಸಿ",
        "Agri-Market Trends: Wheat Prices Soar": "ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಪ್ರವೃತ್ತಿಗಳು: ಗೋಧಿ ಬೆಲೆ ಏರಿಕೆ",
        "Wheat": "ಗೋಧಿ",
        "Rice": "ಅಕ್ಕಿ / ಭತ್ತ",
        "Maize": "ಮೆಕ್ಕೆಜೋಳ",
        "Cotton": "ಹತ್ತಿ",
        "Sugarcane": "ಕಬ್ಬು",
        "Tomato": "ಟೊಮೆಟೊ",
        "Potato": "ಆಲೂಗಡ್ಡೆ",
    }
}


class TranslationService:
    """
    Unified Google Cloud Translation engine with caching, batch processing,
    and graceful fallback mechanisms.
    """

    _cache: Dict[str, str] = {}

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Retrieve configured Google Cloud Translation API Key."""
        return (
            os.getenv("GOOGLE_TRANSLATION_API_KEY")
            or os.getenv("GOOGLE_CLOUD_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

    @classmethod
    def get_supported_languages(cls) -> List[Dict[str, str]]:
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES

    @classmethod
    def _get_cache_key(cls, text: str, target_lang: str, source_lang: str = "en") -> str:
        return f"{source_lang}:{target_lang}:{text.strip()}"

    @classmethod
    def translate_text(
        cls,
        text: str,
        target_lang: str,
        source_lang: str = "en"
    ) -> str:
        """
        Translate a single text string to the target language.
        Returns the original text if target_lang is same as source_lang or on error.
        """
        if not text or not isinstance(text, str):
            return text

        target_lang = target_lang.lower().strip()
        source_lang = source_lang.lower().strip()

        if target_lang == source_lang or (target_lang == "en" and source_lang in ("en", "auto")):
            return text

        cache_key = cls._get_cache_key(text, target_lang, source_lang)
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Check static fallbacks first for ultra-fast response
        if target_lang in STATIC_FALLBACKS and text in STATIC_FALLBACKS[target_lang]:
            translated = STATIC_FALLBACKS[target_lang][text]
            cls._cache[cache_key] = translated
            return translated

        # 1. Try Google Cloud Translation REST API
        api_key = cls.get_api_key()
        if api_key:
            try:
                url = "https://translation.googleapis.com/language/translate/v2"
                params = {
                    "key": api_key,
                    "q": text,
                    "target": target_lang,
                    "format": "text"
                }
                if source_lang and source_lang != "auto":
                    params["source"] = source_lang

                resp = requests.post(url, params=params, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    translated = data["data"]["translations"][0]["translatedText"]
                    cls._cache[cache_key] = translated
                    return translated
                else:
                    logger.debug(f"Google Cloud API returned {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Google Cloud Translation API request failed: {str(e)}")

        # 2. Fallback to deep-translator (GoogleTranslator)
        try:
            from deep_translator import GoogleTranslator
            src = "auto" if source_lang == "auto" else source_lang
            translator = GoogleTranslator(source=src, target=target_lang)
            translated = translator.translate(text)
            if translated:
                cls._cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.debug(f"deep-translator fallback failed: {str(e)}")

        # 3. If all external engines fail, return original text safely
        return text

    @classmethod
    def translate_batch(
        cls,
        texts: List[str],
        target_lang: str,
        source_lang: str = "en"
    ) -> List[str]:
        """
        Translate a list of strings efficiently.
        """
        if not texts or target_lang == source_lang or (target_lang == "en" and source_lang in ("en", "auto")):
            return texts

        # Translate each text (leveraging in-memory cache)
        return [cls.translate_text(t, target_lang, source_lang) for t in texts]

    @classmethod
    def translate_dict(
        cls,
        data: Dict[str, Any],
        target_lang: str,
        fields: Optional[List[str]] = None,
        source_lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate specified or all string fields in a dictionary object.
        """
        if not data or not isinstance(data, dict):
            return data

        if target_lang == source_lang or (target_lang == "en" and source_lang in ("en", "auto")):
            return data

        translated_data = dict(data)
        for key, val in translated_data.items():
            if fields and key not in fields:
                continue

            if isinstance(val, str):
                translated_data[key] = cls.translate_text(val, target_lang, source_lang)
            elif isinstance(val, list):
                translated_data[key] = [
                    cls.translate_dict(item, target_lang, fields, source_lang)
                    if isinstance(item, dict)
                    else (cls.translate_text(item, target_lang, source_lang) if isinstance(item, str) else item)
                    for item in val
                ]
            elif isinstance(val, dict):
                translated_data[key] = cls.translate_dict(val, target_lang, fields, source_lang)

        return translated_data

    @classmethod
    def translate_list_of_dicts(
        cls,
        items: List[Dict[str, Any]],
        target_lang: str,
        fields: Optional[List[str]] = None,
        source_lang: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Translate a list of dictionary objects.
        """
        if not items or not isinstance(items, list):
            return items

        return [
            cls.translate_dict(item, target_lang, fields, source_lang)
            for item in items
        ]
