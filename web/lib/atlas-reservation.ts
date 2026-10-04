import {randomUUID} from 'node:crypto';
import {HttpError} from './limits.ts';

type RpcResult = {data: Record<string, unknown> | null; error: unknown};
type RpcClient = {rpc: (name: string, args: Record<string, unknown>) => PromiseLike<RpcResult>};

// The capability never leaves the server. A client cannot refund a server request.
export async function withAtlasReservation<T>(
  db: RpcClient, requestId: string, work: () => Promise<T>,
  limitMessage = 'Você usou suas cinco perguntas. Consulte os planos para saber quando o upgrade estará disponível.',
): Promise<{value: T; remaining: unknown}> {
  const token = randomUUID();
  const args = {p_request_id: requestId, p_token: token};
  const claim = await db.rpc('reserve_atlas_web_question', args);
  if (claim.error || typeof claim.data?.allowed !== 'boolean') {
    throw new HttpError(503, 'Não foi possível reservar sua pergunta. Tente novamente mais tarde.');
  }
  if (claim.data.duplicate) throw new HttpError(409, 'Esta solicitação já foi recebida.');
  if (!claim.data.allowed) throw new HttpError(402, limitMessage);

  async function settle(success: boolean) {
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const result = await db.rpc('settle_atlas_web_question', {...args, p_success: success});
        if (!result.error && result.data?.status) return result.data;
      } catch { /* Retry the same idempotent settlement once. */ }
    }
    return null;
  }

  let value: T;
  try {
    value = await work();
  } catch {
    const result = await settle(false);
    throw new HttpError(503, result?.status === 'refunded'
      ? 'Não foi possível gerar a resposta. Sua pergunta foi devolvida ao limite disponível.'
      : 'Não foi possível gerar a resposta. A reserva pendente será reconciliada na próxima solicitação válida após dois minutos.');
  }
  const result = await settle(true);
  if (result?.status !== 'completed') {
    throw new HttpError(503, 'Não foi possível confirmar a resposta. Aguarde dois minutos antes de tentar novamente.');
  }
  return {value, remaining: result.remaining};
}
