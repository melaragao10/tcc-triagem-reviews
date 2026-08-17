# Decisão: IA Simbólica (Sistema Especialista) vs. outras abordagens

## Contexto
Ambiente de execução: computador pessoal / VM sem GPU dedicada.
Requisito central do trabalho: explicabilidade e auditoria de cada
classificação (não apenas acurácia).

## Abordagens avaliadas
- Sistema especialista (regras + pesos) — ESCOLHIDA
- Naive Bayes / SVM (ML clássico)
- Random Forest / Gradient Boosting
- LSTM / RNN
- BERT / Transformers (fine-tuning local)
- LLM via API
- spaCy/NLTK + regras (híbrido)

## Justificativa da escolha
1. Restrição de hardware: sem GPU, sistema roda em CPU comum.
2. Explicabilidade nativa: cada decisão é rastreável a uma regra,
   indicador e peso específicos — essencial dado o tema sensível do
   trabalho (representação de personagens femininas, review bombing).
3. Não depende de grande volume de dados rotulados previamente.
4. Reprodutibilidade total e custo computacional zero.
5. Alinhamento com a tradição de IA simbólica (Russell e Norvig;
   Durkin, 1994), já referenciada na fundamentação teórica do TCC.

## Trade-off assumido
Regras não capturam ironia, negação ou variações linguísticas não
previstas. Mitigado por revisão manual, controle de versão da base de
conhecimento e ajuste progressivo de indicadores/pesos.
