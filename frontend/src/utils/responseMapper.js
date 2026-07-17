/**
 * Normalize backend chat responses into UI-friendly objects.
 * @param {import('axios').AxiosResponse} response
 * @returns {{ success: boolean, error?: string, domain?: string, data?: any, response?: string }}
 */
export function mapChatResponse(response) {
  const payload = response?.data || {}
  return {
    success: payload.success === true,
    error: payload.error || null,
    domain: payload.domain || 'general',
    data: payload.data || null,
    response: payload.response || '',
    sources: Array.isArray(payload.sources) ? payload.sources : null,
    used_rag: payload.used_rag ?? null,
  }
}

/**
 * Convert a generic API response into a user-facing result object.
 * @param {import('axios').AxiosResponse} response
 * @returns {{ success: boolean, error: string | null, data: any }}
 */
export function mapApiResult(response) {
  const payload = response?.data || {}
  return {
    success: payload.success === true,
    error: payload.error || null,
    data: payload.data ?? payload,
  }
}
