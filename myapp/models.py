from django.db import models
from django.conf import settings
from .storage import EventMediaStorage, EventGalleryStorage
import boto3
import uuid




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
    

class SportsStable(models.Model):
    """Stores registration details for the Sport Stable Series."""
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    dob = models.DateField(verbose_name="Date of Birth")
    electronic_signature = models.CharField(max_length=100)
    agree_to_waiver = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"