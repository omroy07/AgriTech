translations = {
    'en': {
        'welcome': 'Welcome to AgriTech',
        'dashboard': 'Dashboard',
    },
    'hi': {
        'welcome': 'AgriTech me svagat hai',
        'dashboard': 'Dashboard',
    }
}

def get_translation(lang, key):
    return translations.get(lang, {}).get(key, translations['en'].get(key, key))

