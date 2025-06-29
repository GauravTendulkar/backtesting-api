# Use official Python image as a base
FROM python:3.12.2

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code to the container
COPY . .

# Expose port (default FastAPI port is 8000)
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app","--reload", "--host", "0.0.0.0", "--port", "8000"]
