# from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser
from devices.serializers import DeviceSerializer

class UserSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(max_length=100, allow_blank=True, required=False)
    devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'contact', 'devices')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            contact=validated_data['contact']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
