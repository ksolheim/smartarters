# Use python:3.13-slim as base image
FROM python:3.13-slim

# Install necessary dependencies for ODBC Driver
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository and install ODBC Driver
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

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
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:app"]