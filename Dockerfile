# Use an official Python runtime as a parent image
FROM python:3.9-slim
# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .


# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=barebones.settings
ENV PYTHONUNBUFFERED=1

# Expose the port App Runner expects (default is 8080)
EXPOSE 8080

# Run the WSGI server
CMD ["gunicorn", "barebones.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3", "--timeout", "120"]
#["gunicorn", "--bind", "0.0.0.0:8080", "barebones.wsgi:application"]