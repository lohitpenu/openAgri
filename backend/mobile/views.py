from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Mobile, Device, Image
from .serializers import MobileSerializer, ImageSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from utils.utils import DeviceType
from django.http import FileResponse
from django.http import Http404

class MobileViewSet(viewsets.ModelViewSet):
    queryset = Mobile.objects.all()
    serializer_class = MobileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Extract the device ID and check its type and ownership
        device_id = request.data.get('device')
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        if device.type.id != DeviceType.MOBILE:
            return Response({'error': 'Device is not of type MOBILE'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_superuser and request.user not in device.users.all():
            return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)
        
        # Serialize the data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-location')
    def by_location(self, request):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')

        if not lat or not long:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            return Response({'error': 'Invalid latitude or longitude'}, status=status.HTTP_400_BAD_REQUEST)

        mobiles = Mobile.objects.filter(geo_location_lat=lat, geo_location_long=long, device__users=request.user)

        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-location/admin', permission_classes=[IsAdminUser])
    def by_location_admin(self, request):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')

        if not lat or not long:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            return Response({'error': 'Invalid latitude or longitude'}, status=status.HTTP_400_BAD_REQUEST)

        mobiles = Mobile.objects.filter(geo_location_lat=lat, geo_location_long=long)

        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-device')
    def by_device(self, request):
        device_id = request.query_params.get('device_id')

        if not device_id:
            return Response({'error': 'Device ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and request.user not in device.users.all():
            return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)

        mobiles = Mobile.objects.filter(device=device)

        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='mapped-to-user')
    def mapped_to_user(self, request):
        mobiles = Mobile.objects.filter(device__users=request.user)

        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='mapped-to-user/admin')
    def mapped_to_any_user(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_superuser:
            return Response({'error': 'Only admin users can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

        mobiles = Mobile.objects.filter(device__users__id=user_id)
        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        try:
            mobile = self.get_object()
            device = mobile.device

            if device.type.id != DeviceType.MOBILE:
                return Response({'error': 'Device is not of type MOBILE'}, status=status.HTTP_400_BAD_REQUEST)

            if not request.user.is_superuser and request.user not in device.users.all():
                return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(mobile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile data not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, *args, **kwargs):
        mobile_id = request.data.get('mobile')
        if not mobile_id:
            return Response({"detail": "Mobile ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mobile = Mobile.objects.get(id=mobile_id, device__users=request.user)
        except Mobile.DoesNotExist:
            return Response({"detail": "Mobile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(mobile=mobile)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_multiple(self, request, *args, **kwargs):
        mobile_id = request.data.get('mobile')
        if not mobile_id:
            return Response({"detail": "Mobile ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mobile = Mobile.objects.get(id=mobile_id, device__users=request.user)
        except Mobile.DoesNotExist:
            return Response({"detail": "Mobile not found."}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('images')
        if not files:
            return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        images = []
        for file in files:
            image = Image(mobile=mobile, image_file=file)
            image.save()
            images.append(image)

        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def all(self, request):
        user = request.user  # Assuming user authentication is enabled
        mobile_id = request.query_params.get('mobile_data_id')
        if not mobile_id:
            return Response({"detail": "Mobile ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mobile = Mobile.objects.get(id=mobile_id, device__users=user)
        except Mobile.DoesNotExist:
            return Response({"detail": "Mobile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        images = Image.objects.filter(mobile=mobile)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def download(self, request, pk=None):
        user = request.user  # Assuming user authentication is enabled
        image_id = request.query_params.get('image_id')
        try:
            image = Image.objects.get(id=image_id, mobile__device__users=user)
        except Image.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serve the image file using FileResponse
        try:
            return FileResponse(image.image_file)
        except FileNotFoundError:
            raise Http404("Image not found.")