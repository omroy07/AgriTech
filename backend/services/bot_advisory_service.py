"""
Hyperlocal Voice Assistant & WhatsApp/SMS Advisory Bot Service for AgriTech.

Integrates:
- Twilio & Meta Cloud WhatsApp API Webhooks
- Speech-to-Text: OpenAI Whisper API / Bhashini / Google Speech Recognition
- LLM Pipeline: Google Gemini 2.5 Flash with localized agricultural prompt templates & AgriBot fallback
- Multimodal Image Processing: Plant Disease Detection with actionable remedies
- Text-to-Speech (TTS): gTTS / Bhashini / Local Audio synthesizer
"""

import os
import io
import re
import base64
import uuid
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Supported regional languages mapping
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "bhashini_code": "en", "gtts_code": "en", "label": "English"},
    "hi": {"name": "Hindi", "bhashini_code": "hi", "gtts_code": "hi", "label": "हिन्दी"},
    "mr": {"name": "Marathi", "bhashini_code": "mr", "gtts_code": "mr", "label": "मराठी"},
    "te": {"name": "Telugu", "bhashini_code": "te", "gtts_code": "te", "label": "తెలుగు"},
    "ta": {"name": "Tamil", "bhashini_code": "ta", "gtts_code": "ta", "label": "தமிழ்"},
    "kn": {"name": "Kannada", "bhashini_code": "kn", "gtts_code": "kn", "label": "ಕನ್ನಡ"},
    "pa": {"name": "Punjabi", "bhashini_code": "pa", "gtts_code": "pa", "label": "ਪੰਜਾਬੀ"},
    "gu": {"name": "Gujarati", "bhashini_code": "gu", "gtts_code": "gu", "label": "ગુજરાતી"},
    "bn": {"name": "Bengali", "bhashini_code": "bn", "gtts_code": "bn", "label": "বাংলা"},
    "ml": {"name": "Malayalam", "bhashini_code": "ml", "gtts_code": "ml", "label": "മലയാളം"},
}

