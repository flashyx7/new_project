FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared ./shared

# Copy application code
COPY registration_service/main.py .

# Expose port
EXPOSE 8888

# Run the application
CMD ["python", "main.py"] 