# Dockerfile.app
# Use an official Python runtime as a parent image
FROM python:3.9.12-slim

# Set the working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run app.py when the container launches
CMD ["python", "app.py"]