# Localized agricultural system prompts
LOCALIZED_PROMPTS = {
    "hi": """आप 'AgriBot' (कृषि मित्र) हैं - भारतीय किसानों के लिए एक विशेषज्ञ हाइपरलोकल एआई कृषि सलाहकार।
किसानों को सरल, व्यावहारिक और स्पष्ट भाषा में उत्तर दें। 
अपनी सलाह में निम्नलिखित पहलुओं को प्राथमिकता दें:
1. फसल संरक्षण, जैविक उपाय (जैसे नीम का तेल, दशपर्णी अर्क) और सुरक्षित रासायनिक कीटनाशक।
2. सटीक उर्वरक मात्रा (NPK, सूक्ष्म पोषक तत्व) और सिंचाई मार्गदर्शन।
3. स्थानीय मौसम, मिट्टी का स्वास्थ्य और सरकारी योजनाओं (PM-KISAN, PMFBY, सॉइल हेल्थ कार्ड) की जानकारी।
4. यदि कोई बीमारी पहचानी गई है, तो त्वरित उपचार और रोकथाम के चरण बताएं।
उत्तर संक्षिप्त (3-5 बिंदु), व्यावहारिक और आदरपूर्वक किसान-हितैषी भाषा में दें।""",

    "mr": """तुम्ही 'AgriBot' (कृषी मित्र) आहात - महाराष्ट्रातील व भारतातील शेतकऱ्यांसाठी तज्ज्ञ कृषी सल्लागार.
शेतकऱ्यांना सोप्या, व्यावहारिक मराठी भाषेत मार्गदर्शन करा.
तुमच्या उत्तरात खालील मुद्द्यांवर भर द्या:
1. पीक संरक्षण, सेंद्रिय उपाय (निंबोळी अर्क, जीवामृत) आणि योग्य रासायनिक कीटकनाशके.
2. खतांचे संतुलित प्रमाण (NPK) व ठिबक/तुषार सिंचन व्यवस्थापन.
3. हवामान अंदाज, जमिनीचे आरोग्य आणि शासकीय योजना (पीएम किसान, पीक विमा).
उत्तर छोटे, स्पष्ट व शेतकऱ्याला समजेल अशा भाषेत द्या.""",

    "te": """మీరు 'AgriBot' (రైతు మిత్ర) - భారతీయ రైతుల కోసం నిపుణులైన AI వ్యవసాయ సలహాదారు.
రైతులకు సులభమైన, ఆచరణాత్మకమైన తెలుగు భాషలో సమాధానాలు ఇవ్వండి.
1. పంట రక్షణ, సేంద్రీయ పద్ధతులు (వేప నూనె, జీవామృతం) మరియు రసాయన మందుల మోతాదు.
2. ఎరువుల సమతుల్య వాడకం (NPK) మరియు నీటి యాజమాన్యం.
3. వాతావరణం, నేల రకాలు మరియు ప్రభుత్వ పథకాలు (PM-KISAN, PMFBY).
సమాధానాలు సంక్షిప్తంగా, సులభంగా అర్థమయ్యేలా ఉండాలి.""",

    "ta": """நீங்கள் 'AgriBot' (உழவர் தோழன்) - விவசாயிகளுக்கான AI வேளாண்மை ஆலோசகர்.
விவசாயிகளுக்கு எளிய, பயனுள்ள தமிழ் மொழியில் பதில் அளியுங்கள்.
1. பயிர் பாதுகாப்பு, இயற்கை பூச்சி விரட்டி (வேப்பெண்ணெய், பஞ்சகவ்யா) மற்றும் பூச்சிக்கொல்லி மருந்துகள்.
2. உர மேலாண்மை (NPK) மற்றும் பாசன முறைகள்.
3. வானிலை எச்சரிக்கைகள், மண் வளம் மற்றும் அரசு மானிய திட்டங்கள்.
பதில்கள் சுருக்கமாகவும், நடைமுறைக்கு ஏற்றதாகவும் இருக்க வேண்டும்.""",

    "pa": """ਤੁਸੀਂ 'AgriBot' (ਕਿਸਾਨ ਮਿੱਤਰ) ਹੋ - ਕਿਸਾਨਾਂ ਲਈ ਮਾਹਿਰ AI ਖੇਤੀਬਾੜੀ ਸਲਾਹਕਾਰ।
ਕਿਸਾਨਾਂ ਨੂੰ ਸਰਲ ਅਤੇ ਸਪੱਸ਼ਟ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।
1. ਫਸਲ ਦੀ ਸੁਰੱਖਿਆ, ਜੈਵਿਕ ਤਰੀਕੇ ਅਤੇ ਕੀਟਨਾਸ਼ਕਾਂ ਦੀ ਸਹੀ ਵਰਤੋਂ।
2. ਖਾਦਾਂ ਦੀ ਸਹੀ ਮਾਤਰਾ (NPK, ਯੂਰੀਆ, ਡੀਏਪੀ) ਅਤੇ ਸਿੰਚਾਈ।
3. ਮੌਸਮ, ਮਿੱਟੀ ਦੀ ਸਿਹਤ ਅਤੇ ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਬਾਰੇ ਜਾਣਕਾਰੀ।
ਜਵਾਬ ਸੰਖੇਪ ਅਤੇ ਵਿਵਹਾਰਕ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ।""",

    "gu": """તમે 'AgriBot' (ખેડૂત મિત્ર) છો - ખેડૂતો માટે વિશેષ AI કૃષિ સલાહકાર.
ખેડૂતોને સરળ અને સ્પષ્ટ ગુજરાતીમાં માર્ગદર્શન આપો.
1. પાક સંરક્ષણ, જૈવિક ઉપાયો (લીંબોળી તેલ, જીવામૃત) અને દવાઓનો છંટકાવ.
2. ખાતરનું સંતુલન (NPK) અને સિંચાઈ વ્યવસ્થા.
3. હવામાન અને સરકારી સહાય યોજનાઓ.
જવાબ ટૂંકા અને સરળ ભાષામાં આપો.""",

    "kn": """ನೀವು 'AgriBot' (ರೈತ ಮಿತ್ರ) - ಭಾರತೀಯ ರೈತರಿಗೆ ವಿಶೇಷ AI ಕೃಷಿ ಸಲಹೆಗಾರ.
ರೈತರಿಗೆ ಸರಳ ಹಾಗೂ ಸುಲಭವಾದ ಕನ್ನಡದಲ್ಲಿ ಮಾರ್ಗದರ್ಶನ ನೀಡಿ.
1. ಬೆಳೆ ಸಂರಕ್ಷಣೆ, ಸಾವಯವ ಕೀಟನಾಶಕಗಳು ಮತ್ತು ರಸಗೊಬ್ಬರಗಳ ಬಳಕೆ.
2. ಹನಿ ನೀರಾವರಿ, ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಮತ್ತು ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ.
3. ಸರ್ಕಾರಿ ಕೃಷಿ ಯೋಜನೆಗಳು (ಪಿಎಂ-ಕಿಸಾನ್, ಬೆಳೆ ವಿಮೆ).
ಉತ್ತರಗಳು ಸ್ಪಷ್ಟ ಹಾಗೂ ಸಂಕ್ಷಿಪ್ತವಾಗಿರಲಿ.""",

    "bn": """আপনি 'AgriBot' (কৃষক বন্ধু) - কৃষকদের জন্য বিশ্বস্ত এআই কৃষি উপদেষ্টা।
সহজ ও কার্যকর বাংলা ভাষায় কৃষকদের পরামর্শ দিন।
১. ফসলের রোগ নির্ণয়, জৈব সমাধান (নিম তেল) ও কীটনাশক প্রয়োগ।
২. সুষম সার ব্যবস্থাপনা ও সেচ কৌশল।
৩. আবহাওয়া এবং সরকারি কৃষি প্রকল্প সম্পর্কিত তথ্য।
উত্তর সংক্ষিপ্ত এবং ব্যবহারিক রাখুন।""",

    "ml": """നിങ്ങൾ 'AgriBot' (കർഷക മിത്രം) - കർഷകർക്കായുള്ള AI കാർഷിക ഉപദേശകൻ.
ലളിതമായ മലയാളത്തിൽ കർഷകർക്ക് വ്യക്തമായ നിർദ്ദേശങ്ങൾ നൽകുക.
1. വിള സംരക്ഷണം, ജൈവ കീടനാശിനികൾ, വളപ്രയോഗം.
2. കാലാവസ്ഥാ വിവരങ്ങൾ, ജലസേചനം, സർക്കാർ പദ്ധതികൾ.
ഉത്തരങ്ങൾ ചുരുങ്ങിയതും പ്രായോഗികവുമായിരിക്കണം.""",

    "en": """You are 'AgriBot' - an expert AI agricultural advisory assistant for farmers.
Provide clear, practical, empathetic advice for smallholder and commercial farmers.
Prioritize:
1. Plant protection, disease diagnosis, organic remedies (neem extract, bio-fungicides), and safe chemical dosages.
2. Balanced fertilizer application (NPK, micronutrients) and efficient irrigation.
3. Weather guidance, soil health, and government support schemes (PM-KISAN, PMFBY).
Keep responses concise (3-5 actionable bullet points), easy to understand, and respectful."""
}

