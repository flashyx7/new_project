FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared ./shared

# Copy application code
COPY edge_service/main.py .

# Copy static files and templates if they exist
COPY edge_service/static ./static
COPY edge_service/templates ./templates

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"] 