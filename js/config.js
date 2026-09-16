/**
 * AgriTech Centralized Frontend Configuration & Environment Management
 * Provides typed, immutable runtime configurations, feature flags, API route mappings, and storage registries.
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AgriTechConfig = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // --- 1. Environment Detection ---
  function detectEnvironment() {
    // Check for explicit developer override in localStorage
    try {
      const storedEnv = localStorage.getItem('AGRITECH_CONFIG_ENV');
      if (storedEnv && ['development', 'staging', 'production', 'test'].includes(storedEnv.toLowerCase())) {
        return storedEnv.toLowerCase();
      }
    } catch (e) {
      // localStorage may be unavailable
    }

    if (typeof window === 'undefined' || !window.location) {
      return 'development';
    }

    const hostname = window.location.hostname || '';
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.endsWith('.local')) {
      return 'development';
    }
    if (hostname.includes('staging') || hostname.includes('dev.')) {
      return 'staging';
    }
    if (hostname === '' || window.location.protocol === 'file:') {
      return 'development';
    }
    return 'production';
  }

  const CURRENT_ENV = detectEnvironment();

  // --- 2. API Base URL Resolution ---
  function resolveApiBaseUrl() {
    if (typeof window !== 'undefined') {
      if (window.AGRITECH_API_BASE) {
        return window.AGRITECH_API_BASE;
      }
      try {
        const storedBase = localStorage.getItem('AGRITECH_API_BASE');
        if (storedBase) return storedBase;
      } catch (e) {}

      // If running on a local frontend dev server (e.g., Live Server on port 5500 or Vite on 3000), default backend to 5000
      const port = window.location.port;
      if (port && port !== '5000' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
        return 'http://127.0.0.1:5000';
      }
    }
    return '';
  }

  const API_BASE = resolveApiBaseUrl();

  // --- 3. Base Configuration Schema ---
  const _configData = {
    appName: 'AgriTech',
    version: '1.0.0',
    env: CURRENT_ENV,
    isDev: CURRENT_ENV === 'development',
    isProd: CURRENT_ENV === 'production',

    // API & Network Endpoints
    api: {
      baseUrl: API_BASE,
      prefix: '/api/v1',
      timeoutMs: 15000,
      endpoints: {
        config: '/api/v1/config',
        auth: '/api/v1/auth',
        aiDisease: '/api/v1/ai-disease',
        cropAdvisory: '/api/v1/crop-advisory',
        spatial: '/api/spatial',
        weather: '/api/v1/weather',
        marketplace: '/api/v1/market',
        carbon: '/api/v1/carbon',
        notifications: '/api/v1/notifications',
        forum: '/api/v1/forum',
        insurance: '/api/v1/insurance',
        firebase: '/api/v1/config/firebase',
      },
    },

    // Feature Flags (Gradual Rollouts & Toggle Control)
    featureFlags: {
      enableAiDiseaseDiagnosis: true,
      enablePredictionComparison: true,
      enableSeedlingClassification: true,
      enableWeatherBanner: true,
      enableSpatialAnalytics: true,
      enableCropRecommendation: true,
      enableCarbonPortal: true,
      enableVoiceInput: true,
      enableOfflineCache: true,
    },

    // Model & Upload Parameters
    models: {
      diseaseConfidenceThreshold: 75,
      maxUploadSizeMb: 10,
      maxUploadSizeBytes: 10 * 1024 * 1024,
      supportedImageTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
    },

    // Storage Key Names (Unified Single Source of Truth)
    storageKeys: {
      token: 'token',
      refreshToken: 'refreshToken',
      user: 'user',
      theme: 'theme',
      language: 'language',
      diseaseHistory: 'agritech_disease_prediction_history',
      favorites: 'agritech_favorites',
      configEnv: 'AGRITECH_CONFIG_ENV',
      apiBase: 'AGRITECH_API_BASE',
    },

    // Firebase Frontend Configuration
    firebase: {
      apiKey: '',
      authDomain: '',
      projectId: '',
      storageBucket: '',
      messagingSenderId: '',
      appId: '',
      measurementId: '',
    },
  };

  const _readyCallbacks = [];
  let _isSynced = false;

  // --- 4. Configuration Object Interface ---
  const AgriTechConfig = {
    /**
     * Get a configuration value by dot-notation path
     * @param {string} path e.g. 'api.endpoints.auth'
     * @param {*} defaultValue
     */
    get(path, defaultValue = undefined) {
      if (!path) return _configData;
      const keys = path.split('.');
      let current = _configData;
      for (const key of keys) {
        if (current === undefined || current === null || typeof current !== 'object') {
          return defaultValue;
        }
        current = current[key];
      }
      return current !== undefined ? current : defaultValue;
    },

    /**
     * Check if a feature flag is enabled
     * @param {string} flagName e.g. 'enablePredictionComparison'
     */
    isFeatureEnabled(flagName) {
      return Boolean(_configData.featureFlags[flagName]);
    },

    /**
     * Resolve full absolute or relative API URL for an endpoint
     * @param {string} endpointKey Key from api.endpoints
     */
    getApiUrl(endpointKey) {
      const endpoint = _configData.api.endpoints[endpointKey] || endpointKey;
      if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
        return endpoint;
      }
      return `${_configData.api.baseUrl}${endpoint}`;
    },

    /**
     * Access storage keys dictionary
     */
    get storageKeys() {
      return _configData.storageKeys;
    },

    /**
     * Access feature flags dictionary
     */
    get featureFlags() {
      return _configData.featureFlags;
    },

    /**
     * Access environment string
     */
    get env() {
      return _configData.env;
    },

    /**
     * Synchronize public configuration & feature flags from backend
     */
    async syncWithBackend() {
      if (typeof fetch === 'undefined') return _configData;

      const url = this.getApiUrl('config');
      try {
        const response = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
        if (response.ok) {
          const resJson = await response.json();
          const remoteData = resJson.data || resJson;

          if (remoteData.featureFlags) {
            Object.assign(_configData.featureFlags, remoteData.featureFlags);
          }
          if (remoteData.ai) {
            if (remoteData.ai.confidenceThreshold) {
              _configData.models.diseaseConfidenceThreshold = remoteData.ai.confidenceThreshold;
            }
            if (remoteData.ai.maxUploadSizeMb) {
              _configData.models.maxUploadSizeMb = remoteData.ai.maxUploadSizeMb;
              _configData.models.maxUploadSizeBytes = remoteData.ai.maxUploadSizeMb * 1024 * 1024;
            }
          }
          if (remoteData.firebase) {
            Object.assign(_configData.firebase, remoteData.firebase);
          }

          _isSynced = true;
          _readyCallbacks.forEach((cb) => {
            try {
              cb(_configData);
            } catch (err) {
              console.error('Error in config ready callback:', err);
            }
          });
        }
      } catch (err) {
        // Fallback to embedded defaults silently
        console.debug('AgriTechConfig: Backend config sync bypassed, using local defaults.', err.message);
      }

      return _configData;
    },

    /**
     * Register a callback when backend configuration has synced
     */
    onReady(callback) {
      if (typeof callback === 'function') {
        if (_isSynced) {
          callback(_configData);
        } else {
          _readyCallbacks.push(callback);
        }
      }
    },
  };

  // Auto-sync in browser environment after DOM load
  if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        AgriTechConfig.syncWithBackend();
      });
    } else {
      setTimeout(() => AgriTechConfig.syncWithBackend(), 10);
    }
  }

  return Object.freeze(AgriTechConfig);
});
