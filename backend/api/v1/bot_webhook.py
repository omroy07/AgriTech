"""
Hyperlocal Voice Assistant & WhatsApp/SMS Advisory Bot Webhooks and REST Endpoints.
Location: backend/api/v1/bot_webhook.py
"""

import os
import io
import base64
import logging
from flask import Blueprint, request, jsonify, Response, send_from_directory
from backend.services.bot_advisory_service import BotAdvisoryService, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

bot_webhook_bp = Blueprint("bot_webhook", __name__)


# ------------------------------------------------------------------------------
# 1. TWILIO WHATSAPP & SMS WEBHOOK
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/webhook/twilio", methods=["POST", "GET"])
def twilio_webhook():
    """
    Twilio inbound webhook for SMS & WhatsApp advisory messages.
    Supports text, voice notes (STT), and plant disease photos (multimodal diagnosis).
    Returns TwiML XML with localized advice and audio voice note URL.
    """
    try:
        form_data = request.form.to_dict() or request.args.to_dict()
        base_url = request.host_url
        twiml_response = BotAdvisoryService.handle_twilio_inbound(form_data, base_url)
        return Response(twiml_response, mimetype="application/xml; charset=utf-8")
    except Exception as e:
        logger.error(f"Twilio webhook processing error: {e}")
        fallback_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        <Body>🌾 AgriBot: क्षमा करें, सेवा अभी व्यस्त है। कृपया कुछ समय बाद पुनः प्रयास करें। (1800-180-1551)</Body>
    </Message>
</Response>"""
        return Response(fallback_twiml, mimetype="application/xml; charset=utf-8")


# ------------------------------------------------------------------------------
# 2. META CLOUD WHATSAPP API WEBHOOK
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/webhook/meta", methods=["GET"])
def meta_webhook_verify():
    """
    Meta Cloud WhatsApp webhook verification endpoint.
    Verifies hub.verify_token and returns hub.challenge.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    expected_token = os.environ.get("META_WHATSAPP_VERIFY_TOKEN", "agritech_bot_token_2025")

    if mode == "subscribe" and token == expected_token:
        logger.info("Meta WhatsApp webhook verified successfully.")
        return Response(challenge, mimetype="text/plain", status=200)

    logger.warning("Meta WhatsApp verification token mismatch.")
    return jsonify({"status": "error", "message": "Verification failed"}), 403


