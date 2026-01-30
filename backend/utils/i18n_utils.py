from flask_babel import force_locale, gettext as _

TRANSLATIONS = {
    'hi': {
        'crop_prediction_ready_title': 'फसल भविष्यवाणी तैयार है',
        'crop_prediction_ready_msg': 'AI ने आपके खेत के लिए {crop} की सिफारिश की है।',
        'loan_analysis_complete_title': 'ऋण विश्लेषण पूरा हुआ',
        'loan_analysis_complete_msg': 'आपका ऋण योग्यता विश्लेषण तैयार है। हम अभी आपकी PDF रिपोर्ट तैयार कर रहे हैं।',
        'pdf_report_ready_title': 'PDF रिपोर्ट तैयार है',
        'pdf_report_ready_msg': 'आपकी पेशेवर ऋण योग्यता रिपोर्ट ({filename}) अब डाउनलोड के लिए उपलब्ध है।',
        'report_generation_failed_title': 'रिपोर्ट तैयार करना विफल रहा',
        'report_generation_failed_msg': 'आपकी PDF रिपोर्ट तैयार करते समय हमें एक त्रुटि का सामना करना पड़ा। कृपया बाद में पुनः प्रयास करें।'
    },
    'mr': {
        'crop_prediction_ready_title': 'पीक अंदाज तयार आहे',
        'crop_prediction_ready_msg': 'AI ने तुमच्या शेतासाठी {crop} ची शिफारस केली आहे.',
        'loan_analysis_complete_title': 'कर्ज विश्लेषण पूर्ण झाले',
        'loan_analysis_complete_msg': 'तुमचे कर्ज पात्रता विश्लेषण तयार आहे. आम्ही आता तुमचा PDF अहवाल तयार करत आहोत.',
        'pdf_report_ready_title': 'PDF अहवाल तयार आहे',
        'pdf_report_ready_msg': 'तुमचा व्यावसायिक कर्ज पात्रता अहवाल ({filename}) आता डाउनलोड करण्यासाठी उपलब्ध आहे.',
        'report_generation_failed_title': 'अहवाल जनरेशन अयशस्वी',
        'report_generation_failed_msg': 'तुमचा PDF अहवाल तयार करताना आम्हाला त्रुटी आली. कृपया नंतर पुन्हा प्रयत्न करा.'
    },
    'en': {
        'crop_prediction_ready_title': 'Crop Prediction Ready',
        'crop_prediction_ready_msg': 'The AI has recommended {crop} for your farm.',
        'loan_analysis_complete_title': 'Loan Analysis Complete',
        'loan_analysis_complete_msg': 'Your loan eligibility analysis is ready. We are generating your PDF report now.',
        'pdf_report_ready_title': 'PDF Report Ready',
        'pdf_report_ready_msg': 'Your professional loan eligibility report ({filename}) is now available for download.',
        'report_generation_failed_title': 'Report Generation Failed',
        'report_generation_failed_msg': 'We encountered an error while generating your PDF report. Please try again later.'
    }
}

def get_translated_string(key, lang='en', **kwargs):
    lang_batch = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    string = lang_batch.get(key, TRANSLATIONS['en'].get(key, key))
    return string.format(**kwargs)