# Fallback Agronomy Knowledge Base for offline / rapid responses
AGRONOMY_KB = {
    "tomato_blight": {
        "keywords": ["tomato", "blight", "black spot", "टमाटर", "झੁलसा", "టమోటా", "தக்காளி"],
        "hi": "टमाटर में झुलसा (Blight) का उपचार:\n1. 🌿 जैविक: 5 मिली नीम तेल + 1 लीटर पानी में घोलकर छिड़कें।\n2. 🧪 रासायनिक: कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) या मैंकोजेब का छिड़काव करें।\n3. 🛡️ रोकथाम: शाम को पत्तियों पर पानी देने से बचें और संक्रमित पत्तियां नष्ट करें।",
        "en": "Tomato Blight Management:\n1. 🌿 Organic: Spray Neem Oil (5ml/L of water) every 7 days.\n2. 🧪 Chemical: Spray Copper Oxychloride (2.5g/L) or Mancozeb.\n3. 🛡️ Prevention: Avoid overhead watering and remove infected lower leaves.",
        "mr": "टोमॅटोवरील करपा (Blight) नियंत्रण:\n1. 🌿 सेंद्रिय: ५ मिली निंबोळी तेल प्रति लिटर पाण्यात मिसळून फवारा.\n2. 🧪 रासायनिक: कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लिटर) फवारा.\n3. 🛡️ खबरदारी: झाडांच्या पानांवर थेट पाणी देणे टाळा.",
        "te": "టమోటా తెగులు నివారణ:\n1. 🌿 సేంద్రీయ: వేప నూనె (5ml/లీటరు) పిచికారీ చేయండి.\n2. 🧪 రసాయన: కాపర్ ఆక్సిక్లోరైడ్ (2.5 గ్రా/లీ) పిచికారీ చేయండి.\n3. 🛡️ నివారణ: సోకిన ఆకులను తొలగించండి."
    },
    "fertilizer_general": {
        "keywords": ["fertilizer", "npk", "urea", "dap", "खाद", "उर्वरक", "खत", "ఎరువు"],
        "hi": "संतुलित उर्वरक सलाह:\n1. 🌾 मिट्टी परीक्षण के आधार पर NPK 4:2:1 अनुपात में प्रयोग करें।\n2. 🍂 बुवाई के समय DAP या NPK 19:19:19 और अंतिम जुताई में गोबर की खाद (FYM) डालें।\n3. 🌱 यूरिया को 2-3 खुराकों में सिंचाई के बाद दें।",
        "en": "Balanced Fertilizer Advisory:\n1. 🌾 Apply NPK in recommended 4:2:1 ratio based on soil testing.\n2. 🍂 Apply DAP or NPK 19:19:19 at basal sowing along with well-rotted FYM.\n3. 🌱 Top-dress Urea in split doses after irrigation.",
        "mr": "संतुलित खत व्यवस्थापन:\n1. 🌾 माती परीक्षणानुसार NPK चा योग्य वापर करा.\n2. 🍂 पेरणीच्या वेळी DAP किंवा NPK 19:19:19 द्या.\n3. 🌱 युरिया २-३ हप्त्यांमध्ये विभागून द्या.",
        "te": "ఎరువుల యాజమాన్యం:\n1. 🌾 నేల పరీక్ష ఆధారంగా NPK వాడండి.\n2. 🍂 విత్తే సమయంలో DAP లేదా NPK 19:19:19 వేయండి.\n3. 🌱 యూరియాను విడతల వారీగా అందించండి."
    },
    "pm_kisan": {
        "keywords": ["pm kisan", "scheme", "subsidy", "योजना", "पीएम किसान", "ਸਕੀਮ", "పథకం"],
        "hi": "पीएम किसान सम्मान निधि (PM-KISAN):\n1. 💰 पात्र किसानों को प्रतिवर्ष ₹6,000 (3 किश्तों में ₹2,000 प्रत्येक) सीधे बैंक खाते में मिलते हैं।\n2. 📝 e-KYC pmkisan.gov.in पर या नजदीकी CSC केंद्र पर पूरी करें।\n3. 🔍 आधार और बैंक खाता NPCI से लिंक होना अनिवार्य है।",
        "en": "PM-KISAN Scheme Advisory:\n1. 💰 Eligible farmers receive ₹6,000/year directly into bank accounts in 3 installments of ₹2,000.\n2. 📝 Complete e-KYC at pmkisan.gov.in or nearby CSC center.\n3. 🔍 Ensure Aadhaar is linked to your bank account with NPCI mapping.",
        "mr": "पीएम किसान योजना:\n1. 💰 पात्र शेतकऱ्यांना वार्षिक ₹६,००० (३ हप्त्यांत ₹२,०००) थेट खात्यात मिळतात.\n2. 📝 pmkisan.gov.in वर e-KYC पूर्ण करा.\n3. 🔍 आधार कार्ड बँक खात्याशी संलग्न असणे आवश्यक आहे.",
        "te": "పీఎం కిసాన్ పథకం:\n1. 💰 అర్హులైన రైతులకు ఏడాదికి ₹6,000 (3 విడతలలో ₹2,000) అందుతాయి.\n2. 📝 pmkisan.gov.in లో e-KYC పూర్తి చేయండి.\n3. 🔍 ఆధార్ బ్యాంక్ ఖాతాతో లింక్ చేయబడి ఉండాలి."
    }
}


