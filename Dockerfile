FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Systemabhängigkeiten (optional, aber sinnvoll)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App kopieren
COPY . .

# Flask auf Port 5001
EXPOSE 5001

# Flask starten
CMD ["python", "app.py"]