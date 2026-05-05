# Use official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency files first
COPY Pipfile Pipfile.lock ./

# Install pipenv
RUN pip install pipenv

# Install dependencies into system (not virtualenv)
RUN pipenv install --system --deploy

# Copy rest of the application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "-u", "run.py"]