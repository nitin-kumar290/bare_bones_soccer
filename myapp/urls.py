from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('get-events/', views.get_events, name='get_events'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path("api/get_presigned_url/", views.get_presigned_url, name="get_presigned_url"),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('datadeletion/', views.datadeletion, name='datadeletion'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
