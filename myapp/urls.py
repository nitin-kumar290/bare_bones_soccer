from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

BASE_PATH = settings.FORCE_SCRIPT_NAME or ""

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name = 'about'),
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
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path("api/get_presigned_url/", views.get_presigned_url, name="get_presigned_url"),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('datadeletion/', views.datadeletion, name='datadeletion'),
    path('schedule/', views.schedule, name='schedule'),
    #path('pay/<str:date_str>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('api/create-multi-checkout-session', views.create_multi_checkout_session, name='create_multi_checkout_session'),
    path('series_catalog/',views.series_catalog, name='series_catalog'),
    path('registration-success/', views.registration_success, name='registration_success'),
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
    path('promo-video/', views.promo_video, name='promo_video'),
    path('waldschanke/', views.waldschanke, name='waldschanke'),
    path('api/create-waldschanke-checkout-session', views.create_waldschanke_checkout_session),
     path('waldschanke-payment-success/', views.waldschanke_payment_success),
     path('api/register-free-spectator', views.register_free_spectator, name='register_free_spectator'),
     path('spectator-registration-success/', views.spectator_registration_success, name='spectator_registration_success'),
     path('brighton/', views.brighton, name='brighton'),
     path('api/create-brighton-checkout-session', views.create_brighton_checkout_session),
     path('brighton-payment-success/', views.brighton_payment_success),
     path('api/register-brighton-spectator', views.register_brighton_spectator, name='register_brighton_spectator'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
