from django.db import models
from devices.models import Device
    
class Crop(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Mobile(models.Model):
    geo_location_lat = models.FloatField(null=True)
    geo_location_long = models.FloatField(null=True)
    # image_path=models.CharField(max_length=256)
    qr_code=models.TextField()
    recording_time=models.DateTimeField(null=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name='mobiles')
    pesticides_type=models.IntegerField(null=True)
    pesticide_name=models.CharField(max_length=256, null=True)
    pesticide_used=models.FloatField(null=True)
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, related_name='mobiles')

    def __str__(self):
        return f"Mobile {self.id}-Device {self.device.name}" if self.device else f"Mobile {self.id}"
    
