# Atlas: compreensão com modelo independente — preparação em staging

## Estado real

Esta entrega prepara a integração; **não instala, treina nem ativa um modelo**. Na inspeção do ambiente Preview/staging em 23/11/2026, havia apenas GEMINI_MODEL e GEMINI_API_KEY para geração. Não foi localizado endpoint de inferência próprio. A capacidade de compreensão do novo caminho ainda não foi medida.

O comportamento existente é preservado até uma troca explícita de configuração. Perguntas reconhecidas pela base continuam usando respostas revisadas. Selecionar `openai-compatible` usa exclusivamente o servidor configurado para as demais perguntas; falhas não recorrem ao Gemini.

## Implementação

- Provedor selecionável: `gemini` (compatibilidade com staging existente), `openai-compatible` ou `disabled`.
- Endpoint HTTPS autenticado definido somente no servidor. O navegador não escolhe endereço, modelo ou credencial. Redirecionamentos são recusados.
- As últimas quatro trocas completas da conversa acompanham a pergunta original, preservando erros ortográficos, negações e identificadores. Esse histórico é contexto não confiável enviado pelo navegador; não é memória persistente ou verificação de fatos.
- Os 18 tópicos revisados existentes são enviados integralmente ao modelo, sem duplicar os textos. A base é pequena: cerca de 10 mil caracteres em português. O modelo pode traduzir e relacionar assuntos. Não há busca vetorial/embeddings nesta etapa; enviar toda a base evita excluir tópicos por correspondência de palavras.
- Instruções para interpretar intenção, perguntas compostas, correções e mudanças de assunto; perguntar quando houver ambiguidade. Instruções não garantem qualidade nem eliminam alucinações.
- Saída JSON validada. Referências são selecionadas somente por IDs existentes e resolvidas no servidor. Isso evita referências inventadas, mas **não verifica automaticamente se cada afirmação é sustentada pela fonte**.
- Respostas geradas continuam identificadas como IA. Uma explicação gerada não vira conhecimento revisado ou registro do catálogo.
- Esclarecimentos locais continuam gratuitos. Esclarecimentos do modelo devolvem a reserva antes da resposta ser liberada. O modelo precisa de uma reserva disponível para ser chamado; o limite esgotado impede sua execução, mesmo que ele viesse a pedir esclarecimento.
- Falhas, JSON inválido, respostas truncadas e referências desconhecidas seguem o mecanismo existente de restituição. Sem alteração de schema, RLS ou dados do Supabase.
- Primeira integração própria apenas para texto. Anexos são recusados antes da reserva; nunca descartados silenciosamente ou enviados ao Gemini quando o provedor independente está selecionado.

## Verificação

`cd web && node --experimental-strip-types --test scripts/*.test.mjs`

Resultado local: **250 testes passaram**, incluindo os 229 existentes (uma asserção textual de configuração atualizada) e 21 novos testes de protocolo, contexto, fontes, falhas e restituição. Os testes de provedor usam transporte simulado; não comprovam compreensão linguística. A compilação da implantação será verificada separadamente.

Foram preparados **24 cenários de avaliação real** em `web/scripts/fixtures/atlas-comprehension.mjs`: escrita informal, perguntas indiretas, comparação, negação, perguntas compostas, continuidade, correção explícita, mudança de jogo, ausência de fonte, preços atuais e tentativas de instruir o modelo a inventar respostas.

Listar sem rede:

```sh
cd web
node --experimental-strip-types scripts/evaluate-atlas-model.mjs
```

Após configurar um servidor próprio, executar um caso real (faz uma chamada ao modelo):

```sh
node --experimental-strip-types scripts/evaluate-atlas-model.mjs --live --case=history-correction
```

Omitir `--case` executa os 24 casos sequencialmente. Credenciais ficam apenas nas variáveis de ambiente. O relatório apresenta resposta, critério esperado e latência; o veredicto permanece `needs_human_review`. Não calcula uma falsa taxa de acerto com palavras-chave. Avaliação real **não executada** nesta entrega.

## Ativação concreta pendente

1. Escolher servidor/computador e orçamento. Selecionar modelo multilíngue com licença adequada e desempenho em português, após avaliar hardware e custo. Não pressupor equivalência ao ChatGPT nem contratar GPU automaticamente.
2. Disponibilizar servidor de inferência protegido por autenticação e HTTPS, acessível pela Vercel, com API `/v1/chat/completions`, JSON mode e pelo menos 16 mil tokens de contexto como ponto inicial a validar. O código não exige usar a API da OpenAI; o protocolo é compatível com servidores como vLLM e llama.cpp.
3. Medir os 24 casos e variações novas. Conferir compreensão da intenção, uso do histórico, cobertura de perguntas compostas, limites das fontes, linguagem e latência. Bloquear ativação se houver invenção de preço/estoque/autenticidade, perda sistemática de negação ou vazamento de instruções.
4. Configurar somente Preview da branch staging: `ATLAS_LLM_PROVIDER=openai-compatible`, `ATLAS_LLM_BASE_URL=https://SEU-SERVIDOR/v1`, `ATLAS_LLM_MODEL`, `ATLAS_LLM_API_KEY`. Não enviar segredos pelo chat nem usar variáveis `NEXT_PUBLIC_`.
5. Reimplantar staging; testar login, respostas próprias, conversa contextual, restituição e limite pela interface. A chamada deve terminar em 40 segundos; modelo lento deve ser otimizado ou outra infraestrutura escolhida.
6. Depois de validar a independência, retirar as credenciais Gemini de staging em mudança separada e explícita. Main e produção não foram alterados.

Rollback da seleção: usar `disabled` para manter somente base/catálogo ou restaurar a configuração anterior caso autorizado. O código não troca provedores sozinho.

## Fontes técnicas consultadas

- vLLM — servidor compatível: https://docs.vllm.ai/en/stable/serving/openai_compatible_server/
- llama.cpp — servidor, JSON e API de chat: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

São referências de implementação, não evidência de que qualquer modelo específico já foi escolhido, hospedado ou aprovado para Atlas.
