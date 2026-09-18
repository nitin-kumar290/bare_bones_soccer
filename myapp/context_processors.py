from django.conf import settings


def stripe_keys(request):
    return {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }


def stage_info(request):
    return {
        'STAGE': settings.STAGE,
        'IS_PROD': settings.IS_PROD,
    }


WALDY_LEAGUE_TEAM_CAP = 6
WALDY_LEAGUE_FREE_AGENTS_CLOSED = True


def league_status(request):
    from .models import LeagueTeam
    team_count = LeagueTeam.paid_count('Waldy Street League')
    return {
        'WALDY_LEAGUE_FULL': team_count >= WALDY_LEAGUE_TEAM_CAP,
        'WALDY_LEAGUE_FREE_AGENTS_CLOSED': WALDY_LEAGUE_FREE_AGENTS_CLOSED,
    }
