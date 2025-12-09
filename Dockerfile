# Dockerfile for SQL Tamper Framework

FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/noobforanonymous/sqlmap-tamper-collection"
LABEL org.opencontainers.image.description="SQL Tamper Framework with context-aware transformations"
LABEL org.opencontainers.image.licenses="GPL-2.0"

WORKDIR /app

# Copy framework
COPY tamper_framework/ /app/tamper_framework/
COPY tamper_scripts/ /app/tamper_scripts/
COPY tests/ /app/tests/
COPY setup.py /app/
COPY README.md /app/
COPY requirements.txt /app/

# Install framework
RUN pip install --no-cache-dir -e .

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python3", "-c", "from tamper_framework import __version__; print(f'SQL Tamper Framework v{__version__}')"]
