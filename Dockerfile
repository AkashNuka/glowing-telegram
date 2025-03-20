# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Change to the correct directory for running the application
WORKDIR /app/water_service

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT water_service.wsgi:application