# Use official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Add OpenSSL
RUN apt-get update && apt-get install -y \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install pipenv

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install dependencies into system (not virtualenv)
RUN pipenv install --system --deploy

# Copy rest of the application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "-u", "run.py"]