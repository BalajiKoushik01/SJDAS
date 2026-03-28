export function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}

export function getWsBaseUrl() {
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${protocol}://${window.location.hostname}:8000`;
  }
  return 'ws://localhost:8000';
}

/**
 * Enhanced API Wrapper:
 * Handles authentication, cross-origin requests, and JSON parsing.
 */
export async function apiV1(path: string, options: RequestInit = {}) {
  const isServer = typeof window === 'undefined';
  const base = isServer 
    ? (process.env.BACKEND_URL || 'http://localhost:8000') 
    : `${window.location.protocol}//${window.location.hostname}:8000`;
  
  const url = `${base}/api/v1${path.startsWith('/') ? '' : '/'}${path}`;
  
  // Auto-append Auth Token
  const token = !isServer ? localStorage.getItem('auth_token') : null;
  const headers = new Headers(options.headers || {});
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error ${response.status}: ${errorBody || response.statusText}`);
  }

  // Handle empty or streaming responses
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  return response.text();
}
