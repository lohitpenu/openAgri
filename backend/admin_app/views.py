from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from devices.models import Device
from users.models import CustomUser
from devices.serializers import DeviceSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
# Create your views here.

class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def map_to_device(self, request, pk=None):
        device_id = request.data.get('device_id')
        user_id = request.data.get('user_id')

        try:
            device = Device.objects.get(id=device_id)
            user = CustomUser.objects.get(id=user_id)
        except (Device.DoesNotExist, CustomUser.DoesNotExist):
            return Response({'error': 'Device or User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the mapping already exists
        if user not in device.users.all():
            device.users.add(user)
            device.save()
            return Response({'status': 'user added to device'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'user already mapped to device'}, status=status.HTTP_200_OK)

        # device = self.get_object()  # This retrieves the Device instance based on the provided pk (primary key)
        # user = request.user
        
        # if user not in device.users.all():
        #     device.users.add(user)
        #     device.save()
        #     return Response({'status': 'user added to device'}, status=status.HTTP_200_OK)
        # else:
        #     return Response({'status': 'user already mapped to device'}, status=status.HTTP_200_OK)
    
    # @action(detail=True, methods=['post'])
    # def unmap_device(self, request, pk=None):
    #     device = self.get_object()
    #     user = request.user

    #     if user in device.users.all():
    #         device.users.remove(user)
    #         device.save()
    #         return Response({'status': 'device unmapped from user'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'status': 'user not mapped to device'}, status=status.HTTP_200_OK)