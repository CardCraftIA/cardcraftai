# Atlas — orientação de compra de cartas

Data de revisão: 2026-11-22 (Brasil). Apenas staging.

## Lacuna e entrega

O usuário enviou a frase `onde consigo comprar cartas raras`, que não tinha resposta local. Foi adicionado reconhecimento de perguntas completas sobre onde comprar/encontrar cartas raras e avulsas, e sobre avulsas versus boosters, em PT/EN/ES. A resposta inclui links públicos sem parâmetros de afiliado para a seção Pokémon da MYP Cards e o localizador oficial Pokémon. Orientações são identificadas como editoriais; referências não significam confirmação de uma oferta.

A orientação sobre MYP é condicional a Pokémon no Brasil. Não confirma estoque, preços, autenticidade, reputação de um vendedor nem menor preço. Conferir edição, condição, fotos, frete e devolução é orientação editorial. Perguntas específicas com preço, carta em contexto, anexos ou solicitações adicionais não recebem uma resposta genérica como se fossem solucionadas.

## Fontes verificadas

- https://mypcards.com/pokemon — página pública com seção e filtros de cartas avulsas. Nenhum preço ou anúncio foi importado.
- https://support.pokemon.com/hc/en-us/articles/360000634514-How-can-I-find-where-Pok%C3%A9mon-products-are-available-to-buy — indica o localizador https://events.pokemon.com/en-us/locations; artigo atualizado em 30/01/2026.
- https://support.pokemon.com/hc/en-us/articles/360001024394-What-types-of-Trading-Card-Game-products-are-available — conteúdo aleatório de boosters. Fonte já lida na etapa anterior desta sessão.

A consulta direta à Liga Pokémon retornou HTTP 403; não foi usada para uma nova indicação no app. Resumos originais, sem imagens copiadas e sem presumir licença aberta para importação de catálogos.

## Validação e limites

229 testes passaram: `cd web && node --experimental-strip-types --test scripts/*.test.mjs`.
Inclui 24 formulações de compra, sete de comparação entre avulsas e boosters, ausência de rede, idiomas, pontuação/aspas, limites das respostas e recusa de pedidos compostos ou que exigem dados atuais. Os testes existentes continuam passando.

Não foi executado fluxo autenticado completo nesta etapa. As respostas são locais e a política de cotas permanece a existente. O reconhecimento ainda usa padrões controlados, não compreensão geral. Falhas do provedor para outros assuntos não foram resolvidas nesta alteração. Main, produção e Supabase não foram modificados.