class BotAdvisoryService:
    """Service orchestrating Hyperlocal Voice, WhatsApp, SMS, STT, Gemini AI, Disease AI, and TTS."""

    AUDIO_CACHE_DIR = os.path.join(os.getcwd(), "uploads", "bot_audio_cache")

    @classmethod
    def ensure_audio_cache_dir(cls):
        """Ensure audio cache directory exists."""
        if not os.path.exists(cls.AUDIO_CACHE_DIR):
            try:
                os.makedirs(cls.AUDIO_CACHE_DIR, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create audio cache directory: {e}")

    # --------------------------------------------------------------------------
    # 1. SPEECH-TO-TEXT (STT) PIPELINE
    # --------------------------------------------------------------------------
    @classmethod
    def transcribe_audio(
        cls,
        audio_data: bytes,
        audio_format: str = "wav",
        lang_code: str = "hi"
    ) -> Dict[str, Any]:
        """
        Transcribe incoming voice note / audio bytes to text using:
        1. OpenAI Whisper API (if configured)
        2. Bhashini ASR API (if configured)
        3. SpeechRecognition (Google Speech Recognition / local engine)
        """
        if not audio_data or len(audio_data) == 0:
            return {"success": False, "text": "", "error": "Empty audio payload"}

        # 1. Try OpenAI Whisper API if key is present
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                headers = {"Authorization": f"Bearer {openai_key}"}
                files = {
                    "file": (f"audio.{audio_format}", audio_data, f"audio/{audio_format}"),
                    "model": (None, "whisper-1"),
                    "language": (None, lang_code if lang_code in SUPPORTED_LANGUAGES else "hi")
                }
                res = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    timeout=15
                )
                if res.status_code == 200:
                    transcription = res.json().get("text", "").strip()
                    if transcription:
                        logger.info(f"Whisper transcription successful: {transcription}")
                        return {
                            "success": True,
                            "text": transcription,
                            "engine": "whisper-1",
                            "language": lang_code
                        }
            except Exception as e:
                logger.warning(f"OpenAI Whisper transcription failed: {e}")

        # 2. Try Bhashini ASR if credentials exist
        bhashini_key = os.environ.get("BHASHINI_API_KEY")
        bhashini_user = os.environ.get("BHASHINI_USER_ID")
        if bhashini_key and bhashini_user:
            try:
                b64_audio = base64.b64encode(audio_data).decode("utf-8")
                bhashini_lang = SUPPORTED_LANGUAGES.get(lang_code, {}).get("bhashini_code", "hi")
                bhashini_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "asr",
                            "config": {
                                "language": {"sourceLanguage": bhashini_lang},
                                "audioFormat": audio_format,
                                "samplingRate": 16000
                            }
                        }
                    ],
                    "inputData": {
                        "audio": [{"audioContent": b64_audio}]
                    }
                }
                headers = {
                    "Authorization": bhashini_key,
                    "userID": bhashini_user,
                    "Content-Type": "application/json"
                }
                res = requests.post(bhashini_url, json=payload, headers=headers, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    output_text = data.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source", "")
                    if output_text:
                        return {
                            "success": True,
                            "text": output_text,
                            "engine": "bhashini-asr",
                            "language": lang_code
                        }
            except Exception as e:
                logger.warning(f"Bhashini ASR failed: {e}")

        # 3. SpeechRecognition with Google Speech fallback
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            audio_io = io.BytesIO(audio_data)
            with sr.AudioFile(audio_io) as source:
                audio = recognizer.record(source)
                google_lang = f"{lang_code}-IN" if lang_code != "en" else "en-US"
                text = recognizer.recognize_google(audio, language=google_lang)
                return {
                    "success": True,
                    "text": text,
                    "engine": "google-speech-recognition",
                    "language": lang_code
                }
        except Exception as e:
            logger.info(f"Speech recognition fallback note: {e}")

        # Graceful fallback indication
        return {
            "success": False,
            "text": "",
            "error": "Could not transcribe audio. Please speak clearly or send text query."
        }

    # --------------------------------------------------------------------------
    # 2. MULTIMODAL PLANT DISEASE DETECTION
    # --------------------------------------------------------------------------
    @classmethod
    def diagnose_crop_photo(
        cls,
        image_bytes: bytes,
        crop_type: str = "Tomato",
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a crop leaf photo sent via WhatsApp or Voice Assistant Widget.
        Pipes to backend.services.ai_disease_detection_service.AIDiseaseDetectionService.
        """
        try:
            from backend.services.ai_disease_detection_service import AIDiseaseDetectionService

            # Convert bytes to base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            diagnosis = AIDiseaseDetectionService.analyze_crop_image(
                image_base64=image_b64,
                crop_type=crop_type or "Tomato",
                location=location
            )
            return {
                "success": True,
                "diagnosis": diagnosis,
                "crop_type": crop_type,
                "disease_name": diagnosis.get("disease_name", "Unknown"),
                "severity": diagnosis.get("severity", "LOW"),
                "symptoms": diagnosis.get("symptoms", ""),
                "treatment": diagnosis.get("treatment", ""),
                "organic_solution": diagnosis.get("organic_solution", ""),
                "chemical_solution": diagnosis.get("chemical_solution", ""),
                "preventive_measures": diagnosis.get("preventive_measures", [])
            }
        except Exception as e:
            logger.error(f"Crop photo diagnosis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "diagnosis": {
                    "disease_name": "Detection Issue",
                    "treatment": "Please capture a clear photo of the infected leaf in daylight.",
                    "severity": "LOW"
                }
            }

    # --------------------------------------------------------------------------
    # 3. LLM QUERY PROCESSING (GEMINI 2.5 FLASH / AGRIBOT TEMPLATES)
    # --------------------------------------------------------------------------
    @classmethod
    def generate_advisory_response(
        cls,
        user_query: str,
        lang_code: str = "hi",
        crop_type: Optional[str] = None,
        location: Optional[str] = None,
        diagnosis_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate localized agricultural advice via Google Gemini 2.5 Flash
        with specialized Indian farmer prompt templates and fallback agronomy engine.
        """
        lang = lang_code if lang_code in SUPPORTED_LANGUAGES else "hi"
        system_prompt = LOCALIZED_PROMPTS.get(lang, LOCALIZED_PROMPTS["en"])

        # Check if diagnosis data is included from multimodal photo
        context_addon = ""
        if diagnosis_data and diagnosis_data.get("success"):
            diag = diagnosis_data.get("diagnosis", {})
            context_addon = f"""
[CROP DISEASE DIAGNOSIS DETECTED]:
- Crop: {crop_type or diagnosis_data.get('crop_type', 'Crop')}
- Identified Disease: {diag.get('disease_name')} (Severity: {diag.get('severity')})
- Symptoms: {diag.get('symptoms')}
- Organic Solution: {diag.get('organic_solution')}
- Chemical Solution: {diag.get('chemical_solution')}
- Preventive Steps: {', '.join(diag.get('preventive_measures', []))}
Please structure the response as a friendly, reassuring prescription note for the farmer with clear action steps.
"""

        full_prompt = f"""{system_prompt}

{context_addon}
Farmer's Location: {location or 'India'}
Selected Crop: {crop_type or 'General Farming'}
Farmer's Question: {user_query}

Provide a practical, structured response (with bullet points and emojis) in {SUPPORTED_LANGUAGES[lang]['name']} ({SUPPORTED_LANGUAGES[lang]['label']}):"""

        # 1. Attempt Google Gemini 2.5 Flash
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model_name = os.environ.get("GEMINI_MODEL_ID", "gemini-2.5-flash")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini advisory generation error: {e}")

        # 2. Rule-based AgriBot Agronomy Fallback
        query_lower = user_query.lower()
        matched_kb = None
        for key, entry in AGRONOMY_KB.items():
            if any(kw in query_lower for kw in entry["keywords"]):
                matched_kb = entry
                break

        if matched_kb:
            if lang in matched_kb:
                return matched_kb[lang]
            return matched_kb.get("en", matched_kb.get("hi", ""))

        # 3. Multilingual Default Advisor
        default_replies = {
            "hi": "🌾 कृषि मित्र सलाह:\n• मिट्टी की नमी और पोषक तत्वों की नियमित जांच करें।\n• मौसम अनुकूल होने पर ही कीटनाशक या उर्वरक का छिड़काव करें।\n• किसी विशिष्ट फसल या बीमारी के लिए स्पष्ट फोटो या विवरण भेजें।\n• सहायता हेल्पलाइन: 1800-180-1551 (किसान कॉल सेंटर)",
            "en": "🌾 AgriBot Advisory:\n• Maintain balanced soil moisture and monitor for pests weekly.\n• Apply fertilizers after mild irrigation for optimal root uptake.\n• Send a clear photo of the leaf or crop for instant AI disease diagnosis.\n• Kisan Call Center Toll-Free: 1800-180-1551",
            "mr": "🌾 कृषी मित्र सल्ला:\n• नियमितपणे मातीतील ओलावा तपासा.\n• पिकावर कीड दिसल्यास लगेच सेंद्रिय किंवा शिफारशीत औषध फवारा.\n• अचूक निदानासाठी पिकाचा किंवा पानाचा फोटो पाठवा.\n• शेतकरी हेल्पलाइन: १८००-१८०-१५५१",
            "te": "🌾 రైతు మిత్ర సలహా:\n• నేలలోని తేమను క్రమం తప్పకుండా పరిశీలించండి.\n• తెగుళ్ల నివారణకు తగిన మోతాదులో మందులు వాడండి.\n• వ్యాధి నిర్ధారణ కోసం పంట లేదా ఆకు ఫోటో పంపండి.\n• కిసాన్ కాల్ సెంటర్: 1800-180-1551"
        }
        return default_replies.get(lang, default_replies["en"])

    # --------------------------------------------------------------------------
    # 4. TEXT-TO-SPEECH (TTS) AUDIO SYNTHESIS
    # --------------------------------------------------------------------------
    @classmethod
    def synthesize_speech(
        cls,
        text: str,
        lang_code: str = "hi",
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert advisory text to localized audio (MP3/WAV).
        Returns audio base64, cached file path, and public URL if base_url is given.
        """
        cls.ensure_audio_cache_dir()
        audio_id = f"advisory_{uuid.uuid4().hex[:12]}"
        output_filename = f"{audio_id}.mp3"
        output_filepath = os.path.join(cls.AUDIO_CACHE_DIR, output_filename)

        # Clean text of markdown / symbols for smoother speech synthesis
        clean_text = re.sub(r'[\*\_#•\n]+', ' ', text)
        clean_text = re.sub(r'[🌿🧪🍃🛡️🌾💰📝🔍🍂🌱•]', '', clean_text)
        clean_text = clean_text[:450].strip()  # Limit length for rapid voice note

        # 1. Try Bhashini TTS if credentials available
        bhashini_key = os.environ.get("BHASHINI_API_KEY")
        bhashini_user = os.environ.get("BHASHINI_USER_ID")
        if bhashini_key and bhashini_user:
            try:
                bhashini_lang = SUPPORTED_LANGUAGES.get(lang_code, {}).get("bhashini_code", "hi")
                payload = {
                    "pipelineTasks": [
                        {
                            "taskType": "tts",
                            "config": {
                                "language": {"sourceLanguage": bhashini_lang},
                                "gender": "female"
                            }
                        }
                    ],
                    "inputData": {
                        "input": [{"source": clean_text}]
                    }
                }
                headers = {
                    "Authorization": bhashini_key,
                    "userID": bhashini_user,
                    "Content-Type": "application/json"
                }
                res = requests.post(
                    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
                    json=payload,
                    headers=headers,
                    timeout=12
                )
                if res.status_code == 200:
                    audio_b64 = res.json().get("pipelineResponse", [{}])[0].get("audio", [{}])[0].get("audioContent", "")
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        with open(output_filepath, "wb") as f:
                            f.write(audio_bytes)
                        audio_url = f"{base_url.rstrip('/')}/api/v1/bot/audio/{output_filename}" if base_url else f"/api/v1/bot/audio/{output_filename}"
                        return {
                            "success": True,
                            "audio_id": audio_id,
                            "audio_url": audio_url,
                            "audio_base64": audio_b64,
                            "filepath": output_filepath,
                            "engine": "bhashini-tts",
                            "format": "mp3"
                        }
            except Exception as e:
                logger.warning(f"Bhashini TTS failed: {e}")

        # 2. Try gTTS (Google Text to Speech)
        try:
            from gtts import gTTS
            gtts_lang = SUPPORTED_LANGUAGES.get(lang_code, {}).get("gtts_code", "hi")
            tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
            tts.save(output_filepath)

            with open(output_filepath, "rb") as f:
                audio_bytes = f.read()
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            audio_url = f"{base_url.rstrip('/')}/api/v1/bot/audio/{output_filename}" if base_url else f"/api/v1/bot/audio/{output_filename}"

            return {
                "success": True,
                "audio_id": audio_id,
                "audio_url": audio_url,
                "audio_base64": audio_b64,
                "filepath": output_filepath,
                "engine": "gtts",
                "format": "mp3"
            }
        except Exception as e:
            logger.warning(f"gTTS audio synthesis note: {e}")

        # Fallback empty response with flag
        return {
            "success": False,
            "audio_id": audio_id,
            "audio_url": "",
            "audio_base64": "",
            "error": "TTS engine unavailable on server; client Web Speech fallback enabled.",
            "format": "mp3"
        }

    # --------------------------------------------------------------------------
    # 5. UNIFIED ADVISORY PROCESSOR
    # --------------------------------------------------------------------------
    @classmethod
    def process_farmer_query(
        cls,
        query_text: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_format: str = "wav",
        image_bytes: Optional[bytes] = None,
        crop_type: Optional[str] = "Tomato",
        language: str = "hi",
        location: Optional[str] = None,
        base_url: Optional[str] = None,
        generate_audio: bool = True
    ) -> Dict[str, Any]:
        """
        End-to-end processing pipeline for text, voice notes, and crop photos.
        """
        lang = language if language in SUPPORTED_LANGUAGES else "hi"
        transcription_info = None

        # 1. Transcribe voice note if present
        if audio_bytes and len(audio_bytes) > 0:
            stt_res = cls.transcribe_audio(audio_bytes, audio_format=audio_format, lang_code=lang)
            transcription_info = stt_res
            if stt_res.get("success") and stt_res.get("text"):
                query_text = f"{query_text or ''} {stt_res['text']}".strip()

        # 2. Process image diagnosis if photo attached
        diagnosis_info = None
        if image_bytes and len(image_bytes) > 0:
            diagnosis_info = cls.diagnose_crop_photo(
                image_bytes=image_bytes,
                crop_type=crop_type or "Tomato",
                location=location
            )

        # Fallback default query if nothing provided
        if not query_text and not diagnosis_info:
            query_text = "फसल सलाह और देखभाल" if lang == "hi" else "Crop advisory and protection"
        elif not query_text and diagnosis_info:
            diag = diagnosis_info.get("diagnosis", {})
            query_text = f"फसल {crop_type or 'पौधे'} में {diag.get('disease_name', 'रोग')} का उपचार बताएं।" if lang == "hi" else f"How to treat {diag.get('disease_name', 'disease')} in {crop_type or 'crop'}?"

        # 3. Generate Advisory Text
        reply_text = cls.generate_advisory_response(
            user_query=query_text,
            lang_code=lang,
            crop_type=crop_type,
            location=location,
            diagnosis_data=diagnosis_info
        )

        # 4. Generate Voice / Audio Note
        audio_info = {}
        if generate_audio:
            audio_info = cls.synthesize_speech(
                text=reply_text,
                lang_code=lang,
                base_url=base_url
            )

        return {
            "status": "success",
            "query": query_text,
            "language": lang,
            "reply_text": reply_text,
            "transcription": transcription_info,
            "diagnosis": diagnosis_info,
            "audio": audio_info
        }

    # --------------------------------------------------------------------------
    # 6. TWILIO WEBHOOK HANDLER
    # --------------------------------------------------------------------------
    @classmethod
    def handle_twilio_inbound(cls, form_data: Dict[str, Any], base_url: str) -> str:
        """
        Handle Twilio WhatsApp & SMS Webhook POST requests.
        Returns TwiML XML string response with Message Body and optional Audio Media.
        """
        from_number = form_data.get("From", "")
        body_text = form_data.get("Body", "").strip()
        num_media = int(form_data.get("NumMedia", 0))

        image_bytes = None
        audio_bytes = None
        audio_format = "ogg"

        # Download media if attached
        if num_media > 0:
            media_url = form_data.get("MediaUrl0")
            content_type = form_data.get("MediaContentType0", "")
            if media_url:
                try:
                    auth = None
                    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
                    if account_sid and auth_token:
                        auth = (account_sid, auth_token)

                    media_resp = requests.get(media_url, auth=auth, timeout=15)
                    if media_resp.status_code == 200:
                        if "image" in content_type:
                            image_bytes = media_resp.content
                        elif "audio" in content_type or "ogg" in content_type:
                            audio_bytes = media_resp.content
                            if "ogg" in content_type:
                                audio_format = "ogg"
                            elif "mp3" in content_type:
                                audio_format = "mp3"
                except Exception as e:
                    logger.error(f"Error downloading Twilio media: {e}")

        # Detect language preference (default Hindi for Indian farmers)
        default_lang = os.environ.get("BOT_DEFAULT_LANGUAGE", "hi")
        if any(w in body_text.lower() for w in ["english", "hi in english", "hello", "hi"]):
            if "hindi" not in body_text.lower():
                default_lang = "en"
        elif any(w in body_text for w in ["मराठी", "marathi"]):
            default_lang = "mr"
        elif any(w in body_text for w in ["తెలుగు", "telugu"]):
            default_lang = "te"
        elif any(w in body_text for w in ["தமிழ்", "tamil"]):
            default_lang = "ta"

        # Process query
        result = cls.process_farmer_query(
            query_text=body_text,
            audio_bytes=audio_bytes,
            audio_format=audio_format,
            image_bytes=image_bytes,
            crop_type="Tomato",
            language=default_lang,
            base_url=base_url,
            generate_audio=True
        )

        reply_text = result.get("reply_text", "🌾 AgriBot: धन्यवाद! आपकी सलाह तैयार है।")
        audio_url = result.get("audio", {}).get("audio_url", "")

        # Format TwiML XML Response
        # Escaping XML special characters
        def xml_escape(s):
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        escaped_reply = xml_escape(reply_text)
        media_tag = f"<Media>{xml_escape(audio_url)}</Media>" if audio_url and audio_url.startswith("http") else ""

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>{escaped_reply}</Body>
        {media_tag}
    </Message>
</Response>"""
        return twiml

    # --------------------------------------------------------------------------
    # 7. META CLOUD WHATSAPP WEBHOOK HANDLER
    # --------------------------------------------------------------------------
    @classmethod
    def handle_meta_inbound(cls, payload: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """
        Handle Meta Cloud API WhatsApp incoming messages (Text, Audio, Image).
        Dispatches reply through Meta Graph API.
        """
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return {"status": "no_messages"}

            message = messages[0]
            from_phone = message.get("from")
            msg_type = message.get("type")

            query_text = ""
            image_bytes = None
            audio_bytes = None
            audio_format = "ogg"

            meta_token = os.environ.get("META_WHATSAPP_TOKEN")
            phone_number_id = os.environ.get("META_WHATSAPP_PHONE_NUMBER_ID") or value.get("metadata", {}).get("phone_number_id")

            # Handle Text
            if msg_type == "text":
                query_text = message.get("text", {}).get("body", "")

            # Handle Audio / Voice Note
            elif msg_type == "audio" and meta_token:
                audio_id = message.get("audio", {}).get("id")
                if audio_id:
                    media_url_res = requests.get(
                        f"https://graph.facebook.com/v19.0/{audio_id}",
                        headers={"Authorization": f"Bearer {meta_token}"},
                        timeout=10
                    )
                    if media_url_res.status_code == 200:
                        direct_url = media_url_res.json().get("url")
                        if direct_url:
                            audio_dl = requests.get(
                                direct_url,
                                headers={"Authorization": f"Bearer {meta_token}"},
                                timeout=15
                            )
                            if audio_dl.status_code == 200:
                                audio_bytes = audio_dl.content

            # Handle Image
            elif msg_type == "image" and meta_token:
                image_id = message.get("image", {}).get("id")
                caption = message.get("image", {}).get("caption", "")
                query_text = caption
                if image_id:
                    media_url_res = requests.get(
                        f"https://graph.facebook.com/v19.0/{image_id}",
                        headers={"Authorization": f"Bearer {meta_token}"},
                        timeout=10
                    )
                    if media_url_res.status_code == 200:
                        direct_url = media_url_res.json().get("url")
                        if direct_url:
                            img_dl = requests.get(
                                direct_url,
                                headers={"Authorization": f"Bearer {meta_token}"},
                                timeout=15
                            )
                            if img_dl.status_code == 200:
                                image_bytes = img_dl.content

            # Process query
            result = cls.process_farmer_query(
                query_text=query_text,
                audio_bytes=audio_bytes,
                audio_format=audio_format,
                image_bytes=image_bytes,
                language="hi",
                base_url=base_url,
                generate_audio=True
            )

            reply_text = result.get("reply_text", "")
            audio_url = result.get("audio", {}).get("audio_url", "")

            # Send outbound message via Meta Graph API if credentials configured
            if meta_token and phone_number_id and from_phone:
                send_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {meta_token}",
                    "Content-Type": "application/json"
                }
                # Send text response
                msg_body = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": from_phone,
                    "type": "text",
                    "text": {"preview_url": True, "body": reply_text}
                }
                requests.post(send_url, headers=headers, json=msg_body, timeout=10)

                # Send audio voice note if available and public
                if audio_url and audio_url.startswith("http"):
                    audio_body = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": from_phone,
                        "type": "audio",
                        "audio": {"link": audio_url}
                    }
                    requests.post(send_url, headers=headers, json=audio_body, timeout=10)

            return {
                "status": "success",
                "to": from_phone,
                "reply": reply_text,
                "audio_url": audio_url
            }

        except Exception as e:
            logger.error(f"Meta webhook processing error: {e}")
            return {"status": "error", "message": str(e)}
