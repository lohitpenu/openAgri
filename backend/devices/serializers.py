from rest_framework import serializers
from .models import Device, Image, DeviceType

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'name', 'address', 'type')

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ('id', 'name')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'device', 'geo_location_lat', 'geo_location_long']