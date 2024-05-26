from django.db import models
from devices.models import Device

class QGIS(models.Model):
    geo_location_lat = models.FloatField(null=True)
    geo_location_long = models.FloatField(null=True)
    ndvi = models.FloatField(null=True)
    gndvi = models.FloatField(null=True)
    lai = models.FloatField(null=True)
    msdvi = models.FloatField(null=True)
    recording_time = models.DateTimeField()
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name='qgis')

    def __str__(self):
        return f"QGIS {self.id}-Device {self.device.name}" if self.device else f"QGIS {self.id}"
