from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

class UserRoleManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        """Yangi foydalanuvchini yaratish."""
        if not phone:
            raise ValueError("Telefon raqam kiritilishi shart")
        extra_fields.setdefault("is_active", True)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """Superfoydalanuvchini yaratish."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun `is_staff=True` bo‘lishi shart")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun `is_superuser=True` bo‘lishi shart")

        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    """Foydalanuvchi modeli."""
    GENDER_CHOICES = [
        ('male', 'Erkak'),
        ('female', 'Ayol'),
        ('other', 'Boshqa'),
    ]

    full_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserRoleManager()
    username = None  # Username maydoni mavjud emas

    USERNAME_FIELD = 'phone'  # Telefon raqami foydalanuvchi nomi sifatida ishlatiladi
    REQUIRED_FIELDS = ['email', 'full_name']  # Ro'yxatdan o'tish uchun zarur maydonlar

    def tokens(self):
        """JWT tokenlarini yaratish."""
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def __str__(self):
        """Foydalanuvchini ko'rsatish uchun."""
        return self.full_name or self.phone
