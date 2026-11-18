# Amostragem intencional: jogos polemicos e reviews negativas no conjunto principal

## Por que
Em amostra natural o Afetivo-visual e raro (~1% das reviews). Critica de aparencia e de representacao de personagens aparece quase so em review negativa de jogos com controversia publica. Para o sistema ter o que classificar (e para medir precisao e revocacao com casos suficientes), o conjunto principal passa a incluir de proposito:
- mais jogos polemicos (config/jogos.json agora tem 17);
- reviews negativas desses jogos, coletadas com `--tipo negativas`, gravadas como `steam_<appid>_negativas.csv` na MESMA pasta (data/ e data/en/). O `main.py` junta tudo e remove duplicadas pelo `id_review`.

## Jogos acrescentados (appids conferidos na URL da loja)
Stellar Blade (3489700), Wolfenstein: Youngblood (1056960), Assassin's Creed Shadows (3159330), Marvel's Avengers (997070), Forspoken (1680880), Hogwarts Legacy (990080), Starfield (1716740), Saints Row 2022 (742420). Concord fica na reserva (volume baixo; jogo retirado em 2024).

## Mudancas no coletor (src/coleta_steam.py)
- `--tipo todas|positivas|negativas` (padrao: todas). Negativas usam review_type=2 da API (conferir no primeiro uso: todas as linhas devem ter recomendado=nao).
- Tentativas automaticas com espera crescente (5 s, 10 s, 20 s...) em HTTP 500/502/503/504 e conexao caida, ate 6 tentativas por pagina. 429 continua parando a coleta.

## Limite metodologico (declarar no TCC)
O conjunto e uma AMOSTRA INTENCIONAL, nao representa a populacao de reviews. A proporcao entre Tecnico, Afetivo-visual, Misto e Indefinido nele NAO e a prevalencia real na Steam. Metodologia: descrever como amostragem por conveniencia dirigida; usar a coluna `recomendado` para separar, e relatar precisao/revocacao por categoria no gabarito (nao a distribuicao bruta). A divisao desenvolvimento/teste continua valendo: termos descobertos so em jogos de desenvolvimento; metricas finais so em jogos de teste.
