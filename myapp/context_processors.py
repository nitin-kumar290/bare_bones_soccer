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
