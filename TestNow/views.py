from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from drf_yasg.utils import swagger_auto_schema

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

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                # If credentials are correct
                return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
            else:
                # If credentials are incorrect
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # If serializer validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
