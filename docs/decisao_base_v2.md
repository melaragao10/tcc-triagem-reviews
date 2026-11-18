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

## v2.4: ajuste a partir do primeiro gabarito (125 reviews pt-BR)

Origem: `reports/completo/avaliacao/divergencias.csv` (39 divergencias entre o gabarito manual e a v2.3). Os 3 jogos de teste (Spider-Man 2, Horizon Forbidden West, Mass Effect: Andromeda) NAO foram usados para escolher termos.

Mudancas, todas genericas (nenhuma depende de um review especifico):
- Aspas: trecho curto (ate 60 caracteres) entre aspas sai da busca do grupo afetivo ("Ain que jogo Woke", "criticas sobre 'woke'"). O grupo tecnico continua vendo o texto inteiro. Chave `aspas_neutralizam_afetivo`. Limite conhecido: quem escreve `jogo "woke"` para criticar tambem perde o termo.
- Neutralizadores novos (so afetivo): nao entendi, nao me importo, criticas, insignificante, pipipi, amo, adoro, besteira, vazias, ain, quem achou/acha/diz/disse/chama, frescura, fresco. "critica" no singular NAO entrou (e usada por quem critica de verdade).
- Termos tecnicos novos (peso 1, "nao vai rodar" peso 2): loading(s), tela de carregamento, grind, sidequest(s), side quest(s), missao, batalha(s), game play, repetitivo, colecionaveis, dialogos, nao vai rodar, coop/co op, cooperativo.
- Compostos novos: tecnico "jogo/mundo/mapa/visual + lindo/bonito/feio" (janela 2); afetivo "personagem/protagonista/mulher + bonita/gostosa/linda/sexy" (janela 3, peso 2), porque o gabarito trata aparencia (inclusive elogio) como afetivo.

Medicao (MESMOS 125 reviews dos quais saiu o ajuste, portanto OTIMISTA):
- Desenvolvimento (102): acuracia 0,65 -> 0,82; precisao Tecnico 0,93 -> 0,96; revocacao Tecnico 0,64 -> 0,82; precisao Indefinido 0,45 -> 0,65; precisao Misto 0,40 -> 0,67.
- Teste (23): inalterado (0,87), porque nenhuma mudanca tocou esses reviews. Nao prova generalizacao.
- A medicao valida da v2.4 e nas linhas ainda nao rotuladas da amostra e em gabarito novo.

Erros que sobram (21, 2 de jogos de teste), por tipo:
- Elogio generico rotulado como Tecnico no gabarito ("obra prima", "melhor game", "jogo perfeito"): o sistema esta coerente com o protocolo; o gabarito deve ser revisado para ser consistente.
- Defesa sem palavra-gatilho proxima ("de tao insignificante" longe do termo; "as criticas ... sao besteira" com varias palavras no meio): exige interpretacao semantica.
- "personagens nao parecem vivos" e "game play" separado: casos isolados.

Pendencias para o gabarito (decisao da autora): linha 116 (jogo perfeito, historia fantastica) esta como Indefinido mas, pela regra "historia e Tecnico", seria Tecnico; reviews de elogio generico sem aspecto devem ser Indefinido de forma consistente.

## R7 e R8 (Apendice E do TCC) implementadas como sinalizadores

As regras R7 (confianca menor que 0,6) e R8 (indicador de peso 1 isolado) constavam do Apendice E mas nao estavam no codigo. Agora cada review ganha a coluna `revisao_manual` ("R7", "R8", "R7;R8" ou vazio). Elas NAO mudam a categoria: so sinalizam para revisao. R7 so vale quando ha indicador; R8 vale quando o escore total e 1.
Medicao no gabarito (125 reviews, v2.4): 27 sinalizados (22%: 22 por R8, 5 por R7). Taxa de erro do sistema: 7% nos sinalizados contra 13% nos nao sinalizados. Ou seja, as duas regras NAO concentram os erros; os erros que sobram (defesa/ironia, elogio generico) nao tem confianca baixa. Resultado a relatar no TCC como achado negativo: sinalizar por confianca/peso nao e um bom detector de erro neste sistema.
