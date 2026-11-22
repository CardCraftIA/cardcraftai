# Atlas — início de coleção

Data: 2026-11-22. Alteração somente em staging.

O print do usuário revelou uma lacuna: `quais cartas voce recomendaria para eu iniciar minha coleção?` não tinha resposta local. Foi adicionado um guia editorial de início de coleção, separado das definições de catálogo, com reconhecimento de frases completas e variações em português, inglês e espanhol. O reparo ortográfico cobre também começar/iniciar/colecionar em um vocabulário restrito.

A resposta propõe foco por preferências e orçamento, apresenta personagens apenas como exemplos condicionais a Pokémon, distingue busca por cartas avulsas de boosters aleatórios e indica que jogar e colecionar podem ter objetivos distintos. Não recomenda uma edição específica, não informa preços e não promete valorização. Sugestões de foco, lista curta e orçamento são orientação editorial do Atlas, não recomendação oficial de compra.

Fontes públicas lidas em 2026-11-22:
- https://parents.pokemon.com/en-us/trading-card-game/ (colecionar personagens favoritos, jogar e decks pré-construídos).
- https://support.pokemon.com/hc/en-us/articles/360001024394-What-types-of-Trading-Card-Game-products-are-available (conteúdo aleatório dos boosters e conteúdo fixo de decks; artigo indica atualização em 30/01/2026).

Resumos originais curtos, sem importação de imagens nem presunção de licença aberta. Não foram criados registros confirmados no catálogo.

Validação: 196 testes passaram, incluindo 23 frases novas (a frase exata do print e sua versão com aspas), ausência de rede, idiomas, condições de contexto, recusa de pedidos compostos, preços e garantias de investimento. Comando: `cd web && node --experimental-strip-types --test scripts/*.test.mjs`.

Limites: reconhecimento por padrões, não compreensão geral de linguagem. Não foi implementado acompanhamento local de preferências pelo histórico. O fluxo autenticado completo não foi executado nesta etapa; a compilação remota deve ser verificada após a atualização da branch. A cota de respostas substantivas permanece igual; main, produção e Supabase não são alterados.
