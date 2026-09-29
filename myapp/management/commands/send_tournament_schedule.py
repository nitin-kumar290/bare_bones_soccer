from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.management.base import BaseCommand, CommandError
from django.db import connection as db_connection
from django.utils.html import escape

from myapp.models import EmailUnsubscribe, LeagueTeamPlayer
from myapp.views import TOURNAMENT_LEAGUE_NAME

SUBJECT = "Backyard 3v3 Tournament — Full Schedule & Rules (Friday, Oct 2)"
TEMPLATE_PATH = Path(settings.BASE_DIR) / 'email_templates' / 'tournament_schedule_rules_oct2.html'
MISTYPED_TLDS = ('.con', '.cmo', '.vom')


def _greeting_name(first_name):
    name = (first_name or '').strip()
    if name and (name.islower() or name.isupper()):
        name = name.title()
    return name or 'there'


class Command(BaseCommand):
    help = (
        "Tournament game-by-game schedule + rules email (Oct 2). Audience: every PAID "
        "player on any Backyard 3v3 Tournament team, whether or not they've confirmed a "
        "Bare Bones account yet. Sends to the email on the roster row. Nothing else — "
        "Street League and free agents are never included. Dry run by default; pass "
        "--live to send."
    )

    def add_arguments(self, parser):
        parser.add_argument('--live', action='store_true',
                            help="Actually send. Without this, only prints who WOULD receive it.")
        parser.add_argument('--preview-to', metavar='EMAIL',
                            help="With --live: send ONE copy to this address instead of the roster "
                                 "(subject tagged [PREVIEW]).")
        parser.add_argument('--only', nargs='+', metavar='EMAIL',
                            help="Limit the send to these roster emails (e.g. a late-added player).")

    def handle(self, *args, **options):
        live = options['live']

        if live and db_connection.vendor == 'sqlite':
            raise CommandError(
                "Refusing to send: this is pointed at the local sqlite test DB, not Neon. "
                "Run with LOCAL_SQLITE= (empty) so it reads the real tournament roster."
            )
        self.stdout.write(f"Database: {db_connection.vendor} ({db_connection.settings_dict.get('HOST') or 'local file'})")

        rows = (
            LeagueTeamPlayer.objects
            .filter(team__league_name=TOURNAMENT_LEAGUE_NAME, status='Paid')
            .select_related('team')
            .order_by('team_id', '-is_captain', 'id')
        )

        recipients, skipped = [], []
        seen_emails, seen_names = set(), set()
        for row in rows:
            email = (row.email or '').strip().lower()
            name_key = (row.team_id, row.first_name.strip().lower(), row.last_name.strip().lower())
            if not email:
                skipped.append((row, 'no email on file'))
            elif name_key in seen_names:
                skipped.append((row, 'same person listed twice on this team'))
            elif email.endswith(MISTYPED_TLDS):
                skipped.append((row, 'email looks mistyped'))
            elif email in seen_emails:
                skipped.append((row, 'email already covered by another row'))
            else:
                seen_names.add(name_key)
                seen_emails.add(email)
                recipients.append((row, email))

        if options['only']:
            wanted = {e.strip().lower() for e in options['only']}
            missing = wanted - {email for _, email in recipients}
            if missing:
                raise CommandError(f"Not in the tournament recipient list: {', '.join(sorted(missing))}")
            recipients = [(r, e) for r, e in recipients if e in wanted]

        self.stdout.write(f"\nAudience: {len(recipients)} tournament player(s).")
        for row, email in recipients:
            unsub = "  [on unsubscribe list]" if EmailUnsubscribe.objects.filter(email__iexact=email).exists() else ""
            self.stdout.write(f"  - {email}  (greeting: Hi {_greeting_name(row.first_name)}; {row.team.team_name}){unsub}")

        if skipped:
            self.stdout.write("\nSkipped:")
            for row, reason in skipped:
                self.stdout.write(f"  - {row.first_name} {row.last_name} <{row.email}> ({row.team.team_name}): {reason}")

        if not live:
            self.stdout.write(self.style.WARNING("\nDRY RUN — no emails sent. Re-run with --live to send."))
            return

        template = TEMPLATE_PATH.read_text()
        subject = SUBJECT
        if options['preview_to']:
            recipients = [(recipients[0][0], options['preview_to'].strip())]
            subject = f"[PREVIEW] {SUBJECT}"

        mail = get_connection()
        sent, failed = 0, []
        for row, email in recipients:
            name = 'there' if options['preview_to'] else _greeting_name(row.first_name)
            msg = EmailMessage(subject, template.replace('{first_name}', escape(name)),
                               settings.EMAIL_HOST_USER, [email], connection=mail)
            msg.content_subtype = 'html'
            try:
                msg.send()
                sent += 1
            except Exception as exc:
                failed.append((email, str(exc)))

        self.stdout.write(self.style.SUCCESS(f"\nSent {sent} email(s)."))
        for email, err in failed:
            self.stdout.write(self.style.ERROR(f"  FAILED {email}: {err}"))
