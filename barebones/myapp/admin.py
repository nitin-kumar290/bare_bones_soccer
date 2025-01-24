from django.contrib import admin
from .models import Pickup, Event, EventImage

@admin.register(Pickup)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event',)