# Generated by Django 5.0.6 on 2024-07-03 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_auto_20240626_0729'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='geo_location_lat',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='geo_location_long',
            field=models.FloatField(null=True),
        ),
    ]
