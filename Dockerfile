# Use python:3.13-slim as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies    
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 6001 to the outside world
EXPOSE 6001

# Command to run the application with improved settings
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:6001", "--timeout=120", "--keep-alive=5", "--max-requests=1000", "--max-requests-jitter=50", "--access-logfile=-", "--error-logfile=-", "wsgi:app"]