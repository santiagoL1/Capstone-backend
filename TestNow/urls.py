# urls.py
from django.urls import path
from .views import LoginView, UserDetailView, GeminiAPI, CreateGroupView, AddGroupMemberView, RemoveGroupMemberView, ChangeGroupNameView, DeleteGroupView, RegisterUserView, CreateClassAndLinkView, GetUserClassesView, DeleteUserClassView, createFlashCard, createFlashCardSet, setLinkToClass, setLinkToUser, updateFlashCard, updateFlashCardSet, deleteFlashCardSet, deleteFlashCard

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('gemini/', GeminiAPI.as_view(), name='gemini_api'), 
    path('create-group/', CreateGroupView.as_view(), name='create-group'),
    path('add-group-member/<int:group_id>/', AddGroupMemberView.as_view(), name='add-group-member'),
    path('remove-group-member/<int:group_id>/', RemoveGroupMemberView.as_view(), name='remove-group-member'),
    path('change-group-name/<int:group_id>/', ChangeGroupNameView.as_view(), name='change-group-name'),
    path('delete-group/<int:group_id>/', DeleteGroupView.as_view(), name='delete-group'),
    path('register/', RegisterUserView.as_view(), name='register-user'),  # Added new endpoint
    path('create-class-and-link/', CreateClassAndLinkView.as_view(), name='create-class-and-link'),
    path('get-user-classes', GetUserClassesView.as_view(), name='get-user-classes'),
    path('delete-class/', DeleteUserClassView.as_view(), name='delete-class'),
    path('flashcard/create/', createFlashCard.as_view(), name='create_flashcard'),
    path('flashcardset/create/', createFlashCardSet.as_view(), name='create_flashcard_set'),
    path('flashcard/set-link-class/', setLinkToClass.as_view(), name='set_link_to_class'),
    path('flashcard/set-link-user/', setLinkToUser.as_view(), name='set_link_to_user'),
    path('flashcard/update/', updateFlashCard.as_view(), name='update_flashcard'),
    path('flashcardset/update/', updateFlashCardSet.as_view(), name='update_flashcard_set'),
    path('flashcardset/delete/', deleteFlashCardSet.as_view(), name='delete_flashcard_set'),
    path('flashcard/delete/', deleteFlashCard.as_view(), name='delete_flashcard'),
]