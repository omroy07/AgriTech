import os
import time
from datetime import datetime


class HealthChecker:
    """Health check utilities for monitoring application status."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def check_gemini_api(self):
        """Check if Gemini API key is configured."""
        api_key = os.environ.get('GEMINI_API_KEY')
        return {
            'name': 'gemini_api',
            'status': 'healthy' if api_key else 'unhealthy',
            'message': 'API key configured' if api_key else 'API key missing'
        }
    
    def check_firebase(self):
        """Check if Firebase configuration is available."""
        required_keys = [
            'FIREBASE_API_KEY',
            'FIREBASE_PROJECT_ID',
            'FIREBASE_APP_ID'
        ]
        missing = [k for k in required_keys if not os.environ.get(k)]
        
        return {
            'name': 'firebase',
            'status': 'healthy' if not missing else 'unhealthy',
            'message': 'All keys configured' if not missing else f'Missing: {missing}'
        }
    
    def check_redis(self):
        """Check Redis connection for Celery."""
        try:
            import redis
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            return {
                'name': 'redis',
                'status': 'healthy',
                'message': 'Redis connection successful'
            }
        except Exception as e:
            return {
                'name': 'redis',
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_ml_models(self):
        """Check if ML models are loadable."""
        try:
            import joblib
            import os as os_module
            
            base_dir = os_module.path.dirname(os_module.path.dirname(os_module.path.dirname(__file__)))
            model_path = os_module.path.join(base_dir, "crop_recommendation", "model", "rf_model.pkl")
            
            if os_module.path.exists(model_path):
                return {
                    'name': 'ml_models',
                    'status': 'healthy',
                    'message': 'Crop model available'
                }
            else:
                return {
                    'name': 'ml_models',
                    'status': 'degraded',
                    'message': 'Crop model file not found'
                }
        except Exception as e:
            return {
                'name': 'ml_models',
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def get_uptime(self):
        """Get application uptime."""
        uptime = datetime.utcnow() - self.start_time
        return {
            'started_at': self.start_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds())
        }
    
    def liveness_check(self):
        """Simple liveness check - is the app running?"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def readiness_check(self):
        """Full readiness check - are all dependencies available?"""
        checks = [
            self.check_gemini_api(),
            self.check_firebase(),
            self.check_redis(),
            self.check_ml_models()
        ]
        
        overall_status = 'healthy'
        for check in checks:
            if check['status'] == 'unhealthy':
                overall_status = 'unhealthy'
                break
            elif check['status'] == 'degraded' and overall_status == 'healthy':
                overall_status = 'degraded'
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': checks,
            **self.get_uptime()
        }


# Global health checker instance
health_checker = HealthChecker()
