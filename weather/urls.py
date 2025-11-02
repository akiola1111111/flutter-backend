from django.urls import path
from . import views

urlpatterns = [
    path('countries/', views.get_african_countries, name='get-african-countries'),
    path('locations/', views.get_african_locations, name='get-african-locations'),
    path('save-location/', views.save_user_location, name='save-user-location'),
    path('user-location/', views.get_user_location, name='get-user-location'),
    path('current/', views.get_weather, name='get-weather'),
]