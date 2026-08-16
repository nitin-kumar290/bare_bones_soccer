from django.contrib import admin
from django import forms
from .models import Pickup, Event, EventImage, LeagueTeam, LeagueTeamPlayer

import boto3
import uuid

AWS_REGION = "us-east-2"
TABLE_NAME = "ContactFormSubmissions"

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


# Create a Custom Form for Admin
class ContactFormAdminForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def save(self):
        data = self.cleaned_data
        if not data["id"]:  # Create new entry if ID is missing
            data["id"] = str(uuid.uuid4())

        table.put_item(Item=data)


# Custom Django Admin View
class ContactFormAdmin(admin.ModelAdmin):
    form = ContactFormAdminForm
    list_display = ("name", "email", "message")

    def get_queryset(self, request):
        response = table.scan()
        return response.get("Items", [])

    def save_model(self, request, obj, form, change):
        form.save()


# Register Admin View
#admin.site.register(ContactFormAdmin)  # No Django model required!
admin.site.register(Pickup)
# admin.site.register(Event)
# admin.site.register(EventImage)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event',)


class LeagueTeamPlayerInline(admin.TabularInline):
    model = LeagueTeamPlayer
    extra = 0
    fields = ('first_name', 'last_name', 'email', 'player', 'is_captain', 'status', 'claimed_at')
    readonly_fields = ('claimed_at',)


@admin.register(LeagueTeam)
class LeagueTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'league_name', 'captain', 'payment_mode', 'prepaid_status', 'invite_code', 'created_at')
    list_filter = ('league_name', 'payment_mode', 'prepaid_status')
    search_fields = ('team_name', 'captain__username', 'captain__email', 'invite_code')
    inlines = [LeagueTeamPlayerInline]


@admin.register(LeagueTeamPlayer)
class LeagueTeamPlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'team', 'player', 'is_captain', 'status', 'claimed_at')
    list_filter = ('team', 'status', 'is_captain')
    search_fields = ('first_name', 'last_name', 'email', 'player__username', 'player__email')
