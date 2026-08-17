# Triagem de Reviews de Jogos Digitais com IA Simbólica

TCC — Ciência da Computação — UDF — Melissa Aragão Leite

## Objetivo
Sistema especialista baseado em regras para classificar reviews de jogos
digitais em quatro categorias: técnico, afetivo-visual, misto ou indefinido,
separando críticas de falhas técnicas de comentários motivados por rejeição
à representação de personagens femininas (review bombing).

## Ambiente de execução
- VM Oracle Cloud (Ampere A1 / ARM aarch64)
- 2 vCPUs, 11GB RAM, 195GB disco
- Docker instalado (v29.6.0) para garantir reprodutibilidade (RNF6 do TCC)
- Todo o código roda dentro de container — não depende de instalação
  local de Python/pip no host

## Estrutura do projeto
projeto_reviews/
├── data/       # CSVs de entrada e saída
├── config/     # base_conhecimento.json (indicadores e pesos)
├── reports/    # gráficos e relatórios gerados
├── src/        # código-fonte do sistema especialista
├── docs/       # documentação de decisões técnicas
└── main.py     # ponto de entrada

## Status atual
- [x] VM provisionada e configurada
- [x] Docker instalado e testado
- [x] Estrutura de pastas criada
- [x] Repositório Git inicializado
- [x] Dockerfile criado
- [ ] Base de conhecimento inicial (v1.0)
- [ ] Coleta de reviews implementada
- [ ] Classificador implementado
- [ ] Classificação manual de amostra (gabarito)
- [ ] Comparação automático x manual / ajuste de pesos
- [ ] Relatórios finais gerados

## Log de decisões técnicas
- Escolhida abordagem de IA simbólica (sistema especialista) em vez de
  Machine Learning/Deep Learning: justificativa em docs/decisao_ia.md
  (transparência, auditabilidade, viabilidade em hardware sem GPU).
- Escolhido Docker em vez de venv: garante reprodutibilidade do ambiente
  completo, não só das bibliotecas Python.
