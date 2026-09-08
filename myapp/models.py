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
    business = models.CharField(max_length=150, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} {self.email}"


class Partner(models.Model):
    CATEGORY_CHOICES = [
        ('venue', 'Venue'),
        ('community', 'Community'),
        ('brand', 'Brand'),
        ('legal', 'Legal & Professional'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.CharField(max_length=200, blank=True, null=True)
    featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Pickup(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True, help_text="Short eyebrow line above the title, e.g. '3v3 · One Day · October 2'")
    description = models.TextField(blank=True, null=True, help_text="Shown as the intro/concept paragraph on the event page")
    location_name = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    #image = models.ImageField(upload_to='events/', blank=True, null=True)  # Main event image
    image = models.ImageField(
        storage=EventMediaStorage(),
        upload_to='',  # Empty since we defined location in storage class
        blank=True,
        null=True
    )
    rules_text = models.TextField(blank=True, null=True, help_text="One rule per line — shown as a bulleted list")
    registration_url = models.CharField(max_length=500, blank=True, null=True, help_text="Leave blank to show a 'Registration Opens Soon' placeholder instead of a button")
    registration_note = models.CharField(max_length=300, blank=True, null=True, help_text="Short line shown under the registration button/placeholder")
    schedule_note = models.CharField(max_length=300, blank=True, null=True, help_text="One-line summary above the schedule rows, e.g. '22 games · 5-min games, 2-min breaks · Kickoff 6:30 PM'")
    hero_video_url = models.URLField(max_length=500, blank=True, null=True, help_text="Autoplaying muted background video for the hero — takes priority over the image if both are set")
    registration_deadline_note = models.CharField(max_length=100, blank=True, null=True, help_text="Short urgency line shown above the hero CTA button, e.g. 'Registration closes 9/30'")
    team_structure_note = models.CharField(max_length=150, blank=True, null=True, help_text="Bold highlighted callout shown above the pricing cards, e.g. 'Team Registration Only — No Free Agents'")
    team_structure_subnote = models.CharField(max_length=200, blank=True, null=True, help_text="Small italic asterisk note shown under the team_structure_note callout")

    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')  # Links multiple images to an event
    #image = models.ImageField(upload_to='events/gallery/')  # Upload event gallery images to 'events/gallery/'
    image = models.ImageField(storage=EventGalleryStorage(),upload_to='')

    def __str__(self):
        return f"Image for {self.event.title}"


class EventSpec(models.Model):
    """One card in the format-spec grid on the event detail page, e.g. '3v3' / 'On the field'."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='specs')
    value = models.CharField(max_length=50, help_text="The big number/word, e.g. '3v3' or '18+'")
    label = models.CharField(max_length=100, help_text="The small caption under it, e.g. 'On the field'")
    highlight = models.BooleanField(default=False, help_text="Renders with the accent gradient treatment (use for the standout fact, e.g. the date)")
    compact = models.BooleanField(default=False, help_text="Shrinks the label and keeps it on one line — use for a longer value like a full location name")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.value} — {self.label}"


class EventPricingOption(models.Model):
    """One card in the pricing/registration-options grid, e.g. 'Pay Your Own Way' / '$20' / 'per player'."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='pricing_options')
    label = models.CharField(max_length=100, help_text="e.g. 'Pay Your Own Way' or 'Prepay Your Team'")
    amount = models.CharField(max_length=20, help_text="e.g. '$20'")
    per_text = models.CharField(max_length=50, blank=True, help_text="e.g. 'per player' or 'per player — save $10/player'")
    description = models.CharField(max_length=300, help_text="Short explanation of how this path works")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.label} — {self.amount}"


class EventScheduleRow(models.Model):
    """One row in the tournament/season structure card, e.g. 'Round Robin' / '15 games — everyone plays once'."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedule_rows')
    label = models.CharField(max_length=100, help_text="e.g. 'Round Robin' or 'Championship'")
    description = models.CharField(max_length=300, help_text="e.g. '15 games — every team plays every other team once'")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label


class EventFAQ(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
    

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
    

class ReferralSource(models.Model):
    SOURCE_CHOICES = [
        ('friend', 'A friend told me'),
        ('instagram', 'Instagram'),
        ('google', 'Google search'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    other_detail = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_source_display()}"


class LeagueTeam(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('individual', 'Individual Pay-In — teammates join via invite link and pay their own $50'),
        ('team_prepay', 'Team Prepay — captain pays for the whole roster upfront, $40/player'),
    ]
    league_name = models.CharField(max_length=100, default='Waldy Street League')
    team_name = models.CharField(max_length=100)
    captain = models.ForeignKey(User, on_delete=models.CASCADE, related_name='captained_league_teams')
    invite_code = models.CharField(max_length=12, unique=True, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='individual')
    # Only used for the team_prepay path — captain declares roster upfront and pays for everyone at once.
    # Individual teammates are captured as LeagueTeamPlayer rows (see below), not free text.
    prepaid_roster_size = models.PositiveSmallIntegerField(blank=True, null=True)
    prepaid_payment_id = models.CharField(max_length=200, blank=True, null=True)
    prepaid_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    prepaid_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            import secrets
            self.invite_code = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team_name} ({self.league_name})"

    @classmethod
    def paid_count(cls, league_name):
        # A team row is saved on form submit, before Stripe checkout completes,
        # so an unfiltered count() includes abandoned/never-paid registrations.
        from django.db.models import Q
        return cls.objects.filter(league_name=league_name).filter(
            Q(payment_mode='individual', players__is_captain=True, players__status='Paid') |
            Q(payment_mode='team_prepay', prepaid_status='Paid')
        ).distinct().count()


class LeagueTeamPlayer(models.Model):
    team = models.ForeignKey(LeagueTeam, on_delete=models.CASCADE, related_name='players')
    # Null until the player has a confirmed Bare Bones account attached — every player on a game-day
    # roster must eventually have this set, whether they paid directly (individual path, set immediately)
    # or were named by the captain (team_prepay path, set once they claim their slot).
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    email = models.EmailField(blank=True)
    is_captain = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    # Only used for team_prepay slots waiting on the named player to log in / create an account.
    claim_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    claimed_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'player')

    def __str__(self):
        who = self.player.username if self.player else f"{self.first_name} {self.last_name} (unclaimed)"
        return f"{who} on {self.team.team_name}"


class LeagueFreeAgent(models.Model):
    """
    A player without a team. Pays the standard $50 individual rate upfront at
    signup, same commitment as everyone else — then waits to be manually placed
    by an admin onto a specific team's roster. Never self-service, never a
    visible/joinable team of its own.
    """
    league_name = models.CharField(max_length=100, default='Waldy Street League')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='free_agent_signups')
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField()
    notes = models.TextField(blank=True, help_text="Optional — availability, preferences, anything useful for placement.")
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending Payment'), ('Paid', 'Paid — Awaiting Placement'), ('Placed', 'Placed')], default='Pending')
    placed_team = models.ForeignKey(LeagueTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='free_agents_placed')
    placement_email_sent = models.BooleanField(default=False)
    signed_up_at = models.DateTimeField(auto_now_add=True)
    placed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"


class OneOffEvent(models.Model):
    TICKET_TYPE_CHOICES = [
        ('player', 'Player Ticket'),
        ('player_plus', 'Player + Brunch Ticket'),
        ('spectator', 'Spectator (Free)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='player')
    payment_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Paid')
    created_at = models.DateTimeField(auto_now_add=True)
