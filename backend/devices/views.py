from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device, Image
from .serializers import DeviceSerializer, ImageSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404

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

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, *args, **kwargs):
        device_id = request.data.get('device')
        if not device_id:
            return Response({"detail": "Device ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            device = Device.objects.get(id=device_id)
            if request.user in device.users.all() or request.user.is_superuser:
                device = Device.objects.get(id=device_id)
            else:
                return Response({"detail": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_multiple(self, request, *args, **kwargs):
        device_id = request.data.get('device')
        if not device_id:
            return Response({"detail": "Device ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            device = Device.objects.get(id=device_id)
            if request.user in device.users.all() or request.user.is_superuser:
                device = Device.objects.get(id=device_id)
            else:
                return Response({"detail": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('images')
        if not files:
            return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        images = []
        for file in files:
            image = Image(device=device, image_file=file)
            image.save()
            images.append(image)

        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def all(self, request):
        user = request.user  # Assuming user authentication is enabled
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({"detail": "Device ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            device = Device.objects.get(id=device_id)
            if request.user in device.users.all() or request.user.is_superuser:
                device = Device.objects.get(id=device_id)
            else:
                return Response({"detail": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        except Device.DoesNotExist:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
        
        images = Image.objects.filter(device=device)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def download(self, request, pk=None):
        user = request.user  # Assuming user authentication is enabled
        image_id = request.query_params.get('image_id')
        try:
            image = Image.objects.get(id=image_id)
            device = image.device
            if request.user in device.users.all() or request.user.is_superuser:
                pass
            else:
                return Response({"detail": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        except Image.DoesNotExist:
            return Response({"detail": "Image not found/No permission."}, status=status.HTTP_404_NOT_FOUND)

        # Serve the image file using FileResponse
        try:
            return FileResponse(image.image_file)
        except FileNotFoundError:
            raise Http404("Image not found.")