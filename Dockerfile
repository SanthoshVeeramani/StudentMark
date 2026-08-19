# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for pillow and weasyprint (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage docker cache
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"

# Entrypoint will run migrations, collectstatic and start gunicorn
COPY ./compose/web/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
