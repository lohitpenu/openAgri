from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device
from .serializers import DeviceSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(users=[request.user])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        user = request.user
        devices = Device.objects.filter(users=user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
    
    # admin-api
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin(self, request):        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        
    def retrieve(self, request, pk=None):
        device = self.get_object()
        
        # admin-api
        if request.user in device.users.all() or request.user.is_superuser:
            serializer = self.get_serializer(device)
            return Response(serializer.data)
        else:
            raise PermissionDenied("You do not have permission to access this resource.")
 
    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def map_user(self, request, pk=None):
        device = self.get_object()  # This retrieves the Device instance based on the provided pk (primary key)
        user = request.user
        
        if user not in device.users.all():
            device.users.add(user)
            device.save()
            return Response({'status': 'user added to device'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'user already mapped to device'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unmap_user(self, request, pk=None):
        device = self.get_object()
        user = request.user

        if user in device.users.all():
            device.users.remove(user)
            device.save()
            return Response({'status': 'device unmapped from user'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'user not mapped to device'}, status=status.HTTP_200_OK)

    # admin-api
    @action(detail=True, url_path='map_user/admin', methods=['post'], permission_classes=[IsAdminUser])
    def map_user_admin(self, request, pk=None):
        # Ensure the request is made by an admin
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        device = self.get_object()
        user_id = request.data.get('user_id')

        # Retrieve the user instance
        user = get_object_or_404(User, pk=user_id)

        # Check if the user is already mapped to the device
        if user in device.users.all():
            return Response({'status': 'User already mapped to device'}, status=status.HTTP_200_OK)

        # Add the user to the device
        device.users.add(user)
        device.save()

        return Response({'status': 'User mapped to device'}, status=status.HTTP_200_OK)

    # admin-api
    @action(detail=True, url_path='unmap_user/admin', methods=['post'], permission_classes=[IsAdminUser])
    def unmap_user_admin(self, request, pk=None):
        # Ensure the request is made by an admin
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        device = self.get_object()
        user_id = request.data.get('user_id')

        # Retrieve the user instance
        user = get_object_or_404(User, pk=user_id)

        # Check if the user is mapped to the device
        if user in device.users.all():
            device.users.remove(user)
            device.save()
            return Response({'status': 'User unmapped from device'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'User not mapped to device'}, status=status.HTTP_200_OK)

