from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

BASE_PATH = settings.FORCE_SCRIPT_NAME or ""

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name = 'about'),
    path('sponsors-partners/', views.sponsors_partners, name='sponsors_partners'),
    path('contact/', views.contact, name = 'contact'),
    path('pickup/', views.pickup, name='pickup'),
    path('pickup-temp/', views.pickup_temp, name='pickup-temp'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('pickup/', views.pickup, name='pickup'),
    path('series/', views.series, name='series'),
    path('get-events/', views.get_events, name='get_events'),
    path('events/', views.events, name='events'),
    path("api/get_presigned_url/", views.get_presigned_url, name="get_presigned_url"),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('datadeletion/', views.datadeletion, name='datadeletion'),
    path('schedule/', views.schedule, name='schedule'),
    path('leagues/', views.leagues_hub, name='leagues_hub'),
    path('leagues/waldy-street-league/week-1/', views.waldy_league_week1_schedule, name='waldy_league_week1_schedule'),
    path('leagues/waldy-street-league/matchday/<int:number>/', views.waldy_league_matchday_schedule, name='waldy_league_matchday_schedule'),
    path('leagues/waldy-street-league/rosters/', views.waldy_league_rosters, name='waldy_league_rosters'),
    path('leagues/waldy-street-league/standings/', views.waldy_league_standings, name='waldy_league_standings'),
    path('leagues/waldy-street-league/', views.waldy_street_league, name='waldy_street_league'),
    path('leagues/waldy-street-league/register/', views.waldy_league_register, name='waldy_league_register'),
    path('leagues/waldy-street-league/free-agent/', views.waldy_league_free_agent, name='waldy_league_free_agent'),
    path('leagues/waldy-street-league/free-agent/<int:agent_id>/success/', views.free_agent_checkout_success, name='free_agent_checkout_success'),
    path('leagues/waldy-street-league/checkout/<int:team_id>/success/', views.league_checkout_success, name='league_checkout_success'),
    path('leagues/waldy-street-league/join/<str:invite_code>/', views.waldy_league_join, name='waldy_league_join'),
    path('api/create-league-join-checkout-session/<str:invite_code>/', views.create_league_join_checkout_session, name='create_league_join_checkout_session'),
    path('leagues/waldy-street-league/join/<str:invite_code>/success/', views.league_join_success, name='league_join_success'),
    path('leagues/waldy-street-league/claim/<str:claim_code>/', views.waldy_league_claim, name='waldy_league_claim'),

    path('backyard-tournament/register/', views.backyard_tournament_register, name='backyard_tournament_register'),
    path('backyard-tournament/checkout/<int:team_id>/success/', views.tournament_checkout_success, name='tournament_checkout_success'),
    path('backyard-tournament/join/<str:invite_code>/', views.tournament_join, name='tournament_join'),
    path('api/create-tournament-join-checkout-session/<str:invite_code>/', views.create_tournament_join_checkout_session, name='create_tournament_join_checkout_session'),
    path('backyard-tournament/join/<str:invite_code>/success/', views.tournament_join_success, name='tournament_join_success'),
    path('backyard-tournament/claim/<str:claim_code>/', views.tournament_claim, name='tournament_claim'),
    #path('pay/<str:date_str>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('api/create-multi-checkout-session', views.create_multi_checkout_session, name='create_multi_checkout_session'),
    path('series_catalog/',views.series_catalog, name='series_catalog'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('welcome/', views.welcome_next_steps, name='welcome_next_steps'),
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
         template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
         template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
         template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
         template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
     path(
        'username-reset/',
        views.username_reset,
        name='username_reset'
    ),
    path(
        'username-reset/done/',
        views.username_reset_done,
        name='username_reset_done'
    ),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/success/', views.unsubscribe_success, name='unsubscribe_success'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation-sent/', views.activation_sent, name='activation_sent'),
    path('rsvp/', views.event_rsvp, name='event_rsvp'),
    path('rsvp/success/', views.rsvp_success, name='rsvp_success'),
    path('api/register-wcf-rsvp/', views.register_wcf_rsvp, name='register_wcf_rsvp'),
    path('promo-video/', views.promo_video, name='promo_video'),
    path('waldschanke/', views.waldschanke, name='waldschanke'),
    path('api/create-waldschanke-checkout-session', views.create_waldschanke_checkout_session),
     path('waldschanke-payment-success/', views.waldschanke_payment_success, name='waldschanke_payment_success'),
     path('api/register-free-spectator', views.register_free_spectator, name='register_free_spectator'),
     path('spectator-registration-success/', views.spectator_registration_success, name='spectator_registration_success'),
     path('brighton/', views.brighton, name='brighton'),
     path('api/create-brighton-checkout-session', views.create_brighton_checkout_session),
     path('brighton-payment-success/', views.brighton_payment_success, name='brighton_payment_success'),
     path('api/register-brighton-spectator', views.register_brighton_spectator, name='register_brighton_spectator'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
