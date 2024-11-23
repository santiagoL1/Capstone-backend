from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import User
from .serializers import LoginSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from .services import ExternalAPIService
#Gemini API Imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from django.views import View
from django.utils.decorators import method_decorator
import json
import google.generativeai as genai
from django.conf import settings
from drf_yasg import openapi


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
            # Authenticate using the Django authentication system
                user = authenticate(username=username, password=password)
                if user is not None:
                    try:
                        refresh = RefreshToken.for_user(user)
                    except Exception as token_error:
                        print(f"Error while generating token: {token_error}")
                        return Response({'error': f'Error generating token: {str(token_error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'id': user.id,
                        'message': 'Login successful'
                    }, status=status.HTTP_200_OK)
                else:
                    # If credentials are incorrect
                    print("Invalid Credentials for user:", username)
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                print(f"Error occurred while querying users: {e}")

            
        # If serializer validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        security=[{'Bearer': []}],  # Add this line to enforce Bearer authentication
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

        
class GeminiAPI(APIView):
    """View to handle API calls to Google Gemini."""
    @swagger_auto_schema(
        operation_summary="Generate response from Google Gemini",
        operation_description=(
            "Accepts a prompt in the request body and generates a response using Google Gemini's generative AI model."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "prompt": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The input prompt for the Google Gemini API",
                )
            },
            required=["prompt"],
        ),
        responses={
            200: openapi.Response(
                description="Successful response from Google Gemini",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "response": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="The generated response from Google Gemini API",
                        )
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message describing the issue",
                        )
                    },
                ),
            ),
            500: openapi.Response(
                description="Server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message describing the issue",
                        )
                    },
                ),
            ),
        },
    )

    def post(self, request, *args, **kwargs):
        """Handles POST requests for Gemini API responses."""
        try:
            # Parse JSON body
            body = json.loads(request.body)
            prompt = body.get("prompt", "")
            
            if not prompt:
                return JsonResponse({"error": "Prompt is required."}, status=400)

            # Call Gemini API
            gemini_response = self.generate_gemini_response(prompt)

            # Return response
            if "error" in gemini_response:
                return JsonResponse(gemini_response, status=500)

            return JsonResponse({"response": gemini_response}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {e}"}, status=500)

    @staticmethod
    def configure_genai():
        """Configures Google Generative AI client."""
        genai.configure(api_key=settings.EXTERNAL_API['API_KEY'])

    @staticmethod
    def generate_gemini_response(prompt: str, model_name="gemini-1.5-flash"):
        """Generates a response from the Google Gemini API."""
        try:
            # Configure Generative AI client
            GeminiAPI.configure_genai()

            # Initialize the model
            model = genai.GenerativeModel(model_name)

            # Generate the content
            response = model.generate_content(prompt)

            # Convert the response to a serializable format
            if hasattr(response, 'to_dict'):  # If a helper method exists to convert to a dict
                return response.to_dict()
            else:
                # Manually extract necessary fields
                return {
                    "text": response.text,  # Assuming `text` holds the generated content
                    "metadata": getattr(response, "metadata", {})  # Optional metadata
                }
        except Exception as e:
            return {"error": f"Gemini API error: {e}"}
