# Use an AWS Lambda-compatible base image for Python
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container
WORKDIR /var/task

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Django app code into the container
COPY . .

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# Collect static files (uncomment this if running collectstatic inside the container)
# RUN python manage.py collectstatic --noinput

# Command to start the Django app with Lambda handler
CMD ["barebones.wsgi.application"]