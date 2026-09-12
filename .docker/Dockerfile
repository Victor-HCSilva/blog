# .docker/Dockerfile

# Imagem base oficial do Python (versão slim para ser leve)
FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc e força o log no terminal (sem buffer)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia primeiro o arquivo de requisitos para otimizar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da API (o contexto passado será a raiz do projeto)
COPY . .

# Expõe a porta que a API vai rodar
EXPOSE 8000

# Comando para iniciar o servidor Uvicorn escutando em todas as interfaces de rede do contêiner
CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]