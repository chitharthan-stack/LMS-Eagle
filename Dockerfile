# Use the bullseye slim variant
FROM python:3.11-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /app/requirements.txt

COPY . /app
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN useradd --create-home appuser || true
RUN chown -R appuser:appuser /app || true
USER appuser

EXPOSE 8080
CMD ["/app/entrypoint.sh"]
