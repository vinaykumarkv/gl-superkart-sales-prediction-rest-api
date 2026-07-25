# Use a minimal Python 3.9 base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all files from backend_files directory
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the Flask port
EXPOSE 7860

# Run the Flask application
CMD ["python", "app.py"]
