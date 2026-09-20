"""
Unit and Integration Tests for Google Cloud Translation Service and Dynamic Content Localization.
"""

import pytest
from flask import Flask
from backend.services.translation_service import TranslationService, SUPPORTED_LANGUAGES
from backend.api.v1.translations import translation_bp, content_bp


@pytest.fixture
def client():
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.register_blueprint(translation_bp, url_prefix='/api/v1/translate')
    test_app.register_blueprint(content_bp, url_prefix='/api/v1/content')
    with test_app.test_client() as test_client:
        yield test_client


class TestTranslationService:
    def test_supported_languages(self):
        langs = TranslationService.get_supported_languages()
        assert isinstance(langs, list)
        codes = [l["code"] for l in langs]
        assert "en" in codes
        assert "hi" in codes
        assert "kn" in codes

    def test_translate_text_english(self):
        # Translating to same language or English should return original immediately
        text = "Sustainable Farming Practices"
        res = TranslationService.translate_text(text, target_lang="en", source_lang="en")
        assert res == text

    def test_translate_text_hindi_and_kannada_static_fallbacks(self):
        text = "Wheat"
        hi_res = TranslationService.translate_text(text, target_lang="hi")
        kn_res = TranslationService.translate_text(text, target_lang="kn")
        assert hi_res == "गेहूं"
        assert kn_res == "ಗೋಧಿ"

    def test_translate_batch(self):
        texts = ["Wheat", "Rice", "Maize"]
        res = TranslationService.translate_batch(texts, target_lang="hi")
        assert len(res) == 3
        assert res[0] == "गेहूं"
        assert res[1] == "चावल"
        assert res[2] == "मक्का"

    def test_translate_dict(self):
        data = {
            "id": 1,
            "title": "Wheat",
            "count": 50,
            "nested": {
                "desc": "Rice"
            }
        }
        res = TranslationService.translate_dict(data, target_lang="kn")
        assert res["title"] == "ಗೋಧಿ"
        assert res["count"] == 50
        assert res["nested"]["desc"] == "ಅಕ್ಕಿ / ಭತ್ತ"

    def test_cache_hits(self):
        text = "Organic Pest Control Methods"
        res1 = TranslationService.translate_text(text, target_lang="hi")
        # Check cache
        cache_key = TranslationService._get_cache_key(text, "hi", "en")
        assert cache_key in TranslationService._cache
        res2 = TranslationService.translate_text(text, target_lang="hi")
        assert res1 == res2


class TestTranslationApiEndpoints:
    def test_get_languages(self, client):
        resp = client.get('/api/v1/translate/languages')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        codes = [l["code"] for l in data["languages"]]
        assert "en" in codes
        assert "hi" in codes
        assert "kn" in codes

    def test_post_translate_single_text(self, client):
        resp = client.post('/api/v1/translate/translate', json={
            "text": "Wheat",
            "target_lang": "hi"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["translated_text"] == "गेहूं"

    def test_post_translate_batch_texts(self, client):
        resp = client.post('/api/v1/translate/translate', json={
            "texts": ["Wheat", "Potato"],
            "target_lang": "kn"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["translated_texts"][0] == "ಗೋಧಿ"
        assert data["translated_texts"][1] == "ಆಲೂಗಡ್ಡೆ"

    def test_get_localized_blogs(self, client):
        # English
        resp_en = client.get('/api/v1/content/blogs?lang=en')
        assert resp_en.status_code == 200
        blogs_en = resp_en.get_json()["blogs"]
        assert len(blogs_en) > 0

        # Hindi
        resp_hi = client.get('/api/v1/content/blogs?lang=hi')
        assert resp_hi.status_code == 200
        blogs_hi = resp_hi.get_json()["blogs"]
        assert len(blogs_hi) == len(blogs_en)
        # Check first blog title translated
        assert blogs_hi[0]["title"] == "2025 के लिए सतत कृषि पद्धतियाँ"

        # Kannada
        resp_kn = client.get('/api/v1/content/blogs?lang=kn')
        assert resp_kn.status_code == 200
        blogs_kn = resp_kn.get_json()["blogs"]
        assert len(blogs_kn) == len(blogs_en)
        assert blogs_kn[0]["title"] == "2025 ರ ಸುಸ್ಥಿರ ಕೃಷಿ ಪದ್ಧತಿಗಳು"

    def test_get_localized_crops(self, client):
        resp = client.get('/api/v1/content/crops?lang=hi')
        assert resp.status_code == 200
        crops = resp.get_json()["crops"]
        assert len(crops) > 0
        assert crops[0]["name"] == "गेहूं"

    def test_get_localized_resources(self, client):
        resp = client.get('/api/v1/content/resources?lang=en')
        assert resp.status_code == 200
        resources = resp.get_json()["resources"]
        assert len(resources) > 0
        assert "Soil Health Management Guide" in [r["title"] for r in resources]
