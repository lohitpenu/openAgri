from rest_framework import serializers
from .models import Mobile, Crop

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
            'device',
            'pesticides_type',
            'pesticide_name',
            'pesticide_used',
            'crop'
        ]

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'