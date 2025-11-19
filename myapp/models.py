from django.contrib.auth.models import User
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
    

# class SportsStable(models.Model):
#     """Stores registration details for the Sport Stable Series."""
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     emergency_contact_name = models.CharField(max_length=100)
#     emergency_contact_phone = models.CharField(max_length=20)
#     dob = models.DateField(verbose_name="Date of Birth")
#     electronic_signature = models.CharField(max_length=100)
#     agree_to_waiver = models.BooleanField(default=False)
#     registered_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.full_name} - {self.email}"

from django.contrib.auth.models import User

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age_category = models.CharField(
        max_length=10,
        choices=[('adult', 'Adult (18+)'), ('minor', 'Minor (Under 18)')],
        default='adult'
    )
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    electronic_signature = models.CharField(max_length=100)
    agree_to_waiver = models.BooleanField(default=False)
    marketing_opt_in = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class AttendancePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_date = models.DateField()
    payment_id = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.game_date} | {self.status}"
    

class EmailUnsubscribe(models.Model):
    REASON_CHOICES = [
        ('too_many', 'I receive too many emails'),
        ('not_relevant', 'Content is not relevant to me'),
        ('never_signed_up', 'I never signed up for these emails'),
        ('other', 'Other reason')
    ]
    
    email = models.EmailField(unique=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, blank=True, null=True)
    other_reason = models.TextField(blank=True, null=True)  # For "Other" option
    date_unsubscribed = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class EventRSVP(models.Model):
    email = models.EmailField()
    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'event_name', 'event_date')

    def __str__(self):
        return f"{self.email} - {self.event_name} ({self.event_date})"
    

class OneOffEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    payment_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Paid')
    created_at = models.DateTimeField(auto_now_add=True)
