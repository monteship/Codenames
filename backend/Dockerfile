# Use official Python image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5000 to the outside world
EXPOSE 5000

# Command to run the Flask application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
