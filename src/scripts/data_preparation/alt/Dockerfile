# Verwende ein Basis-Image mit Python
FROM python:3.9

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anforderungen der Anwendung in das Arbeitsverzeichnis
COPY requirements_docker.txt requirements_docker.txt

# Installiere die Anforderungen
RUN pip install -r requirements_docker.txt

# Kopiere den Rest des Anwendungscodes
COPY . .

# Setze den Standardbefehl
CMD ["python", "data_collection_web_scraping_docker.py"]
