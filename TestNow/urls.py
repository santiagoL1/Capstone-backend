# urls.py
from django.urls import path
from .views import LoginView, UserDetailView, GeminiAPI, CreateGroupView, AddGroupMemberView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('gemini/', GeminiAPI.as_view(), name='gemini_api'), 
    path('create-group/', CreateGroupView.as_view(), name='create-group'),
    path('add-group-member/<int:group_id>/', AddGroupMemberView.as_view(), name='add-group-member'),
]


