# Decisao: base de conhecimento v2.0 (bilingue + indicadores compostos)

## O que mudou
- Termos em ingles na secao `en` da base. Os dois idiomas sao aplicados a todo review e os escores somam. Ingles casa so de forma literal (RSLP e stemmer do portugues).
- Indicadores compostos (`compostos_afetivo_visual`): termo do grupo A a ate N palavras de um termo do grupo B (ex.: "character" perto de "ugly"). Regra explicita, auditavel, registrada como `nome [termoA + termoB]`.
- Termos de representacao/ideologia (Opcao B): `woke`, `pandering`, `tokenism`, `forced diversity`, `agenda` perto de `woke/political/lgbt`... marcados como critica, nao como simples mencao a personagens LGBT ou diversidade.
- Termos tecnicos em ingles (crash, stutter, fps drops, black screen...).

## O que ficou de fora de proposito
- `forced` sozinho: quase sempre "forced to play as X" (jogabilidade/roteiro).
- `lgbt characters`, `diversity`, `trans` sozinhos: mencao ou elogio, nao critica.
- Taash (Veilguard): personagem nao-binaria, fora do escopo.

## Limitacoes conhecidas
- `woke` domina os acertos em ingles; inclui usos como "idiots complain about woke" (defesa do jogo). E ruido de precisao a medir na avaliacao.
- Indicador composto e termo simples equivalente (ex.: "personagem feia") podem pontuar os dois; so afeta a confianca de Misto.
- Fonte dos termos: amostra de candidatos de jogos de DESENVOLVIMENTO (Dragon Age: Veilguard, TLOU II, Star Wars Outlaws, Suicide Squad, Horizon). A medicao deve usar jogos de TESTE nao vistos.
- Contagem de categorias na amostra de candidatos NAO e avaliacao (amostra enviesada). Avaliacao = gabarito manual em jogos de teste.

## v2.1: neutralizadores e excecoes (ajuste apos conferencia manual)

Conferencia manual de 60 reviews pt-BR classificados como Afetivo-visual pela v2.0 (amostra aleatoria, rotulada a mao):
- 36 critica real (ideologica ou de aparencia), 1 duvida, 23 erros -> precisao 36/59 = 61%.
- Erros tipicos: defesa do jogo ("quem fala em woke e bobo"), negacao ("nao vi lacracao", "sem lacracao"), mencao ("reclamam que ela e feia"), "woke up" (verbo em ingles), "personagens horriveis" (roteiro/animacao, nao aparencia).

Mudancas (regras explicitas, registradas no relatorio como "(ignorado: perto de 'X')"):
- `neutralizadores`: negacao/defesa ate 6 palavras antes ou 3 depois do termo afetivo cancela o escore (ex.: "nao vi", "sem", "nem", "mimimi", "reclamam", "quem fala"). So no grupo afetivo_visual. "nao gostei" NAO neutraliza.
- `excecoes_texto`: "woke up" etc. saem do texto antes da busca.
- Composto de aparencia: removidos `ela`, `estranha(s)`, `horrivel/horriveis`, `desproporcional` (ambiguos); em ingles removido `terribly ugly` (falso positivo de desempenho grafico).
- Composto "agenda + woke" removido (dupla contagem com `woke`).

Resultado na MESMA amostra usada para descobrir os erros (desenvolvimento, otimista): precisao 61% -> 78%, os 36 criticos reais continuam detectados. Os 10 erros restantes sao defesa/mencao que exigem interpretacao semantica (limite da abordagem simbolica, a discutir no TCC).
A medicao final deve ser feita em jogos de TESTE com gabarito novo.

## v2.2: vocabulario tecnico (otimizacao e desempenho)

Motivo: entre os reviews Indefinidos pt-BR (amostra de 8.000), os pares mais frequentes incluem "mal otimizado" (152) e "bem otimizado" (98): desempenho aparece muito e a v2.1 nao reconhecia.
- Termos novos (pt e en): otimizado/otimizacao/optimized/optimization, desempenho, fps, framerate, travou, crashou, bugado, congelou, engasgando, gargalo, roda mal/bem, tela azul, nao carrega/roda, requisitos.
- DECISAO A CONFIRMAR COM A ORIENTADORA: termos de otimizacao e fps sao neutros quanto a polaridade ("bem otimizado" tambem conta como Tecnico). Se a categoria Tecnico for so reclamacao, remover os de peso 1 e manter os de problema.
- Fora do escopo por ora: elogio de graficos ("graficos lindos", "expressoes faciais") e trilha sonora; decidir se "visual geral" entra em Afetivo-visual (reduziria muito o Indefinido, mas amplia o escopo alem de personagem/representacao).
- Efeito esperado, ainda nao medido: Tecnico pt-BR de ~10% para ~13%.

## v2.3: aspectos do jogo (historia, graficos, jogabilidade) contam como Tecnico
Decisao da autora: elogio ou critica sobre historia e graficos e Tecnico; elogio de graficos NAO e Afetivo-visual.
- Tecnico passa a significar "avaliacao dos aspectos do jogo enquanto produto" (desempenho, graficos, historia, jogabilidade, som, mecanicas). Afetivo-visual fica restrito a aparencia/representacao de personagens e critica ideologica.
- Termos peso 1: historia, enredo, roteiro, narrativa, jogabilidade, gameplay, graficos, trilha sonora, dublagem, combate, mundo aberto, missoes, mecanicas, animacoes, cenarios (+ equivalentes em ingles).
- Efeito esperado e observado: Indefinido cai muito; Misto cresce (reviews ideologicos quase sempre falam de historia); Afetivo-visual puro encolhe.
- Atencao no TCC: o nome "Tecnico" fica mais amplo que a definicao original (falha tecnica). Justificar ou renomear (ex.: "Aspectos do jogo") e confirmar com a orientadora.
- Em 60 reviews pt-BR antes afetivos: 36 Afetivo -> 11 Afetivo + 35 Misto + 10 Tecnico + 4 Indefinido (so desenvolvimento).
