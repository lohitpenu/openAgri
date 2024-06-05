from django.contrib import admin
from .models import Device, Image, DeviceType

admin.site.register(Device)
admin.site.register(DeviceType)
admin.site.register(Image)
