# Decisao: o que conta como afetivo-visual

## Decisao (17/11/2026): opcao B
A categoria Afetivo-visual passa a incluir a **critica ideologica dirigida a
personagens femininas** (por exemplo "woke", "lacracao", "forcada"), alem da
rejeicao a aparencia (rosto, corpo, roupa, feminilidade, atratividade).

Motivo: a primeira coleta (899 reviews) mostrou que a critica a personagens
femininas em pt-BR aparece mais como critica de representacao do que de
aparencia (so cerca de 2 a 4 casos de aparencia em 899).

## Consequencias a tratar
1. **Titulo e objetivos do TCC.** O termo "afetivo-visual" passa a cobrir tambem
   a dimensao ideologica. Ajustar a definicao no texto (secoes 2.7 e 3.2) e,
   se a orientadora preferir, o titulo.
2. **Limite da categoria.** Para nao perder o foco em personagens femininas,
   critica ideologica geral (sem personagem feminina) nao entra: fica
   Indefinido, com registro `ideologico_geral`. Ver
   docs/protocolo_rotulagem.md.
3. **Subtipo.** Cada review afetivo-visual ou misto recebe o subtipo
   `aparencia` ou `representacao`. As quatro categorias e as metricas
   principais nao mudam, e os dois fenomenos podem ser relatados em separado.
4. **Base de conhecimento v2.0.** Termos como "woke" sozinhos nao dizem se a
   critica e sobre mulheres. O motor atual soma indicadores soltos, sem
   contexto. Plano: indicadores compostos (um termo de personagem feminina
   a ate N palavras de um termo ideologico), ainda 100% simbolicos e
   auditaveis. Os termos saem da exploracao da coleta completa, descobertos
   em uma parte dos jogos e medidos nos demais.
5. **Avaliar com cautela.** Rotular a amostra seguindo o protocolo atualizado,
   com segundo anotador para o kappa, porque a fronteira entre critica de
   representacao e critica ideologica geral e subjetiva.

## Pendente com a orientadora
Confirmar a opcao B e o limite descrito acima (critica dirigida a personagem
feminina). Opcoes consideradas: A (so aparencia), B (aparencia e ideologia),
C (as quatro categorias com subtipo). A decisao registrada e B, com o subtipo
da opcao C como recurso de analise.

## Dados que sustentam a decisao
- Primeira coleta: 100 reviews pt-BR mais recentes por jogo, 9 jogos, 899
  reviews: Tecnico 91 (10,1%), Afetivo-visual 1, Misto 1, Indefinido 806 (89,7%).
- Coleta completa em pt-BR: [ ] reviews, [ ] com critica de aparencia,
  [ ] com critica de representacao.
- Exemplos (trechos curtos): "os modelos dos personagens, alguns sao bem
  feios" (aparencia); "Taash, cuja construcao acaba sendo mais forcada"
  (representacao).
