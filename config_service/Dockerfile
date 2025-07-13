FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared ./shared

# Copy application code
COPY config_service/main.py .

# Expose port
EXPOSE 9999

# Run the application
CMD ["python", "main.py"] 