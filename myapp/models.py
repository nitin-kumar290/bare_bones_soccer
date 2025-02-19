from django.db import models
from django.conf import settings
from .storage import EventMediaStorage, EventGalleryStorage
import boto3
import uuid


# # Initialize DynamoDB client
# dynamodb = boto3.resource(
#     'dynamodb',
#     region_name='us-east-2',  # Change to your AWS region
#     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
# )

# TABLE_NAME = 'ContactFormSubmissions'
# table = dynamodb.Table(TABLE_NAME)

# def save_contact_form(name, email, message):
#     """Save a contact form submission to DynamoDB."""
#     table.put_item(
#         Item={
#             'id': str(uuid.uuid4()),  # Generate a unique ID
#             'name': name,
#             'email': email,
#             'message': message,
#         }
#     )


# def get_contact_submissions():
#     """Retrieve all contact form submissions."""
#     response = table.scan()
#     return response.get('Items', [])

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.name} {self.email}"


class Pickup(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    #image = models.ImageField(upload_to='events/', blank=True, null=True)  # Main event image
    image = models.ImageField(
        storage=EventMediaStorage(),
        upload_to='',  # Empty since we defined location in storage class
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', args=[str(self.id)])

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')  # Links multiple images to an event
    #image = models.ImageField(upload_to='events/gallery/')  # Upload event gallery images to 'events/gallery/'
    image = models.ImageField(storage=EventGalleryStorage(),upload_to='')

    def __str__(self):
        return f"Image for {self.event.title}"