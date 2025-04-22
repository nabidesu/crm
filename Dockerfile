# Use Python 3.9 as the base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Create and set working directory
WORKDIR /app

# Install system dependencies including ffmpeg for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Expose the port the app runs on
EXPOSE 8000

# Create a non-root user to run the app
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]