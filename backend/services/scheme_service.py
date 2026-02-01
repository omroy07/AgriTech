import json
import os
from backend.extensions.cache import cache
from backend.utils.logger import logger

class SchemeService:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'schemes.json')

    def get_all_schemes(self):
        """Fetch all schemes from JSON and cache them."""
        cached_schemes = cache.get('all_agricultural_schemes')
        if cached_schemes:
            return cached_schemes

        try:
            if not os.path.exists(self.data_path):
                return []
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                schemes = json.load(f)
            
            # Cache for 24 hours
            cache.set('all_agricultural_schemes', schemes, timeout=86400)
            return schemes
        except Exception as e:
            logger.error(f"Failed to load schemes: {str(e)}")
            return []

    def get_schemes_by_category(self, category):
        """Get schemes filtered by category with caching."""
        cache_key = f'schemes_cat_{category}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        all_schemes = self.get_all_schemes()
        filtered = [s for s in all_schemes if s.get('category') == category]
        
        cache.set(cache_key, filtered, timeout=3600)
        return filtered

    def invalidate_cache(self):
        """Invalidate schemes cache (e.g. after update)."""
        cache.delete('all_agricultural_schemes')
        logger.info("Agricultural schemes cache invalidated")

scheme_service = SchemeService()
