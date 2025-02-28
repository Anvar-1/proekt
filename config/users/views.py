import requests
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .location import get_location
from .serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer, PasswordResetSerializer, \
    PasswordChangeSerializer
from .models import User
from django.conf import settings


class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
        location_data = get_location(ip_address)

        if location_data and location_data['status'] == 'success':
            city = location_data.get('city')
            country = location_data.get('country')
            # Qo'shimcha ma'lumotlar bilan ishlash
        else:
            city = country = None

        user = serializer.save()
        user.ip_address = ip_address  # IP manzilini saqlash
        user.city = city  # Agar kerak bo'lsa, shaharni saqlash
        user.country = country  # Agar kerak bo'lsa, mamlakatni saqlash
        user.save()
    # def get_country_from_ip(self, ip_address):
    #     access_key = settings.IPSTACK_ACCESS_KEY  # API kalitini olamiz
    #     url = f'http://api.ipstack.com/{ip_address}?access_key={access_key}'
    #
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             data = response.json()
    #             print(data)  # Olingan ma'lumotlarni ko'rsatish
    #             return data.get('country_name')  # Davlat nomini qaytarish
    #         else:
    #             print(f"Xatolik: {response.status_code} - {response.text}")
    #             return None
    #     except Exception as e:
    #         print(f"Xatolik yuz berdi: {str(e)}")  # Xatolik haqida ma'lumot
    #         return None


class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "Bu himoyalangan API. Siz tizimga muvaffaqiyatli kirdingiz!"})


class UserLogin(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']
            user = authenticate(phone=phone, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid Credentials'}, status=400)
        return Response(serializer.errors, status=400)

class PasswordResetView(generics.CreateAPIView):
    serializer_class = PasswordResetSerializer

class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer


class UserUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDelete(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Muvaffaqiyatli chiqildi!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Xatolik yuz berdi!"}, status=status.HTTP_400_BAD_REQUEST)
