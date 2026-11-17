# Selecao dos jogos da amostra

Cumpre a secao 2.4 do TCC: a selecao deve ser documentada, com os criterios,
a origem dos dados, a forma de acesso e o motivo de cada jogo.

## Criterios (TCC, secao 2.4)
1. Protagonista feminina, ou personagem feminina em posicao de destaque.
2. Controversia publica documentada sobre aparencia, corpo, rosto, roupas,
   feminilidade ou atratividade da personagem.
3. Jogo vendido na Steam, com reviews em portugues (pt-BR) em volume suficiente.
4. Dados de acesso legitimo: Web API oficial da Steam (GetAppReviews), sem
   scraping de terceiros e sem gravar o steamid do autor (secao 2.14).

## Estrutura da amostra
- **Nucleo (7 jogos):** a controversia e sobre a aparencia de uma personagem feminina.
- **Controle (2 jogos):** reviews com muito ruido tecnico ou de outra natureza.
  Servem para testar se o classificador separa bem o grupo tecnico do afetivo-visual.
- **Reserva (3 jogos, config/jogos_reserva.json):** so entram se o volume do
  nucleo for insuficiente.

## Nucleo

| Jogo | appid | Personagem | Controversia documentada |
|---|---|---|---|
| Horizon Zero Dawn Complete Edition | 1151640 | Aloy | Aparencia de Aloy criticada por parte do publico; o debate se intensificou com a sequencia |
| Horizon Forbidden West Complete Edition | 2420110 | Aloy | "Peach fuzz" chamado de "barba" e Aloy considerada "masculinizada"; review bombing |
| The Last of Us Part II Remastered | 2531310 | Abby | Reacao ao corpo musculoso de Abby; estudo academico sobre a recepcao |
| Star Wars Outlaws | 2842040 | Kay Vess | Criticas de que a protagonista seria "feia" em comparacao com a atriz da captura facial |
| Marvel's Spider-Man 2 | 2651280 | Mary Jane Watson | Criticas ao rosto de Mary Jane apos o trailer de 2023 |
| Dragon Age: The Veilguard | 1845910 | Rook, Taash e companheiras | Personagens chamados de "feios", critica a proporcoes e a musculatura de Taash; review bombing no Metacritic |
| Mass Effect: Andromeda | 1238000 | Sara Ryder | Rosto e expressoes de Sara Ryder e de outras personagens ridicularizados no lancamento |

## Controle

| Jogo | appid | Motivo |
|---|---|---|
| The Last of Us Part I | 1888930 | Rosto de Ellie alterado no remake; port de PC com review bombing tecnico em 2023 |
| Suicide Squad: Kill the Justice League | 315210 | Criticas a aparencia de Harley Quinn e rotulo de "woke"; ~12 mil reviews |

## Reserva

| Jogo | appid | Motivo e ressalva |
|---|---|---|
| Concord | 2443720 | Personagens chamados de "os mais feios"; poucas reviews (jogo retirado em 2024) |
| Stellar Blade | 3489700 | Debate sobre o corpo de Eve, de polaridade oposta (sexualizacao); a base atual nao cobre esse vocabulario |
| Wolfenstein: Youngblood | 1056960 | Criticas as protagonistas gemeas; aparencia pouco documentada |

## Fontes das controversias
Conferir cada link e citar no padrao ABNT no texto do TCC.

- Horizon:
  - https://www.denofgeek.com/games/horizon-forbidden-west-controversies-sequel-review-bomb-user-scores/
  - https://gamerant.com/horizon-forbidden-west-review-bombing-weird-reasons-explained/
- The Last of Us Part II:
  - Capitulo "Hard Bodies in Virtual Worlds: Assessing the Reception of Abby's Spectacular Body in The Last of Us Part II" (Emerald, 2022): https://emerald.com/insight/content/doi/10.1108/978-1-80117-514-220221007
  - https://www.inverse.com/gaming/last-of-us-2-trans-controversy-explained-abby-tlou
