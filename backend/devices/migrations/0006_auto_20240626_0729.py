# your_app_name/migrations/0002_auto_YYYYMMDD_HHMM.py
from django.db import migrations

def create_device_types(apps, schema_editor):
    DeviceType = apps.get_model('devices', 'DeviceType')
    DeviceType.objects.bulk_create([
        DeviceType(id=1, name='MOBILE'),
        DeviceType(id=2, name='QGIS'),
        DeviceType(id=3, name='WEATHER_STATION')
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_alter_device_address'),
    ]

    operations = [
        migrations.RunPython(create_device_types),
    ]
