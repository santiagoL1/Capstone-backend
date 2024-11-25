# urls.py
from django.urls import path
from .views import LoginView, UserDetailView, GeminiAPI, RegisterUserView  # Import RegisterUserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('gemini/', GeminiAPI.as_view(), name='gemini_api'),
    path('register/', RegisterUserView.as_view(), name='register-user'),  # Added new endpoint
]



