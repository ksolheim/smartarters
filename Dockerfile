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

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=6001"]