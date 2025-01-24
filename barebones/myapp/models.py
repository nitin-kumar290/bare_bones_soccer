from django.db import models

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
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)  # Main event image

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', args=[str(self.id)])

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')  # Links multiple images to an event
    image = models.ImageField(upload_to='events/gallery/')  # Upload event gallery images to 'events/gallery/'

    def __str__(self):
        return f"Image for {self.event.title}"