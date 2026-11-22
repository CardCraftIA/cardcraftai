# Atlas — tolerância de entrada e esclarecimento

Data: 2026-11-22. Somente staging.

## Correção reproduzida

A pergunta do print, “Qual a diferença entre sleeve e toploader?”, com aspas curvas externas, retornava null na busca local; a versão sem aspas encontrava o guia sleeves. Removemos apenas pares externos de aspas e pontuação de término, preservando pedidos adicionais dentro/fora das aspas.

## Comportamento

- Reconhecimento exato tem prioridade. Depois, até duas correções de uma edição por palavra (inclui transposição) são permitidas apenas em vocabulário controlado de TCG e perguntas. Candidatos ambíguos são recusados. A frase inteira ainda deve corresponder a um assunto suportado.
- Abreviações como oq, o q, oque, q e eh; fragmentos controlados como carta nm, sleeve, sleeve ou toploader e holo vs reverse holo.
- Não corrige nomes/códigos de cartas, valores ou negações. Não extrai palavras-chave de um pedido composto para responder apenas parte dele.
- Pedidos curtos reconhecidos como ambíguos recebem esclarecimento em português, inglês ou espanhol, conforme a expressão. Termos isolados sem evidência de idioma usam português.
- Esclarecimento exige conta autenticada, mas sai antes de consultar catálogo, Gemini e reservar pergunta. Tem rótulo próprio na interface, sem alegação de fonte revisada ou geração por IA. Anexo e carta em contexto continuam pelo fluxo existente.
- Os prompts pedem que o usuário inclua o contexto na próxima pergunta; não foi implementada resolução local do histórico da conversa.

## Validação

171 testes passaram em `cd web && node --experimental-strip-types --test scripts/*.test.mjs`.
A regressão com aspas inclui os 75 cenários locais em seis estilos de aspas, espaços, pontuação externa e pares aninhados. Novos testes cobrem 22 entradas abreviadas/com erros, 13 pedidos de esclarecimento, ausência de rede, contextos e pedidos compostos e posição do esclarecimento antes da reserva. Testes de reserva existentes continuam passando.

Não é um modelo de linguagem independente e não reconhece toda frase ou erro possível. Testes automatizados não substituem validação autenticada no app; nenhum fluxo autenticado completo foi executado nesta etapa. Main, produção e Supabase não foram modificados.
