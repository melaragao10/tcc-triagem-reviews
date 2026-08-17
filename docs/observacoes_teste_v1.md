# Observacoes do primeiro teste (base de conhecimento v1.0)

## Resultado do teste com 7 reviews de exemplo
- Tecnico: 2
- Afetivo-visual: 3
- Indefinido: 2
- Misto: 0

## Limitacao identificada
Review 3 ("O servidor cai e a protagonista parece um homem.") deveria
ser classificado como "Misto" (contem critica tecnica e afetivo-visual),
mas foi classificado como "Afetivo-visual" (escore_tecnico=0).

Causa raiz: a base de conhecimento possui os indicadores "erro no
servidor" e "servidor caiu", mas nao "servidor cai" (variacao verbal
no presente do indicativo). O comparador de indicadores e literal
(secao 2.5 do TCC), entao variacoes morfologicas nao cadastradas nao
sao reconhecidas.

## Acao futura
Documentado como exemplo real de limitacao do sistema (capitulo 6.3
do TCC). Sera avaliado se a base de conhecimento devera incluir mais
variacoes verbais/morfologicas dos indicadores tecnicos, ou se este
tipo de caso sera tratado apenas na revisao manual (Requisito RF5).
