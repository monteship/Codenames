# Use official Node.js image as the base image
FROM node:latest as build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the Angular application for production
RUN ng build --configuration=production

# Expose port 4200 to the outside world
EXPOSE 4200

# Command to start the Angular development server
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
