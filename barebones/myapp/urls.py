from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name = 'about'),
    path('contact/', views.contact, name = 'contact'),
    path('pickup/', views.pickup, name='pickup'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('pickup/', views.pickup, name='pickup'),
    path('get-events/', views.get_events, name='get_events'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'), 
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
