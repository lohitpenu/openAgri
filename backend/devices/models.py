from django.db import models
from users.models import CustomUser


class DeviceType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Device(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    macaddress = models.CharField(max_length=100)  # Assuming MAC address length is 17 characters
    type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True, related_name='devices')
    # type = models.IntegerField(null=True)

    # Many-to-Many relationship with User
    users = models.ManyToManyField(CustomUser, related_name='devices')

    def __str__(self):
        return self.name
    
class Image(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image {self.id} for Device {self.device.id}"