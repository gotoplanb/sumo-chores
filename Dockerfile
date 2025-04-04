FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/gotoplanb/sumo-chores"
LABEL org.opencontainers.image.description="GitHub Action for Sumo Logic administration tasks"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set entrypoint to run the main script
ENTRYPOINT ["python", "-m", "src.main"] 