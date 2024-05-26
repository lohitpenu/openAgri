from rest_framework import serializers
from .models import WeatherStation

class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = [
            'id', 
            'geo_location_lat', 
            'geo_location_long', 
            'wind_direction', 
            'wind_speed', 
            'rainfall', 
            'sunshine', 
            'temperature', 
            'humidity', 
            'recording_time', 
            'device'
        ]
