# Imagem base: Python 3.11 ja pronto, versao "slim" = enxuta, sem excessos
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
# (tudo que rodar depois disso acontece "dentro" dessa pasta)
WORKDIR /app

# Copia primeiro so o requirements.txt (nao o projeto todo ainda)
# Isso e uma otimizacao: o Docker guarda em cache essa camada,
# entao se voce so mudar o codigo depois, nao precisa reinstalar
# as bibliotecas de novo, so quando o requirements.txt mudar
COPY requirements.txt .

# Instala as bibliotecas Python listadas no requirements.txt
# --no-cache-dir evita guardar cache de instalacao, deixando a imagem menor
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do projeto para dentro do container
COPY . .

# Comando que roda quando o container e iniciado
CMD ["python", "main.py"]
