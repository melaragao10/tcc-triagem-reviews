<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-escuro.svg">
    <img src="assets/logo.svg" alt="Triagem de reviews com IA simbólica" width="360">
  </picture>
</p>

# Triagem de reviews de jogos digitais com IA simbólica

**TCC — Ciência da Computação — UDF — 2026/2**
Autora: Melissa Aragão Leite

Sistema especialista baseado em regras que classifica reviews de jogos digitais em
**Técnico**, **Afetivo-visual**, **Misto** ou **Indefinido**. O objetivo é separar a avaliação
dos aspectos do jogo como produto (desempenho, gráficos, história, jogabilidade) dos comentários
motivados pela aparência ou pela representação de personagens e pela crítica ideológica
(*review bombing*).

Toda classificação é rastreável: o sistema registra quais indicadores encontrou, os
escores de cada grupo, a regra aplicada e a confiança. Não há aprendizado de máquina
envolvido (justificativa em [docs/decisao_ia.md](docs/decisao_ia.md)).

**Sumário:** [Como funciona](#como-funciona) · [Executar](#como-executar) ·
[Validação](#fluxo-de-validação) · [Painel](#painel-de-resultados) ·
[Coletas](#coletas) · [Estrutura](#estrutura) ·
[Andamento](#andamento) · [Decisões](#decisões-técnicas)

---

## Como funciona

```
reviews (CSV) → preparação → base de conhecimento → escores → regras → relatórios + painel
```

1. **Entrada** — um ou vários CSVs com `id_review`, `jogo` e `texto_original` (mais
   `nota`, `recomendado`, `idioma` e metadados da Steam quando houver).
2. **Preparação** — remove duplicados e textos vazios e padroniza o texto (minúsculas,
   sem acentos, links e pontuação). O texto original nunca é alterado (RNF5).
3. **Base de conhecimento** — [config/base_conhecimento.json](config/base_conhecimento.json)
   (v2.3): indicadores técnicos e afetivo-visuais com peso de 1 a 3, em português e em inglês
   (a seção `"en"`, só casamento literal), mais:
   - **indicadores compostos** (`compostos_afetivo_visual`): dois grupos de palavras que precisam
     aparecer a poucas palavras de distância, registrados como `nome [A + B]`;
   - **neutralizadores**: negação e defesa perto de um termo afetivo (por exemplo "não é woke")
     anulam o indicador, e o log mostra `(ignorado: perto de 'X')`;
   - **exceções de texto**: expressões que não devem casar ("woke up").
   A versão fica no próprio JSON e é gravada em cada linha do resultado.
4. **Escores** — primeiro o casamento literal de todos os indicadores, depois o casamento
   pelo radical (stemmer RSLP do NLTK, só em português). Cada radical conta uma vez só, seja qual
   for a ordem da base.
5. **Regras** — a matriz abaixo define a categoria.
6. **Relatórios** — CSVs, gráfico e um painel HTML na pasta de saída.

### Definição das categorias (base v2.3)

- **Técnico**: avaliação de aspectos do jogo como produto: desempenho, gráficos, história,
  jogabilidade, som, mecânicas. É neutra quanto à polaridade: elogio ("bem otimizado", "história
  incrível") e crítica ("trava", "mal otimizado") contam igual.
- **Afetivo-visual**: aparência e representação de personagens, e crítica ideológica. Defesa,
  negação e simples menção não contam.
- **Misto**: indicadores dos dois grupos no mesmo review.
- **Indefinido**: nenhum indicador da base.

As decisões e o raciocínio estão em [docs/decisao_base_v2.md](docs/decisao_base_v2.md).
A definição ainda será confirmada com a orientadora.

### Matriz de classificação

|                  | Afetivo = 0       | Afetivo > 0             |
|------------------|-------------------|-------------------------|
| **Técnico = 0**  | R4 — Indefinido   | R2 — Afetivo-visual     |
| **Técnico > 0**  | R1 — Técnico      | R3 — Misto              |

### Confiança

```
confiança = max(T, A) / (T + A)
```

Vale 1,00 quando só um grupo pontua e cai para 0,50 quando os dois empatam. Sem nenhum
indicador, a confiança é 0.

---

## Como executar

Tudo roda em Docker, sem instalar Python no host. Para rodar direto no Python, use os
mesmos comandos sem o prefixo `docker compose run --rm classificador`.

```bash
docker compose build
```

A imagem copia o código na hora do build: depois de mudar `src/`, `tests/` ou `config/`, rode
`docker compose build` de novo antes de testar.

```bash
docker compose run --rm classificador python main.py
```

Sem argumentos, `main.py` classifica `data/reviews_entrada.csv` (7 reviews de exemplo)
e grava em `reports/`. Para outros arquivos, passe sempre `--entrada`:

```bash
docker compose run --rm classificador python main.py --entrada data/steam_*.csv --saida reports/steam
```

### Testes

```bash
docker compose run --rm classificador python -m unittest discover -s tests
```

Os testes ficam em `tests/`: classificador (inclui indicadores compostos, bilíngue e
neutralizadores), coleta, validação, painel e servidor.

### Saídas

| Arquivo | Conteúdo |
|---|---|
| `reviews_classificados.csv` | Cada review com escores, indicadores, categoria, regra, confiança e versão da base |
| `reviews_tecnicos.csv` | Só os reviews Técnico e Misto |
| `resumo_categorias.csv` | Quantidade e percentual por categoria |
| `distribuicao_categorias.png` | Gráfico da distribuição |
| `painel.html` | Painel interativo, offline, para a banca |

---

## Fluxo de validação

Reviews reais → gabarito manual → métricas. As regras de rotulagem e de cegamento
estão em [docs/protocolo_rotulagem.md](docs/protocolo_rotulagem.md). Pelo Docker,
prefixe cada comando com `docker compose run --rm classificador`.

**1. Coletar** reviews (não precisa de chave de API). Português é o padrão; `--idioma english`
coleta em inglês; `--tipo negativas` coleta só as negativas, em arquivos `steam_<appid>_negativas.csv`
na mesma pasta:

```bash
python -m src.coleta_steam --lote config/jogos.json --filtro helpful --max 3000 --saida data
python -m src.coleta_steam --lote config/jogos.json --filtro helpful --max 3000 --tipo negativas --saida data
```

Ou um jogo só (o `appid` é o número na URL da loja), opcionalmente num período:

```bash
python -m src.coleta_steam --appid <id> --jogo "<nome>" --max 500 --periodo 2025-01-30 2025-02-28
```

`--filtro helpful` pega as mais úteis de todo o histórico. Por padrão, as reviews que a
Steam marca como "fora do assunto" (o jeito dela de tratar review bombing) entram na
coleta. Erros temporários da Steam (500, 502, 503, 504) são repetidos automaticamente. O steamid
do autor não é gravado.

**2. Classificar** (aceita vários CSVs, que são juntados; reviews repetidas pelo `id_review` entram uma vez):

```bash
python main.py --entrada data/steam_*.csv --saida reports/steam
```

**3. Sortear a amostra cega** para rotulagem manual (estratificada pela categoria
automática, com semente fixa):

```bash
python -m src.amostragem --tamanho 200
```

**4. Rotular:** preencher `categoria_manual` e salvar como `data/gabarito_rotulado.csv`.

**5. Avaliar:** matriz de confusão, precisão, revocação e F1 (e kappa, com `--segundo`):

```bash
python -m src.avaliacao --gabarito data/gabarito_rotulado.csv
```

Para evitar ajuste da base aos mesmos dados em que ela é medida, os termos são descobertos só nos
jogos de desenvolvimento; os jogos de teste (Spider-Man 2, Horizon Forbidden West e Mass Effect:
Andromeda) ficam de fora dessa etapa.

---

## Painel de resultados

Cada classificação gera um `painel.html` na pasta de relatórios (por exemplo
`reports/steam/painel.html`). É um arquivo só, que abre offline em qualquer navegador.
Ele mostra a divisão por categoria e por jogo, os indicadores mais acionados, a matriz de
confusão (depois da avaliação) e cada review com os indicadores marcados no próprio
texto, para auditar a classificação a olho. No fim de cada cartão fica a conta: cada indicador com o
seu peso na base (`trava +2`, `bug +1`), a soma de cada grupo, a barra técnico × afetivo-visual (a
confiança) e o veredito com a regra aplicada. Passar o mouse num indicador acende o trecho dele no texto.

- **Idioma**: quando o CSV tem mais de um idioma (coluna `idioma`), o cabeçalho mostra o seletor
  *Idioma* (Todos / Português / Inglês). Um painel só, e o filtro recorta todos os números e a lista.
  Na URL: `?idioma=english` ou `?idioma=brazilian`.
- **Modo apresentação** (tecla `P`, `Esc` sai): letra maior para projetor.
- **Tema**: do sistema, claro ou escuro.
- **Imprimir ou salvar em PDF**: no tema que estiver na tela (claro, escuro ou o do sistema), em A4 com
  tipografia compacta, com os filtros aplicados na tela e a lista de reviews inteira.
- **Link do recorte**: jogo, categoria, período, busca e ordenação ficam na URL.

Para gerar o painel de novo sem reclassificar:

```bash
python -m src.painel --pasta reports/completo_todos
```

### Abrir numa porta local

```bash
docker compose up -d painel
```

Abre em http://localhost:8090. Para parar, use `docker compose stop painel`. Sem Docker, o
equivalente é `python -m src.servidor`. A página inicial lista os painéis de `reports/`, e cada um
tem uma rota própria: `reports/<pasta>/painel.html` fica em `/<pasta>`. Para usar outra porta:
`PAINEL_PORTA=9000` no Docker ou `--porta 9000` no Python.

### Painel ao vivo (desenvolvimento)

`src/painel_vivo.py` serve a pasta `reports/` e recarrega a página sozinha quando um relatório
muda (consulta `/__versao` a cada 2 segundos; selo "● ao vivo"). Sobe com:

```bash
docker compose -f docker-compose.vivo.yml up -d
```

Abre em http://localhost:8091 (preso a 127.0.0.1). Não use `--remove-orphans` ao subir outros
serviços, senão o painel ao vivo é removido.

A porta fica presa a 127.0.0.1, então na VM os painéis não ficam expostos na internet. Para
vê-los do seu computador, abra um túnel SSH e deixe a janela aberta:

```bash
ssh -L 8091:localhost:8091 <usuario>@<ip-da-vm>
```

(para o painel da porta 8090, troque as duas portas por 8090). O painel unificado, com os dois
idiomas, fica em `/completo_todos/`.

---

## Coletas

Amostragem **intencional**: a coleta inclui, de propósito, jogos polêmicos e avaliações
negativas misturados no todo (não numa parte separada), para haver reviews afetivo-visuais
suficientes para avaliar o sistema. Detalhes em [docs/coleta_dirigida.md](docs/coleta_dirigida.md).

- A distribuição entre as categorias **não representa** a população de reviews da Steam. As
  conclusões do TCC vêm de precisão e revocação medidas no gabarito, separadas por `recomendado`.
- Jogos em [config/jogos.json](config/jogos.json) (17, entre os originais e jogos polêmicos como
  Stellar Blade, Assassin's Creed Shadows, Marvel's Avengers, Forspoken, Hogwarts Legacy, Starfield
  e Saints Row); reserva em [config/jogos_reserva.json](config/jogos_reserva.json).
- Resultados por pasta: `reports/completo` (português), `reports/completo_en` (inglês) e
  `reports/completo_todos` (os dois juntos, com o filtro de idioma).

**Achados até agora (base v2.3):**
- Mesmo com amostragem dirigida, Afetivo-visual e Misto somados ficam em poucos por cento; o
  Indefinido continua grande. O vocabulário afetivo ideológico ("woke", "lacração") aparece, mas
  poucos reviews o usam sozinho.
- Reviews que misturam crítica ideológica com história ou gráficos caem em Misto.
- Os erros que sobram de precisão dependem de sentido (defesa, citação, ironia), o que está além de
  uma abordagem simbólica baseada em palavras. É um limite a discutir no TCC.

A primeira coleta (11/11/2026, 100 reviews pt-BR mais recentes por jogo, base v1.1) mostrou 87,7%
de Indefinido e só 1 review Afetivo-visual. Ela motivou a base v2 e a coleta dirigida.

---

## Estrutura

```
tcc-triagem-reviews/
├── config/
│   ├── base_conhecimento.json   # indicadores, compostos e neutralizadores (v2.3)
│   ├── jogos.json               # jogos da coleta
│   └── jogos_reserva.json       # jogos de reserva
├── data/                        # exemplo e CSVs coletados (fora do Git); data/en/ em inglês
├── docs/                        # decisões técnicas, protocolo, coleta dirigida
├── reports/                     # relatórios; completo, completo_en, completo_todos
├── src/
│   ├── classificador.py         # normalização, escores, regras e confiança
│   ├── coleta_steam.py          # coleta pela Web API GetAppReviews
│   ├── amostragem.py            # amostra cega para o gabarito
│   ├── avaliacao.py             # matriz de confusão, F1, kappa
│   ├── painel.py                # painel HTML (com filtro de idioma)
│   ├── servidor.py              # servidor local do painel
│   └── painel_vivo.py           # servidor com recarga automática (desenvolvimento)
├── tests/                       # testes automatizados
├── main.py                      # ponto de entrada
├── Dockerfile
├── docker-compose.yml
└── docker-compose.vivo.yml
```

## Ambiente

- VM Oracle Cloud (Ampere A1, ARM aarch64), 2 vCPUs, 11 GB de RAM
- Docker para reproduzir o ambiente completo (RNF6), com versões fixadas em `requirements.txt`
- Python 3.11, pandas, matplotlib e NLTK (RSLP)

---

## Decisões técnicas

- **IA simbólica em vez de ML/DL** — transparência, auditabilidade e execução sem GPU.
  [docs/decisao_ia.md](docs/decisao_ia.md)
- **Docker em vez de venv** — reproduz o ambiente inteiro, não só as bibliotecas.
- **Stemming RSLP como complemento** — cobre flexões regulares ("fechou sozinho" casa com
  "fecha sozinho"). Ele não une formas curtas como "cai" e "caiu", por isso "servidor cai"
  e "trava" foram cadastrados na base. Radicais de uma palavra só com menos de 3
  letras não casam sozinhos, porque o RSLP reduz "trava" e "trem" a "tr".
  [docs/decisao_stemming.md](docs/decisao_stemming.md)
- **Dupla contagem** — indicadores com o mesmo radical somam uma vez só, seja
  qual for a ordem da base. [docs/observacoes_teste_v1.md](docs/observacoes_teste_v1.md)
- **Base v2.x** — bilíngue, indicadores compostos por proximidade, neutralizadores de negação e
  defesa, e definição de Técnico neutra quanto à polaridade (elogio e crítica contam igual).
  [docs/decisao_base_v2.md](docs/decisao_base_v2.md)
- **Amostragem intencional** — jogos polêmicos e reviews negativas de propósito, sem tratar a
  distribuição como prevalência. Não usamos tweets: a API é paga, os termos de uso restringem e há
  questões éticas e de escopo.
- **Coleta pela Web API GetAppReviews** — o endpoint antigo da loja foi desligado em
  outubro de 2026. O coletor pede `filter_offtopic_activity=false` para incluir as reviews
  que a Steam esconde como fora do assunto.
- **Privacidade** — o identificador do autor não é gravado, só o texto e metadados
  agregados (data, votos, horas jogadas).
- **Gabarito cego** — a planilha de rotulagem não mostra a resposta do sistema.
- Critérios para incluir indicadores na base:
  [docs/criterios_base_conhecimento.md](docs/criterios_base_conhecimento.md)

### Limitações conhecidas

- Negação e defesa são tratadas só perto de termos afetivos, numa janela de palavras
  ("não é woke" é ignorado). Ironia, citação e defesa mais distantes ainda geram erros.
- Termos curtos podem casar pelo radical ("lag" com "lagado") em português; em inglês o casamento
  é só literal.
- O inglês não passa por stemming.

## Como regerar os dados

Os CSVs coletados (`data/steam_*.csv`, `data/en/`) e os relatórios de `reports/completo*` não ficam no Git (mais de 100 MB). Para regenerar:

    docker compose run --rm classificador python -m src.coleta_steam --lote config/jogos.json --filtro helpful --max 3000 --saida data
    docker compose run --rm classificador python -m src.coleta_steam --lote config/jogos.json --filtro helpful --max 3000 --tipo negativas --saida data
    docker compose run --rm classificador python -m src.coleta_steam --lote config/jogos.json --idioma english --filtro helpful --max 3000 --saida data/en
    docker compose run --rm classificador python -m src.coleta_steam --lote config/jogos.json --idioma english --filtro helpful --max 3000 --tipo negativas --saida data/en
    docker compose run --rm classificador python main.py --entrada data/steam_*.csv --saida reports/completo
    docker compose run --rm classificador python main.py --entrada data/en/steam_*.csv --saida reports/completo_en
    docker compose run --rm classificador python main.py --entrada data/steam_*.csv data/en/steam_*.csv --saida reports/completo_todos

A coleta inclui jogos polêmicos e reviews negativas de propósito (amostragem intencional, ver `docs/coleta_dirigida.md`); a distribuição entre categorias não representa a população de reviews da Steam.