- Star Wars Outlaws:
  - https://www.pcgamer.com/games/action/as-rage-factories-howl-about-kay-vess-looks-star-wars-outlaws-lead-says-theres-no-point-engaging-with-bad-faith-criticism-no-nuance-and-no-possibility-of-real-dialogue
  - https://opencritic.com/news/3461/star-wars-outlaws-lead-calls-out-bad-faith-people-over-kay-vess-looks
- Marvel's Spider-Man 2:
  - https://comicbook.com/gaming/news/marvels-spider-man-2-mary-jane-mj-face-change
  - https://www.pushsquare.com/news/2023/07/marvels-spider-man-2-will-feature-the-same-mary-jane-face-model-insomniac-insists
- Dragon Age: The Veilguard:
  - https://www.levelup.com/en/news/it-ruined-the-series-dragon-age-the-veilguard-debuted-successfully-but-is-facing-review-bombing-on-metacritic-users-are-calling-it-a-woke-game/
  - https://comicbook.com/gaming/news/asmongold-dragon-age-the-veilguard-characters
- Mass Effect: Andromeda:
  - https://www.pcgamer.com/the-internet-is-brutally-mocking-mass-effect-andromedas-animations
  - https://pcgamer.com/bioware-boss-says-ryder-is-awesome-promises-animations-will-be-improved
  - https://mein-mmo.de/en/mass-effect-andromeda-gesichteranimationen-vergleich,149504
- The Last of Us Part I:
  - https://www.ggrecon.com/articles/fans-slam-the-last-of-us-part-1-as-worst-pc-port-ever/
  - https://www.gameinformer.com/feature/2022/12/01/pretty-different
  - https://gamingbible.com/news/the-last-of-us-fans-fence-remake-graphics-20220610
- Suicide Squad: Kill the Justice League:
  - https://cms.ggrecon.com/articles/suicide-squad-kill-the-justice-league-branded-a-woke-disaster
  - https://mein-mmo.de/en/consulting-firm-under-fire-whats-behind-the-allegations-that-sweet-baby-inc-makes-woke-games,1099852
- Concord:
  - https://mein-mmo.de/en/the-new-shooter-concord-from-sony-flops-brutally-at-launch-on-steam,1167655
  - https://dexerto.com/gaming/concord-slammed-over-ugliest-character-designs-ever-2754244
- Stellar Blade:
  - https://inverse.com/gaming/stellar-blade-the-male-gaze-sweet-baby
  - https://tech4gamers.com/stellar-blade-receiving-negative-reviews/

## Ressalvas a registrar no texto
- As reviews da Steam sao da versao de PC, lancada depois do auge de cada
  polemica (a polemica de Abby e de 2020; a versao de PC e de 2025). Por isso
  a coleta deve ser por periodo, nas semanas de lancamento no PC.
- A controversia do "peach fuzz" e da aparencia "masculina" de Aloy esta ligada
  principalmente a Horizon Forbidden West; Horizon Zero Dawn entra como jogo
  de referencia da mesma personagem.
- Spider-Man 2 e Mass Effect: Andromeda: a controversia de Mary Jane e de
  Sara Ryder mistura aparencia e qualidade da animacao facial, que e um
  aspecto tecnico. Registrar essa ambiguidade na discussao dos resultados.
- Spider-Man 2 nao tem protagonista feminina: entra pelo criterio de
  personagem feminina em posicao de destaque (secao 2.4).
- Os jogos de controle (The Last of Us Part I e Suicide Squad) nao tem a
  aparencia de uma personagem como centro da polemica; entram para testar a
  separacao entre ruido tecnico e afetivo-visual.
- Conferir os appids de Star Wars Outlaws e Spider-Man 2 na URL da loja antes
  da coleta definitiva.

## Proximo passo
Checar o volume de reviews em pt-BR de cada jogo e definir o periodo de coleta
(campo "periodo" em config/jogos.json).
