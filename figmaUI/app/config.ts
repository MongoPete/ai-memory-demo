// API Configuration
// Uses VITE_API_BASE_URL from environment variables, defaults to localhost for development
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8182';

export const config = {
  apiBaseUrl: API_BASE_URL,
  healthCheckEndpoint: `${API_BASE_URL}/health`,
  conversationEndpoint: `${API_BASE_URL}/conversation/`,
  retrieveMemoryEndpoint: `${API_BASE_URL}/retrieve_memory/`,
  memoriesEndpoint: (userId: string) => `${API_BASE_URL}/memories/${userId}`,
};
