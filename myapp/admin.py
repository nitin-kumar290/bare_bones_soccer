from django.contrib import admin
from django import forms
from .models import Pickup, Event, EventImage, LeagueTeam, LeagueTeamPlayer, LeagueFreeAgent
from django.utils import timezone

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


@admin.register(LeagueFreeAgent)
class LeagueFreeAgentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'placed_team', 'placement_email_sent', 'signed_up_at')
    list_filter = ('league_name', 'status', 'placed_team')
    search_fields = ('first_name', 'last_name', 'email', 'player__username', 'player__email')
    readonly_fields = ('player', 'signed_up_at', 'placed_at', 'placement_email_sent')
    actions = ['place_on_team']

    @admin.action(description="Place selected free agents on their assigned team (requires 'Placed team' to be set; agent must already be Paid)")
    def place_on_team(self, request, queryset):
        from .views import send_free_agent_placement_email
        placed, skipped = 0, 0
        for agent in queryset:
            if not agent.placed_team or agent.status != 'Paid':
                skipped += 1
                continue
            LeagueTeamPlayer.objects.create(
                team=agent.placed_team,
                player=agent.player,
                first_name=agent.first_name,
                last_name=agent.last_name,
                email=agent.email,
                payment_id=agent.payment_id,
                amount=agent.amount,
                status='Paid',
            )
            agent.status = 'Placed'
            agent.placed_at = timezone.now()
            agent.placement_email_sent = True
            agent.save()
            send_free_agent_placement_email(request, agent)
            placed += 1
        if placed:
            self.message_user(request, f"Placed {placed} free agent(s) on their assigned team and notified them.")
        if skipped:
            self.message_user(request, f"Skipped {skipped} agent(s) — 'Placed team' must be set and status must be 'Paid' first.", level='warning')
