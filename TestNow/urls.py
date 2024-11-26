# urls.py
from django.urls import path
from .views import LoginView, UserDetailView, GeminiAPI, CreateGroupView, AddGroupMemberView, RemoveGroupMemberView, ChangeGroupNameView, DeleteGroupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('gemini/', GeminiAPI.as_view(), name='gemini_api'), 
    path('create-group/', CreateGroupView.as_view(), name='create-group'),
    path('add-group-member/<int:group_id>/', AddGroupMemberView.as_view(), name='add-group-member'),
    path('remove-group-member/<int:group_id>/', RemoveGroupMemberView.as_view(), name='remove-group-member'),
    path('change-group-name/<int:group_id>/', ChangeGroupNameView.as_view(), name='change-group-name'),
    path('delete-group/<int:group_id>/', DeleteGroupView.as_view(), name='delete-group'),
    #path('register/', RegisterUserView.as_view(), name='register-user'),  # Added new endpoint
]



