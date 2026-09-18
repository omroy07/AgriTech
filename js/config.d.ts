/**
 * Type declarations for AgriTechConfig
 */

export interface StorageKeysConfig {
  token: string;
  refreshToken: string;
  user: string;
  theme: string;
  language: string;
  diseaseHistory: string;
  favorites: string;
  configEnv: string;
  apiBase: string;
}

export interface FeatureFlagsConfig {
  enableAiDiseaseDiagnosis: boolean;
  enablePredictionComparison: boolean;
  enableSeedlingClassification: boolean;
  enableWeatherBanner: boolean;
  enableSpatialAnalytics: boolean;
  enableCropRecommendation: boolean;
  enableCarbonPortal: boolean;
  enableVoiceInput: boolean;
  enableOfflineCache: boolean;
  [key: string]: boolean;
}

export interface ApiEndpointsConfig {
  config: string;
  auth: string;
  aiDisease: string;
  cropAdvisory: string;
  spatial: string;
  weather: string;
  marketplace: string;
  carbon: string;
  notifications: string;
  forum: string;
  insurance: string;
  firebase: string;
  [key: string]: string;
}

export interface ModelParametersConfig {
  diseaseConfidenceThreshold: number;
  maxUploadSizeMb: number;
  maxUploadSizeBytes: number;
  supportedImageTypes: string[];
}

export interface AgriTechConfigStatic {
  readonly env: 'development' | 'staging' | 'production' | 'test';
  readonly storageKeys: StorageKeysConfig;
  readonly featureFlags: FeatureFlagsConfig;
  get<T = any>(path?: string, defaultValue?: T): T;
  isFeatureEnabled(flagName: keyof FeatureFlagsConfig | string): boolean;
  getApiUrl(endpointKey: keyof ApiEndpointsConfig | string): string;
  syncWithBackend(): Promise<any>;
  onReady(callback: (config: any) => void): void;
}

declare global {
  interface Window {
    AgriTechConfig: AgriTechConfigStatic;
    AGRITECH_API_BASE?: string;
  }
}

export const AgriTechConfig: AgriTechConfigStatic;
export default AgriTechConfig;
