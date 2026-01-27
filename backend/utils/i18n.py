from flask import request, g

LOCALE_TO_NAME = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu'
}

TRANSLATIONS = {
    'en': {
        'error_missing_fields': 'Missing required fields',
        'error_user_not_found': 'User not found',
        'error_invalid_token': 'Invalid or expired token',
        'loan_processed_success': 'Loan processed successfully',
        'notification_loan_ready_title': 'Loan Eligibility Analysis Complete',
        'notification_loan_ready_msg': 'Your agricultural loan eligibility report is now ready.',
        'notification_crop_ready_title': 'Crop Recommendation Ready',
        'notification_crop_ready_msg': 'The AI has recommended {crop} for your farm.',
        'welcome_farmer': 'Welcome, Farmer!',
    },
    'hi': {
        'error_missing_fields': 'आवश्यक फ़ील्ड गायब हैं',
        'error_user_not_found': 'उपयोगकर्ता नहीं मिला',
        'error_invalid_token': 'अमान्य या समाप्त टोकन',
        'loan_processed_success': 'ऋण सफलतापूर्वक संसाधित किया गया',
        'notification_loan_ready_title': 'ऋण पात्रता विश्लेषण पूरा हुआ',
        'notification_loan_ready_msg': 'आपकी कृषि ऋण पात्रता रिपोर्ट अब तैयार है।',
        'notification_crop_ready_title': 'फसल की सिफारिश तैयार है',
        'notification_crop_ready_msg': 'एआई ने आपके खेत के लिए {crop} की सिफारिश की है।',
        'welcome_farmer': 'किसान भाई, आपका स्वागत है!',
    },
    'bn': {
        'error_missing_fields': 'প্রয়োজনীয় তথ্য missing',
        'error_user_not_found': 'ব্যবহারকারী খুঁজে পাওয়া যায়নি',
        'error_invalid_token': 'অবৈধ বা মেয়াদোত্তীর্ণ টোকেন',
        'loan_processed_success': 'ঋণ সফলভাবে প্রক্রিয়া করা হয়েছে',
        'notification_loan_ready_title': 'ঋণ যোগ্যতার বিশ্লেষণ সম্পন্ন হয়েছে',
        'notification_loan_ready_msg': 'আপনার কৃষি ঋণের যোগ্যতার রিপোর্ট এখন প্রস্তুত।',
        'notification_crop_ready_title': 'ফসল সুপারিশ প্রস্তুত',
        'notification_crop_ready_msg': 'AI আপনার খামারের জন্য {crop} সুপারিশ করেছে।',
        'welcome_farmer': 'স্বাগতম, কৃষক বন্ধু!',
    },
    'te': {
        'error_missing_fields': 'అవసరమైన ఫీల్డ్లు లేవు',
        'error_user_not_found': 'వినియోగదారు కనుగొనబడలేదు',
        'error_invalid_token': 'చెల్లని లేదా గడువు ముగిసిన టోకెన్',
        'loan_processed_success': 'రుణం విజయవంతంగా ప్రాసెస్ చేయబడింది',
        'notification_loan_ready_title': 'రుణ అర్హత విశ్లేషణ పూర్తయింది',
        'notification_loan_ready_msg': 'మీ వ్యవసాయ రుణ అర్హత నివేదిక ఇప్పుడు సిద్ధంగా ఉంది.',
        'notification_crop_ready_title': 'పంట సిఫార్సు సిద్ధంగా ఉంది',
        'notification_crop_ready_msg': 'AI మీ పొలం కోసం {crop}ను సిఫార్సు చేసింది.',
        'welcome_farmer': 'రైతు సోదరులకు స్వాగతం!',
    }
}

def get_locale(user_id=None):
    """Detect locale from header or user preference."""
    # Priority 1: Check if locale is already set in g
    if hasattr(g, 'locale'):
        return g.locale
    
    # Priority 2: Check database for user preference
    if user_id:
        from backend.models import User
        user = User.query.get(user_id)
        if user and user.language_preference:
            return user.language_preference
    
    # Priority 3: Check Accept-Language header
    header_lang = request.headers.get('Accept-Language', 'en').split(',')[0].split('-')[0]
    if header_lang in TRANSLATIONS:
        return header_lang
    
    return 'en'

def t(key, locale=None, **kwargs):
    """Translate a key to the current locale."""
    if not locale:
        locale = get_locale()
    
    # Fallback to English if key or locale not found
    text = TRANSLATIONS.get(locale, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))
    
    if kwargs:
        return text.format(**kwargs)
    return text

def gettext(key, **kwargs):
    return t(key, **kwargs)
