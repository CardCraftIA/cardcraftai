# Atlas — ampliação dos guias de colecionadores

Data: 2026-11-22. Publicação somente na staging. Continuação da bateria inicial de 71 cenários, descrita em atlas-collector-test-report-2026-11-22.md.

## Entrega

Nove temas com respostas originais e fontes públicas revisadas em português, inglês e espanhol: armazenamento; sleeves/toploaders; precauções com limpeza; graduação; Near Mint versus PSA 10; orientação de identificação de coleção; número de colecionador; promos; primeira edição/reimpressão.

As respostas são orientação geral. Não criam registros confirmados no catálogo, não avaliam uma carta física e não consultam preços atuais. Regras e termos de Pokémon são apresentados como específicos desse jogo.

## Resultado

- 131 testes passaram, incluindo 110 cenários de colecionadores e verificações adicionais/existentes.
- 75 cenários têm resposta local; 9 continuam como lacunas; 26 verificam proteção contra contexto inadequado, pedidos compostos ou idioma não coberto.
- Das 18 lacunas da bateria inicial, 9 agora têm orientação local. Os IDs foram preservados e os casos migrados guardam previousKind=gap.
- Os testes exercitam a função usada pela API e bloqueiam chamadas de rede. Não consumiram perguntas reais nem executaram inferência externa.
- A suíte testa assunto, idioma, proveniência e limites das respostas, além de recusar respostas genéricas quando há anexo ou uma edição em contexto.

## Fontes e revisão

Links constam das respostas com data de revisão 2026-11-22. Foram redigidos resumos curtos; nenhuma imagem, catálogo completo ou resposta anterior de modelo foi importada como dado confirmado. Não se presume licença aberta dos sites consultados.

- Ultra PRO: https://ultrapro.com/blogs/news/a-top-to-bottom-guide-on-toploaders
- PSA: https://www.psacard.com/info/get-started
- PSA: https://www.psacard.com/gradingstandards
- PSA: https://www.psacard.com/info/tcg/pokemon-basics-guide
- CGC: https://www.cgcgrading.com/news/articles/pokemon-first-editions-3RuIuDcH5mM8koeRHgmzrx/
- TCGplayer: https://help.tcgplayer.com/hc/en-us/articles/221430307-Card-Conditioning-Overview
- TCGplayer: https://help.tcgplayer.com/hc/en-us/articles/360025636074-What-are-the-rarities-of-Pok%C3%A9mon-TCG-cards
- Pokémon: https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/par_rulebook_en.pdf

A orientação de não aplicar álcool é uma precaução editorial conservadora baseada nas restrições de alteração/limpeza química da PSA; não é um procedimento de restauração autorizado pelo fabricante. A distinção entre NM e PSA 10 é uma comparação entre as escalas publicadas por TCGplayer e PSA.

## Limites

O reconhecimento permanece baseado em perguntas completas e termos controlados, não em um modelo de linguagem independente. O conjunto de testes orientou a implementação: os resultados não medem generalização a todas as perguntas reais. As lacunas não são contabilizadas como respostas corretas só porque retornam null.

Não foi testado o fluxo autenticado completo no navegador nesta etapa. Os testes existentes de reserva/devolução continuam passando, e o limite de cinco perguntas não mudou. Não houve alteração em main, Supabase ou credenciais.

## Lacunas restantes

- Vale a pena mandar minha carta para graduação?
- Quanto vale meu Charizard SM211 hoje?
- Quanto vale minha coleção?
- Onde comprar pelo menor preço?
- Carta japonesa vale mais que portuguesa?
- Como saber se uma carta é falsa?
- Minha carta é original?
- Como identificar uma carta paralela de One Piece?
- O que é Secret Rare no Yu-Gi-Oh?

## Reproduzir

`cd web && node --experimental-strip-types --test scripts/*.test.mjs`

A matriz completa está em web/scripts/fixtures/collector-questions.json.
