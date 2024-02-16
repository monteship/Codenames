# Use official Python image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /backend

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client packages
RUN apt-get update && apt-get install -y postgresql-client

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5000 to the outside world
EXPOSE 5000

# Set up PostgreSQL environment variables
ENV POSTGRES_DB=codenames_db
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=secret_password
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

# Command to run the Flask application with Gunicorn
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
