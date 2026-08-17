cat > README.md << 'EOF'
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
- [x] Base de conhecimento inicial (v1.0)
- [x] Classificador implementado e testado (7 reviews de exemplo, via Docker/Portainer)
- [x] Classificador com stemming (RSLP) implementado e testado
- [ ] Dicionário de sinônimos curados (config/sinonimos.json)
- [ ] Coleta de reviews reais (API Steam)
- [ ] Classificação manual de amostra (gabarito)
- [ ] Comparação automático x manual / ajuste de pesos
- [ ] Relatórios finais gerados

## Log de decisões técnicas
- Escolhida abordagem de IA simbólica (sistema especialista) em vez de
  Machine Learning/Deep Learning: justificativa em docs/decisao_ia.md
  (transparência, auditabilidade, viabilidade em hardware sem GPU).
- Escolhido Docker em vez de venv: garante reprodutibilidade do ambiente
  completo, não só das bibliotecas Python.
- Adicionado stemming (RSLP/NLTK) como camada complementar à comparação
  literal, para tratar variações morfológicas não cadastradas na base
  de conhecimento: docs/decisao_stemming.md.
- Corrigida dupla contagem de indicadores que reduzem ao mesmo radical
  (bug identificado e corrigido na v1.2 do classificador):
  docs/observacoes_teste_v1.md.
EOF
