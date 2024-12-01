from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from .models import User, Group, UserClass, ClassTable
from .serializers import LoginSerializer, UserSerializer, GroupSerializer, ClassSerializer, UserClassSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from rest_framework.decorators import action


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
    permission_classes = [IsAuthenticated]
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











class RegisterUserView(APIView):
    permission_classes = [AllowAny]  # No authentication required to register a new user

    @swagger_auto_schema(
        operation_description="Register a new user by providing necessary details.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
                'university': openapi.Schema(type=openapi.TYPE_STRING, description='University'),
            },
            required=['username', 'password', 'email']
        ),
        responses={
            201: 'User created successfully',
            400: 'Validation error',
        }
    )
    def post(self, request, *args, **kwargs):
        # Use UserSerializer to validate incoming request data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Save the new user to the database
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        # If validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)









class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new group.",
        request_body=GroupSerializer,
        responses={
            201: 'Group created successfully',
            400: 'Validation error',
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response({'message': 'Group created successfully', 'group_id': group.group_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddGroupMemberView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add a new member to an existing group.",
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID of the user to add", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Member added successfully',
            404: 'Group or user not found',
            400: 'Validation error',
        }
    )
    def post(self, request, group_id, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate that the group exists and add the user to the group if found
        try:
            group = Group.objects.get(group_id=group_id)
            # Parse the members field, add the new member, and update the field
            members_list = group.members.split(',') if group.members else []
            if user_id not in members_list:
                members_list.append(user_id)
                group.members = ','.join(members_list)
                group.save()
                return Response({'message': 'Member added successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'User is already a member of the group'}, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        
class RemoveGroupMemberView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove a member from an existing group.",
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID of the user to remove", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Member removed successfully',
            404: 'Group not found',
            400: 'Validation error',
        }
    )
    def post(self, request, group_id, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(group_id=group_id)
            # Parse the members field, remove the member, and update the field
            members_list = group.members.split(',') if group.members else []
            if user_id in members_list:
                members_list.remove(user_id)
                group.members = ','.join(members_list)
                group.save()
                return Response({'message': 'Member removed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'User is not a member of the group'}, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

class ChangeGroupNameView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change the name of an existing group.",
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group", type=openapi.TYPE_INTEGER),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'group_name': openapi.Schema(type=openapi.TYPE_STRING, description="New name for the group")
            },
            required=['group_name']
        ),
        responses={
            200: 'Group name changed successfully',
            404: 'Group not found',
            400: 'Validation error',
        }
    )
    def post(self, request, group_id, *args, **kwargs):
        group_name = request.data.get('group_name')
        if not group_name:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(group_id=group_id)
            group.group_name = group_name
            group.save()
            return Response({'message': 'Group name changed successfully'}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

class DeleteGroupView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete an existing group.",
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_PATH, description="ID of the group", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: 'Group deleted successfully',
            404: 'Group not found',
        }
    )
    def delete(self, request, group_id, *args, **kwargs):
        try:
            group = Group.objects.get(group_id=group_id)
            group.delete()
            return Response({'message': 'Group deleted successfully'}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        







class CreateClassAndLinkView(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new class and link it to the user.",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID of the user", type=openapi.TYPE_INTEGER),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'class_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the class")
            },
            required=['class_name']
        ),
        responses={
            201: 'Class created and linked successfully',
            400: 'Validation error',
            404: 'User not found',
        }
    )
    def post(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        class_name = request.data.get('class_name')

        if not user_id or not class_name:
            return Response({'error': 'User ID and class name are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create a new class linked to the user's university
        class_instance = ClassTable.objects.create(class_name=class_name, university=user.university)

        # Link the class to the user via the UserClass model
        UserClass.objects.create(user=user, class_instance=class_instance)

        return Response({'message': 'Class created and linked successfully', 'class_id': class_instance.class_id}, status=status.HTTP_201_CREATED)
