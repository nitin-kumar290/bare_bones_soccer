from django.core.management.base import BaseCommand
from myapp.models import LeagueTeamPlayer
from myapp.views import send_league_week_reminder_email


class Command(BaseCommand):
    help = (
        "Sends the '1 week until kickoff' reminder email to every confirmed league "
        "player. Strict audience rule: LeagueTeamPlayer.status == 'Paid' AND "
        "LeagueTeamPlayer.player is not None (a real, claimed Bare Bones account). "
        "Anyone still Pending, or any unclaimed team_prepay slot (named by a captain "
        "but never confirmed by the actual player logging in), is excluded — no "
        "exceptions. Sends to the player's own account email, never the raw "
        "LeagueTeamPlayer.email field, since that can be stale/typed-in by someone else."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--live', action='store_true',
            help="Actually send the emails. Without this flag, only prints who WOULD receive it.",
        )

    def handle(self, *args, **options):
        qs = (
            LeagueTeamPlayer.objects
            .filter(status='Paid', player__isnull=False)
            .select_related('player', 'team')
            .order_by('player_id')
        )

        seen_player_ids = set()
        recipients = []
        for row in qs:
            if row.player_id in seen_player_ids:
                continue
            seen_player_ids.add(row.player_id)
            recipients.append(row)

        self.stdout.write(f"Audience: {len(recipients)} confirmed, paid, account-linked player(s).")
        for row in recipients:
            self.stdout.write(f"  - {row.player.email}  ({row.first_name} {row.last_name}, team: {row.team.team_name})")

        if not options['live']:
            self.stdout.write(self.style.WARNING(
                "\nDRY RUN — no emails sent. Re-run with --live to actually send."
            ))
            return

        sent = 0
        for row in recipients:
            send_league_week_reminder_email(row)
            sent += 1
        self.stdout.write(self.style.SUCCESS(f"\nSent {sent} reminder email(s)."))