@bot_webhook_bp.route("/webhook/meta", methods=["POST"])
def meta_webhook_messages():
    """
    Meta Cloud WhatsApp inbound message handler.
    Processes text, voice notes, and crop photos asynchronously.
    """
    try:
        payload = request.get_json(silent=True) or {}
        base_url = request.host_url
        res = BotAdvisoryService.handle_meta_inbound(payload, base_url)
        return jsonify(res), 200
    except Exception as e:
        logger.error(f"Meta webhook message error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------------------------
# 3. PWA / WEB HYPERLOCAL VOICE ASSISTANT QUERY ENDPOINT
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/query", methods=["POST"])
def bot_query():
    """
    Unified REST endpoint for frontend voice assistant widget, PWA, and mobile apps.
    Accepts JSON or multipart/form-data:
    - query: text query
    - audio: audio file upload or base64
    - image: leaf image file upload or base64
    - language: language code ('hi', 'mr', 'te', 'ta', 'en', etc.)
    - crop_type: crop name ('Tomato', 'Wheat', 'Rice', etc.)
    - location: farmer city/state/gps
    """
    try:
        query_text = None
        audio_bytes = None
        audio_format = "wav"
        image_bytes = None
        crop_type = "Tomato"
        language = "hi"
        location = None
        generate_audio = True

        # Check if multipart form-data
        if request.content_type and "multipart/form-data" in request.content_type:
            query_text = request.form.get("query") or request.form.get("text")
            language = request.form.get("language") or request.form.get("lang", "hi")
            crop_type = request.form.get("crop_type", "Tomato")
            location = request.form.get("location")
            generate_audio = request.form.get("generate_audio", "true").lower() == "true"

            # Check audio file upload
            if "audio" in request.files:
                audio_file = request.files["audio"]
                audio_bytes = audio_file.read()
                filename = audio_file.filename.lower()
                if filename.endswith(".ogg") or filename.endswith(".opus"):
                    audio_format = "ogg"
                elif filename.endswith(".mp3"):
                    audio_format = "mp3"
                elif filename.endswith(".webm"):
                    audio_format = "webm"
                else:
                    audio_format = "wav"

            # Check image file upload
            if "image" in request.files:
                image_file = request.files["image"]
                image_bytes = image_file.read()

        # Check if JSON payload
        else:
            data = request.get_json(silent=True) or {}
            query_text = data.get("query") or data.get("text")
            language = data.get("language") or data.get("lang", "hi")
            crop_type = data.get("crop_type", "Tomato")
            location = data.get("location")
            generate_audio = data.get("generate_audio", True)

            # Audio base64
            if data.get("audio_base64"):
                try:
                    audio_raw = data.get("audio_base64")
                    if "," in audio_raw:
                        audio_raw = audio_raw.split(",")[1]
                    audio_bytes = base64.b64decode(audio_raw)
                    audio_format = data.get("audio_format", "wav")
                except Exception as e:
                    logger.warning(f"Failed decoding audio_base64: {e}")

            # Image base64
            if data.get("image_base64") or data.get("image"):
                try:
                    img_raw = data.get("image_base64") or data.get("image")
                    if "," in img_raw:
                        img_raw = img_raw.split(",")[1]
                    image_bytes = base64.b64decode(img_raw)
                except Exception as e:
                    logger.warning(f"Failed decoding image_base64: {e}")

        # Process through advisory pipeline
        base_url = request.host_url
        result = BotAdvisoryService.process_farmer_query(
            query_text=query_text,
            audio_bytes=audio_bytes,
            audio_format=audio_format,
            image_bytes=image_bytes,
            crop_type=crop_type,
            language=language,
            location=location,
            base_url=base_url,
            generate_audio=generate_audio
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Bot query error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------------------------
# 4. STANDALONE SPEECH-TO-TEXT (STT) ENDPOINT
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/stt", methods=["POST"])
def speech_to_text_endpoint():
    """
    Transcribe speech audio file or base64 using Whisper / Bhashini / SpeechRecognition.
    """
    try:
        audio_bytes = None
        audio_format = "wav"
        lang = request.args.get("language") or request.args.get("lang", "hi")

        if request.files and "audio" in request.files:
            audio_file = request.files["audio"]
            audio_bytes = audio_file.read()
            filename = audio_file.filename.lower()
            if filename.endswith(".ogg") or filename.endswith(".opus"):
                audio_format = "ogg"
            elif filename.endswith(".mp3"):
                audio_format = "mp3"
        elif request.is_json:
            data = request.get_json()
            lang = data.get("language", lang)
            audio_raw = data.get("audio_base64", "")
            if "," in audio_raw:
                audio_raw = audio_raw.split(",")[1]
            audio_bytes = base64.b64decode(audio_raw)
            audio_format = data.get("audio_format", "wav")

        if not audio_bytes:
            return jsonify({"status": "error", "message": "No audio payload provided"}), 400

        result = BotAdvisoryService.transcribe_audio(
            audio_data=audio_bytes,
            audio_format=audio_format,
            lang_code=lang
        )
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"STT endpoint error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------------------------
# 5. STANDALONE TEXT-TO-SPEECH (TTS) ENDPOINT
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/tts", methods=["POST"])
def text_to_speech_endpoint():
    """
    Convert text to localized Indian language speech audio (gTTS / Bhashini).
    """
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        lang = data.get("language", "hi")

        if not text:
            return jsonify({"status": "error", "message": "Text parameter is required"}), 400

        base_url = request.host_url
        result = BotAdvisoryService.synthesize_speech(
            text=text,
            lang_code=lang,
            base_url=base_url
        )
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------------------------
# 6. AUDIO CACHE SERVING
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/audio/<filename>", methods=["GET"])
def serve_bot_audio(filename):
    """
    Serve generated audio file for WhatsApp/Twilio/browser playback.
    """
    BotAdvisoryService.ensure_audio_cache_dir()
    return send_from_directory(
        BotAdvisoryService.AUDIO_CACHE_DIR,
        filename,
        mimetype="audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    )


# ------------------------------------------------------------------------------
# 7. BOT STATUS & HEALTH ENDPOINT
# ------------------------------------------------------------------------------
@bot_webhook_bp.route("/status", methods=["GET"])
def bot_status():
    """
    Health check and capability matrix for Hyperlocal Voice & WhatsApp bot.
    """
    return jsonify({
        "status": "active",
        "service": "Hyperlocal Voice Assistant & WhatsApp/SMS Advisory Bot",
        "supported_languages": SUPPORTED_LANGUAGES,
        "capabilities": {
            "stt": ["openai-whisper", "bhashini-asr", "google-speech-recognition", "web-speech-api"],
            "llm": ["gemini-2.5-flash", "agribot-expert-engine"],
            "tts": ["gtts", "bhashini-tts", "web-speech-synthesis"],
            "multimodal_disease_detection": True,
            "offline_pwa_fallback": True,
            "channels": ["Twilio-SMS", "Twilio-WhatsApp", "Meta-Cloud-WhatsApp", "Web-PWA-Voice-Widget"]
        },
        "config": {
            "gemini_configured": bool(os.environ.get("GEMINI_API_KEY")),
            "whisper_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "bhashini_configured": bool(os.environ.get("BHASHINI_API_KEY")),
            "twilio_configured": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
            "meta_whatsapp_configured": bool(os.environ.get("META_WHATSAPP_TOKEN"))
        }
    }), 200
