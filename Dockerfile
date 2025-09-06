# Dockerfile
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports for FastAPI and Streamlink
EXPOSE 9000-9001:9000-9001

# Command to run the FastAPI application
CMD ["python", "main.py"]