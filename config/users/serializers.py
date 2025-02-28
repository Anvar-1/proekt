from rest_framework import serializers
from .models import User
from .utils import send_sms
import random
from .utils import send_email

class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES)
    email = serializers.EmailField(required=True)  # Email maydoni kiritildi

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email', 'password', 'gender']
        extra_kwargs = {
            'password': {'write_only': True},
            'full_name': {'required': True},
        }

    def create(self, validated_data):
        # Telefon raqamini tekshirish
        if User.objects.filter(phone=validated_data['phone']).exists():
            raise serializers.ValidationError({"phone": "Bu telefon raqami allaqon ro'yxatdan o'tgan."})

        user = User.objects.create_user(
            phone=validated_data['phone'],
            full_name=validated_data['full_name'],
            email=validated_data['email'],  # Emailni kiritish
            password=validated_data['password'],
            gender=validated_data['gender']
        )
        send_sms(validated_data['phone'], "Siz muvaffaqiyatli ro'yhatdan o'tdingiz")
        return user

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "full_name": instance.full_name,
            "phone": instance.phone,
            'email': instance.email,
            "password": instance.password,
            "ip_address": instance.ip_address,
            "country": instance.country,
            "gender": instance.gender,
            "refresh_token": instance.tokens()['refresh'],
            "access_token": instance.tokens()['access']
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone', 'email', 'ip_address', 'interests', 'gender', 'is_active', 'is_staff']
        extra_kwargs = {
            'ip_address': {'read_only': True},
            'interests': {'allow_blank': True},
        }

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzil bilan foydalanuvchi topilmadi.")
        return value


    def save(self):
        email = self.validated_data['email']
        code = random.randint(100000, 999999)
        message = f"Sizning tasdiqlash kodingiz: {code}. Iltimos, parolingizni tiklash uchun ushbu kodni kiriting."
        send_email(email, "Parolni tiklash uchun tasdiqlash kodi", message)
        return code

class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzil bilan foydalanuvchi topilmadi.")
        return value

    def validate_code(self, value):
        return value

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"phone": "Bunday telefon raqami mavjud emas."})

        return attrs