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
