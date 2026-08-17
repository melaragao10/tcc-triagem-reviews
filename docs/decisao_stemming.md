# Decisao: stemming (RSLP) como complemento a comparacao literal

## Problema identificado
No teste com a base v1.0, o review "O servidor cai e a protagonista
parece um homem" nao foi classificado como Misto porque o indicador
cadastrado era "servidor caiu" (passado), nao "servidor cai" (presente).
Documentado em docs/observacoes_teste_v1.md.

## Solucao adotada
Adicionada uma segunda etapa de comparacao no metodo find_indicators:
se a comparacao literal (exata) nao encontrar o indicador, o sistema
reduz tanto o texto quanto o indicador ao radical morfologico via
RSLP Stemmer (NLTK, Removedor de Sufixos da Lingua Portuguesa) e
tenta casar novamente.

## Por que isso preserva a natureza simbolica do sistema
Stemming e uma tecnica baseada em regras linguisticas explicitas de
sufixacao (nao envolve rede neural, embeddings ou aprendizado
estatistico). O resultado de cada radical e deterministico e pode
ser verificado manualmente, preservando o requisito de auditabilidade
(RNF3) e a fundamentacao teorica de IA simbolica do capitulo 1.6.

## Explicabilidade preservada
O campo "indicadores_tecnicos"/"indicadores_afetivos" do resultado
agora informa quando um indicador foi encontrado via radical (sufixo
" (via radical)"), distinguindo do casamento literal exato. Isso
mantem rastreavel qual metodo levou a cada classificacao.

## Limitacao ainda existente
Stemming resolve variacoes morfologicas da MESMA palavra (flexao
verbal, genero, numero), mas nao resolve sinonimos verdadeiros
(palavras diferentes com sentido equivalente, ex: "trava" vs "buga").
Para esses casos, ver docs/decisao_sinonimos.md.
