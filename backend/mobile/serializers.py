from rest_framework import serializers
from .models import Mobile

class MobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = [
            'id', 
            'geo_location_lat', 
            'geo_location_long', 
            # 'image_path', 
            'qr_code', 
            'recording_time', 
            'device'
        ]
