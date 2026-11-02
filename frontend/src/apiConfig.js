/**
 * Centralized API configuration and dynamic base URL resolution for FedSentinel-X.
 *
 * Ensures seamless operation across:
 *   1. Local development (http://127.0.0.1:8000)
 *   2. Cloud deployments (Vercel edge -> https://fedsentinel-api.onrender.com)
 *   3. Preview and custom domains
 */

export function getApiBaseUrl() {
  // 1. Explicit Vite environment variable (injected at build time)
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    const envUrl = String(import.meta.env.VITE_API_BASE_URL).trim()
    if (envUrl && envUrl !== 'undefined' && envUrl !== 'null') {
      return envUrl.replace(/\/+$/, '')
    }
  }

  // 2. Client-side runtime detection: If running on a cloud host (e.g. *.vercel.app or any non-localhost)
  if (typeof window !== 'undefined' && window.location) {
    const hostname = window.location.hostname.toLowerCase()
    const isLocal =
      hostname === 'localhost' ||
      hostname === '127.0.0.1' ||
      hostname.startsWith('192.168.') ||
      hostname.startsWith('10.') ||
      hostname.endsWith('.local')

    if (!isLocal) {
      return 'https://fedsentinel-api.onrender.com'
    }
  }

  // 3. Local development fallback
  return 'http://127.0.0.1:8000'
}

export const API_BASE_URL = getApiBaseUrl()
