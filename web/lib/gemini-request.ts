import {HttpError} from './limits.ts';

// Never log provider bodies, headers, URLs, prompts, attachments or raw errors.
export async function geminiRequest(url: string, init: RequestInit, transport: typeof fetch = fetch): Promise<Response> {
  let response: Response;
  try {
    response = await transport(url, init);
  } catch (error) {
    const timeout = error instanceof Error && ['TimeoutError', 'AbortError'].includes(error.name);
    console.error('[atlas-provider]', JSON.stringify({category: timeout ? 'timeout' : 'network'}));
    throw new HttpError(503, 'O provedor de IA não respondeu.');
  }
  if (!response.ok) {
    const status = response.status;
    const category = status === 429 ? 'quota_or_rate_limit'
      : status === 401 || status === 403 ? 'authentication_or_permission'
      : status === 404 ? 'model_or_endpoint_unavailable'
      : status === 400 ? 'invalid_request_or_key'
      : status >= 500 ? 'provider_unavailable' : 'provider_rejected';
    console.error('[atlas-provider]', JSON.stringify({category, status}));
    await response.body?.cancel().catch(() => {});
    throw new HttpError(503, 'O provedor de IA não respondeu.');
  }
  return response;
}
