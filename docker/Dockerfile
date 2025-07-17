# Use uma imagem oficial do Python como imagem base. A versão 'slim' é mais leve.
FROM python:3.8-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala as dependências de sistema necessárias para as bibliotecas Python
# - 'iputils-ping' é necessário para o 'ping3' funcionar.
# - 'whois' é necessário para o 'python-whois' funcionar.
RUN apt-get update && apt-get install -y iputils-ping whois && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências para o diretório de trabalho
# Copiamos este arquivo primeiro para aproveitar o cache de camadas do Docker.
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Define o comando padrão para executar a aplicação quando o contêiner iniciar
CMD ["python", "main.py"]