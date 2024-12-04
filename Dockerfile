# Base image
FROM python:alpine

# Copy all files from the current directory to /app in the container
COPY . /app

# Change to the /app directory
WORKDIR /app

# Install gcc and other dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add a health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:80/health || exit 1

# Command to run the application
CMD ["python", "app.py"]
