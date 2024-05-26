from rest_framework import serializers
from .models import QGIS

class QGISSerializer(serializers.ModelSerializer):
    class Meta:
        model = QGIS
        fields = [
            'id',
            'geo_location_lat',
            'geo_location_long',
            'ndvi',
            'gndvi',
            'lai',
            'msdvi',
            'recording_time',
            'device'
        ]
