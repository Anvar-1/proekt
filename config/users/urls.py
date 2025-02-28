from django.urls import path
from .views import UserRegisterView, ProtectedView, LogoutView, UserLogin, UserUpdate, UserDelete, PasswordResetView, \
    PasswordChangeView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('update/<int:pk>/', UserUpdate.as_view(), name='user_update'),
    path('delete/<int:pk>/', UserDelete.as_view(), name='user_delete'),
    path('logout/', LogoutView.as_view(), name='logout'),

]