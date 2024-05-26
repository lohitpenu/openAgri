from django.db import models
from devices.models import Device

class WeatherStation(models.Model):
    geo_location_lat = models.FloatField(null=True)
    geo_location_long = models.FloatField(null=True)
    wind_direction = models.CharField(max_length=128, null=True)
    wind_speed = models.CharField(max_length=128, null=True)
    rainfall = models.CharField(max_length=128, null=True)
    sunshine = models.CharField(max_length=128, null=True)
    temperature = models.CharField(max_length=128, null=True)
    humidity = models.CharField(max_length=128, null=True)
    recording_time = models.DateTimeField()
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name='weather_stations')

    def __str__(self):
        return f"WeatherStation {self.id}-Device {self.device.name}" if self.device else f"WeatherStation {self.id}"
