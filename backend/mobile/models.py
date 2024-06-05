from django.db import models
from devices.models import Device
    

class Mobile(models.Model):
    geo_location_lat = models.FloatField(null=True)
    geo_location_long = models.FloatField(null=True)
    # image_path=models.CharField(max_length=256)
    qr_code=models.TextField()
    recording_time=models.DateTimeField(null=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name='mobiles')

    def __str__(self):
        return f"Mobile {self.id}-Device {self.device.name}" if self.device else f"Mobile {self.id}"
    
