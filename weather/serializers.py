from rest_framework import serializers
from .models import UserLocation, AfricanLocation

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ['city', 'country', 'language']

class AfricanLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AfricanLocation
        fields = ['name', 'country', 'region', 'latitude', 'longitude', 'local_name']

class WeatherRequestSerializer(serializers.Serializer):
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    language = serializers.CharField(required=False, default='en')