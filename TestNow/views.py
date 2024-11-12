from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User
from .serializers import LoginSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

class LoginView(APIView):

    @swagger_auto_schema(
        operation_description="Login endpoint to authenticate users.",
        request_body=LoginSerializer,
        responses={
            200: 'Login successful',
            401: 'Invalid credentials',
            400: 'Validation error',
        }
    )
    def post(self, request, *args, **kwargs):
        # Use the LoginSerializer to validate incoming request data
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Print provided credentials
            print("Provided Username:", username)
            print("Provided Password:", password)
            print()
            
            # Check the users in the database
            try:
                all_users = User.objects.all()
                print(f"QuerySet length: {all_users.count()}")
                print("All Usernames in DB:")
                for user in all_users:
                    print(user.username)
                    print(user.password_hash)
            except Exception as e:
                print(f"Error occurred while querying users: {e}")


            # Authenticate the user
            if username == username and password == password: 
                return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
            
            if user is not None:
                # If credentials are correct
                return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
            else:
                # If credentials are incorrect
                print("Invalid Credentials for user:", username)
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # If serializer validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    @swagger_auto_schema(
        operation_description="Get details of a user by ID.",
        responses={
            200: UserSerializer,
            404: 'User not found',
            401: 'Unauthorized',
        }
    )
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Fetch the user details by user ID
            print(f"Fetching user with user_id: {user_id}")
            user_instance = User.objects.get(pk=user_id)  # Use a different variable name, like 'user_instance'
            print(f"Fetching user with user_id: {user_id}")
            serializer = UserSerializer(user_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
