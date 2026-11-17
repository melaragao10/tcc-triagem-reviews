# Protocolo de rotulagem manual (gabarito)

Rascunho para revisao da autora: as definicoes abaixo seguem as quatro
categorias do sistema (Tabela 3 do TCC) e devem ser ajustadas ao texto
final do capitulo de metodologia antes da rotulagem comecar.

## Objetivo
Produzir um gabarito humano, independente do sistema, para medir
precisao, revocacao e F1 de cada categoria (secao 4.8 do TCC).

## Fluxo
1. Coletar reviews reais:
   `python -m src.coleta_steam --appid <id> --jogo "<nome>" --max 500`
2. Classificar automaticamente:
   `python main.py --entrada data/steam_<id>.csv`
3. Gerar a planilha cega:
   `python -m src.amostragem --tamanho 200`
   (cria `data/gabarito_para_rotular.csv`)
4. Rotular: preencher `categoria_manual` (e `observacao` quando houver
   duvida) e salvar como `data/gabarito_rotulado.csv`.
5. Avaliar:
   `python -m src.avaliacao --gabarito data/gabarito_rotulado.csv`

## Regras de cegamento
- A planilha mostra so o texto. Nao consultar `reports/` durante a
  rotulagem: ver a resposta do sistema enviesa o gabarito.
- Rotular na ordem da planilha (ja embaralhada).
- Nao alterar a base de conhecimento depois de ver o gabarito sem
  registrar a mudanca e reavaliar em uma amostra NOVA. Ajustar pesos
  olhando o mesmo gabarito usado para medir infla o resultado
  (sobreajuste). Sugestao: separar uma parte do gabarito para ajuste e
  outra, intocada, para a medicao final.

## Categorias
Valores aceitos em `categoria_manual`: `Tecnico`, `Afetivo-visual`,
`Misto`, `Indefinido` (acentos e maiusculas sao ignorados; aceita
tambem as iniciais T, A, M, I).

| Categoria | Quando usar | Exemplo |
|---|---|---|
| Tecnico | Critica a falhas de funcionamento: bugs, travamentos, desempenho, servidor, controles, salvamento. | "Fecha sozinho na segunda fase." |
| Afetivo-visual | Rejeicao a aparencia ou a representacao de personagens femininas. Subtipo **aparencia**: beleza, feminilidade, corpo, rosto, roupa. Subtipo **representacao**: critica ideologica dirigida a personagem feminina ou ao papel das mulheres no jogo ("woke", "lacracao", "forcada"). | Aparencia: "A protagonista parece um homem." Representacao: "Forcaram a barra com a protagonista, so lacracao." |
| Misto | Contem as duas criticas acima no mesmo review. | "O servidor cai e a personagem e feia." |
| Indefinido | Nenhuma das duas: elogios, historia, preco, jogabilidade sem falha tecnica, texto vazio ou sem sentido. | "Gostei da historia." |

## Subtipo do afetivo-visual
Todo review rotulado como Afetivo-visual ou Misto leva na coluna
`observacao` o subtipo: `subtipo:aparencia` ou `subtipo:representacao`
(ou os dois, separados por virgula). Isso nao muda as quatro categorias
nem as metricas principais; permite relatar separadamente os dois
fenomenos.

## Limite da critica ideologica
A categoria cobre a critica ideologica **dirigida a personagens femininas**
ou ao papel das mulheres no jogo. Critica ideologica geral, sem relacao
com personagem feminina, nao entra:
- "Jogo woke, nao compro." (sem personagem feminina): Indefinido,
  observacao `ideologico_geral`.
- "A protagonista e so lacracao." : Afetivo-visual, `subtipo:representacao`.
- Critica a personagens LGBT ou a etnia, sem foco em mulheres:
  Indefinido, observacao `ideologico_geral`.
Registrar a contagem de `ideologico_geral` para discutir no texto.

## Casos dificeis (decidir e registrar em `observacao`)
- **Negacao:** "nao tem bug nenhum" e Indefinido (o sistema hoje erra
  esse caso; e uma limitacao conhecida).
- **Ironia/sarcasmo:** rotular pelo sentido pretendido, nao pelas
  palavras. Marcar `ironia` na observacao.
- **Critica de arte geral** (graficos, texturas, cenarios) sem foco em
  personagem feminina: e Tecnico se for falha (textura quebrada), e
  Indefinido se for gosto estetico geral.
- **Idioma misturado ou outro idioma:** rotular se compreensivel; senao
  Indefinido com observacao `idioma`.

## Concordancia entre anotadores
Se possivel, uma segunda pessoa rotula de forma independente a mesma
planilha (ou pelo menos 50 reviews dela). O kappa de Cohen sai com:

    python -m src.avaliacao --gabarito data/gabarito_a.csv --segundo data/gabarito_b.csv

Referencia usual (Landis e Koch, 1977): kappa acima de 0,61 e
concordancia substancial; acima de 0,81, quase perfeita. Kappa baixo
indica que as definicoes acima precisam ficar mais claras antes de
medir o sistema.
