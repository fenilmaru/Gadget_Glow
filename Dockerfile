FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/logs /app/staticfiles /app/media

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

CMD gunicorn Gadget_Glow.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120 --access-logfile /app/logs/gunicorn.log --error-logfile /app/logs/gunicorn-error.log
