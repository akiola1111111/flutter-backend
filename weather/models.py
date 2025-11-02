from django.db import models
from django.conf import settings

class UserLocation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=10, default='en')  # Language preference
    
    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.country}"

class AfricanLocation(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    local_name = models.CharField(max_length=100, blank=True)  # Local language name
    
    def __str__(self):
        return f"{self.name}, {self.country}"