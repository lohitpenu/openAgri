from django.contrib import admin
from .models import Device
from .models import DeviceType

admin.site.register(Device)
admin.site.register(DeviceType)
