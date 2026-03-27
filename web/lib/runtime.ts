const DEFAULT_API_BASE_URL = "http://localhost:8000";

function trimTrailingSlash(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL;
  return trimTrailingSlash(configured || DEFAULT_API_BASE_URL);
}

export function getWsBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_WS_URL;
  if (configured) {
    return trimTrailingSlash(configured);
  }
  const apiUrl = getApiBaseUrl();
  if (apiUrl.startsWith("https://")) {
    return apiUrl.replace("https://", "wss://");
  }
  return apiUrl.replace("http://", "ws://");
}

export function apiV1(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBaseUrl()}/api/v1${normalized}`;
}
