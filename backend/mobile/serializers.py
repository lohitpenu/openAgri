from rest_framework import serializers
from .models import Mobile, Image

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

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'mobile', 'image_file']