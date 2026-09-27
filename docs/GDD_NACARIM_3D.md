# Nacarim: Guardiões da Luz — GDD resumido (protótipo 3D)

## Visão

Jogo de ação 3D em terceira pessoa para navegador. O jogador controla Nilo na Ponte das Três Ilhas, protege o Núcleo de Luz e dissipa criaturas da Névoa. Cada fase dura cerca de 1 a 2 minutos; entre fases, Fragmentos de Luz podem ser trocados por melhorias. O protótipo é local e não possui contas, monetização ou ranking global.

## Ciclo

Escolher guardião (Nilo nesta versão) → cumprir um objetivo → ganhar pontuação e fragmentos → escolher melhorias → avançar. Ao perder toda a vida, mostrar recordes locais e permitir recomeçar. A progressão salva recorde de pontuação e fase no navegador, sem sincronização entre dispositivos.

| Fase | Objetivo | Novidades | Vitória |
| --- | --- | --- | --- |
| Ponte 1: Despertar | Dissipar 12 sombras | Rápidas; piras de luz | 12 dissipações |
| Ponte 2: Vigília | Sobreviver 60 segundos | Tanques mais resistentes | Cronômetro zerado com vida |
| Ponte 3: O Núcleo | Defender o Núcleo por 75 segundos | Atiradoras, projéteis e HP do Núcleo | Núcleo e jogador sobrevivem |
| Ponte 4: Chamas Perdidas | Acender 3 piras e dissipar 10 sombras | Zona segura temporária após acender | Ambas as metas cumpridas |
| Ponte 5: Eclipse | Dissipar o Guardião do Eclipse | Chefe com mais HP e ataques à distância | Chefe derrotado |

Depois da quinta fase, ciclos adicionais repetem esses cinco objetivos com inimigos mais fortes e aparecimento mais frequente; chefes a cada quinta fase.

## Controles e combate

- WASD/setas movem no plano da ponte; Shift corre; Espaço lança um projétil de luz no inimigo próximo; E emite uma onda circular de luz.
- Piras: aproximar-se e pressionar F (ou tocar no botão) para acender. A zona iluminada reduz a pressão inimiga e restaura um pouco de vida uma vez por ativação.
- Sombras rápidas perseguem; tanques suportam mais golpes; atiradoras disparam projéteis; chefes combinam resistência e disparos.
- Feedback: patas e cauda articuladas, aura ao conjurar, clarão no dano, partículas de dissolução ao derrotar, luz dinâmica das piras.

## Economia e recordes

- Pontuação: 100 pontos por sombra, bônus de combo, resposta rápida e fase sem dano. Combo zera ao sofrer dano ou ficar seis segundos sem dissipar.
- Fragmentos de Luz: ganhos por inimigos e vitória; gastos entre fases em velocidade, alcance do Poder, vida máxima ou redução de recarga. Custos sobem a cada nível.
- Recordes: maior pontuação e fase mais alta, em `localStorage`. O progresso da tentativa atual não é salvo ao fechar a aba.

## Interface e áudio

HUD sobreposta: barra de vida, progresso da fase, combo, fragmentos, recarga, score e objetivo. Menus de início, vitória/melhorias e derrota. Áudio sintetizado pelo navegador após interação do jogador, com botão para silenciar. O ritmo musical aumenta quando há ameaças próximas. Botões de toque complementam o teclado.

## Limites do primeiro protótipo

Os guardiões e criaturas são modelos procedurais estilizados de baixa complexidade. Animações articuladas e efeitos em WebGL substituem os sprites 2D; modelos 3D autorais com acabamento idêntico às cartas, narrativa interativa, servidor de ranking e partidas online são etapas futuras. A disponibilidade do Three.js por CDN e WebGL depende do navegador e da conexão do jogador.
