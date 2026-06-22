FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    openssh-client \
    iptables \
    bash \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY orchestrator.py .
COPY actions/ ./actions/
RUN chmod +x ./actions/*.sh
CMD ["python", "orchestrator.py"]
