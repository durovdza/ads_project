# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.8

# Setzen Sie das Arbeitsverzeichnis in den Container
WORKDIR /app

# Kopieren Sie die Dateien requirements.txt und Ihre Python-Anwendung in das Arbeitsverzeichnis des Containers
COPY DS_project\requirements\requirements_docker.txt .
COPY project_sophie.py .


# Befehl, um Ihre Anwendung auszuführen
CMD ["python", "DS_project\project_sophie.py"]
