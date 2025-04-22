# Use the official Python 3.8 slim image as the base to keep the image lightweight
FROM python:3.8-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies, including FFmpeg for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt to install Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Collect static files for Django (requires STATIC_ROOT to be set in settings.py)
RUN python manage.py collectstatic --noinput

# Expose port 8000 for the Gunicorn server
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=crm.settings

# Run migrations and start Gunicorn server
CMD ["sh", "-c", "python manage.py migrate && gunicorn crm.wsgi:application --bind 0.0.0.0:8000"]