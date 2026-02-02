from flask_babel import Babel
from flask import request, current_app

babel = Babel()

def get_locale():
    # 1. Check from URL parameter
    lang = request.args.get('lang')
    if lang in ['en', 'hi', 'mr']:
        return lang
    
    # 2. Check from Cookie
    lang = request.cookies.get('lang')
    if lang in ['en', 'hi', 'mr']:
        return lang
        
    # 3. Check from Accept-Language header
    return request.accept_languages.best_match(['en', 'hi', 'mr']) or 'en'
