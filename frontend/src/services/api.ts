/**
 * Minimal API client. Phase 1 only needs a health check; incident,
 * knowledge, and agent endpoints are added to this client as those
 * API routers are implemented in later phases.
 */

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface HealthResponse {
  status: string;
  service: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

export { API_BASE_URL };
