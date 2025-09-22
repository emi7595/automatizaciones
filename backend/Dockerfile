FROM python:3.12

# Evita .pyc y asegura logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY app ./app

# Render expone la variable PORT. Usa 8000 por defecto localmente.
ENV PORT=8000
EXPOSE 8000

# Ejecuta Uvicorn respetando $PORT de Render
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]