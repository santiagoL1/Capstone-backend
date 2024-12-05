from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from .models import User, Group, UserClass, ClassTable, FlashCardSet, ActivityLog, FlashCards
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
from django.utils import timezone
from django.shortcuts import get_object_or_404

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
            
            # Check the users in the database
            try:
            # Authenticate using the Django authentication system
                user = authenticate(username=username, password=password)
                if user is not None:
                    try:
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        refresh = RefreshToken.for_user(user)
                        ActivityLog.objects.create(
                            user=user,
                            action_done="User logged in"
                        )
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
            ActivityLog.objects.create(
                user=request.user,
                action_done=f"error: {TypeError}"
            )
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ActivityLog.objects.create(
                user=request.user,
                action_done=f"Fetched user details for user_id: {user_id}"
            )
            user_instance = User.objects.get(pk=user_id)  
            serializer = UserSerializer(user_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            ActivityLog.objects.create(
                user=request.user,
                action_done=f"error user: {user_id} does not exist"
            )
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
                ActivityLog.objects.create(
                    user=request.user,
                    action_done=f"Prompt is required: no prompt given"
                )
                return JsonResponse({"error": "Prompt is required."}, status=400)

            # Call Gemini API
            gemini_response = self.generate_gemini_response(prompt)

            # Return response
            if "error" in gemini_response:
                ActivityLog.objects.create(
                    user=request.user,
                    action_done=f"Error in gemini response: {e}"
                )
                return JsonResponse(gemini_response, status=500)

            ActivityLog.objects.create(
                user=request.user,
                action_done=f"200 response status for gemini: sucessful query"
            )
            return JsonResponse({"response": gemini_response}, status=200)
        
        except json.JSONDecodeError:
            ActivityLog.objects.create(
                user=request.user,
                action_done=f"Invalid JSON payload: {e}"
            )
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            ActivityLog.objects.create(
                user=request.user,
                action_done=f"Exception: {e}"
            )
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
            uni = user.university
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create a new class linked to the user's university
        class_instance = ClassTable.objects.create(class_name=class_name, university=uni)

        # Link the class to the user via the UserClass model
        #UserClass.objects.create(user=user, class_instance=class_instance)
        UserClass.objects.create(user=user, class_model=class_instance)


        return Response({'message': 'Class created and linked successfully', 'class_id': class_instance.class_id}, status=status.HTTP_201_CREATED)





class GetUserClassesView(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all classes linked to a user.",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID of the user", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Class ID"),
                        'class_name': openapi.Schema(type=openapi.TYPE_STRING, description="Class Name"),
                        'university': openapi.Schema(type=openapi.TYPE_STRING, description="University"),
                    }
                )
            ),
            404: 'User not found',
        }
    )
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Query to get all classes linked to the user
        user_classes = UserClass.objects.filter(user=user).select_related('class_model')
        
        # Extract data efficiently without loops
        classes_data = user_classes.values(
            'class_model__class_id',
            'class_model__class_name',
            'class_model__university'
        )

        # Rename keys to match the desired output
        classes = [
            {
                'class_id': entry['class_model__class_id'],
                'class_name': entry['class_model__class_name'],
                'university': entry['class_model__university']
            }
            for entry in classes_data
        ]

        return Response(classes, status=status.HTTP_200_OK)
    




class DeleteUserClassView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a class associated with a user based on class name, including all related flashcard sets.",
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="ID of the user", type=openapi.TYPE_INTEGER),
            openapi.Parameter('class_name', openapi.IN_QUERY, description="Name of the class", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Class and related flashcard sets deleted successfully',
            400: 'Validation error',
            404: 'Class or User not found',
        }
    )
    def delete(self, request, *args, **kwargs):
        # Extract query parameters
        user_id = request.query_params.get('user_id')
        class_name = request.query_params.get('class_name')

        if not user_id or not class_name:
            return Response({'error': 'User ID and class name are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch the UserClass entry and the associated class
            user_class = UserClass.objects.select_related('class_model').get(
                user=user, class_model__class_name=class_name
            )

            # Get the associated class instance
            class_instance = user_class.class_model

            # Delete all FlashCardSet entries related to the class
            FlashCardSet.objects.filter(class_model=class_instance).delete()

            # Delete the UserClass entry
            user_class.delete()

            # Delete the ClassTable entry
            class_instance.delete()

        except UserClass.DoesNotExist:
            return Response({'error': 'Class not found for this user'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': f'Class \"{class_name}\" and all related flashcard sets deleted successfully for user \"{user.username}\".'
        }, status=status.HTTP_200_OK)

class createFlashCard(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a new flashcard",
        operation_description="This endpoint allows authenticated users to create a new flashcard by providing a question, answer, and set ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'set_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard set'),
                'question': openapi.Schema(type=openapi.TYPE_STRING, description='Question text for the flashcard'),
                'answer': openapi.Schema(type=openapi.TYPE_STRING, description='Answer text for the flashcard'),
            },
            required=['set_id', 'question', 'answer'],
        ),
        responses={
            201: openapi.Response(
                description="Flashcard created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'card_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the created flashcard'),
                        'set_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard set'),
                        'question': openapi.Schema(type=openapi.TYPE_STRING, description='Question text'),
                        'answer': openapi.Schema(type=openapi.TYPE_STRING, description='Answer text'),
                    },
                ),
            ),
            400: "Bad Request - Validation Error",
            401: "Unauthorized - Authentication Required",
        },
    )
    def post(self, request):
        """
        Handles the creation of a new flashcard.
        """
        data = request.data
        set_id = data.get('set_id')
        question = data.get('question')
        answer = data.get('answer')

        if not all([set_id, question, answer]):
            return Response({"error": "All fields (set_id, question, answer) are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the flashcard set
        try:
            flashcard_set = FlashCardSet.objects.get(set_id=set_id)
        except FlashCardSet.DoesNotExist:
            return Response({"error": "Flashcard set with the provided set_id does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Save to database
        flashcard = FlashCards.objects.create(
            flash_card_set=flashcard_set, question=question, answer=answer
        )

        return Response({
            "card_id": flashcard.card_id,
            "set_id": flashcard_set.set_id,
            "question": flashcard.question,
            "answer": flashcard.answer,
        }, status=status.HTTP_201_CREATED)


class createFlashCardSet(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a new flashcard set",
        operation_description="This endpoint allows authenticated users to create a new flashcard set by providing a set name, class ID, and user ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'set_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the flashcard set'),
                'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the class'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user creating the set'),
            },
            required=['set_name', 'class_id', 'user_id'],  # Mandatory fields
        ),
        responses={
            201: openapi.Response(
                description="Flashcard set created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'set_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the created flashcard set'),
                        'set_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the flashcard set'),
                        'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the class'),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                    },
                ),
            ),
            400: "Bad Request - Validation Error",
            401: "Unauthorized - Authentication Required",
        },
    )
    def post(self, request, *args, **kwargs):
        # Extract data from the request body
        set_name = request.data.get('set_name')
        class_id = request.data.get('class_id')
        user_id = request.data.get('user_id')

        if not set_name or not class_id or not user_id:
            return Response({"error": "All fields (set_name, class_id, user_id) are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the Class and User objects
        class_instance = get_object_or_404(ClassTable, class_id=class_id)
        user_instance = get_object_or_404(User, id=user_id)

        # Create a new FlashCardSet instance
        flashcard_set = FlashCardSet.objects.create(
            set_name=set_name,
            class_model=class_instance,
            user=user_instance
        )

        return Response({"message": "FlashCardSet created successfully."}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Retrieve flashcard sets by user or class",
        operation_description="This endpoint allows authenticated users to retrieve flashcard sets by providing user ID or class ID as query parameters.",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="ID of the user whose flashcard sets are to be retrieved",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'class_id',
                openapi.IN_QUERY,
                description="ID of the class whose flashcard sets are to be retrieved",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="List of flashcard sets",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'set_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard set'),
                            'set_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the flashcard set'),
                            'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the class'),
                            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                        },
                    ),
                ),
            ),
            400: "Bad Request - Validation Error",
            401: "Unauthorized - Authentication Required",
        },
    )
    def get(self, request):
        """
        Retrieves flashcard sets by user ID or class ID.
        """
        user_id = request.query_params.get('user_id')
        class_id = request.query_params.get('class_id')

        if not user_id and not class_id:
            return Response({"error": "Either user_id or class_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Query database
        flashcard_sets = FlashCardSet.objects.all()
        if user_id:
            try:
                user_instance = User.objects.get(id=user_id)
                flashcard_sets = flashcard_sets.filter(user=user_instance)
            except User.DoesNotExist:
                return Response({"error": "User with the provided user_id does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if class_id:
            try:
                class_instance = ClassTable.objects.get(class_id=class_id)
                flashcard_sets = flashcard_sets.filter(class_model=class_instance)
            except ClassTable.DoesNotExist:
                return Response({"error": "Class with the provided class_id does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        response_data = [
            {
                "set_id": flashcard_set.set_id,
                "set_name": flashcard_set.set_name,
                "class_id": flashcard_set.class_model.class_id,
                "user_id": flashcard_set.user.id,
            }
            for flashcard_set in flashcard_sets
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    
class setLinkToClass(APIView):
    """
    Links a flashcard set to a specific class.
    """
    def post(self, request, *args, **kwargs):
        set_id = request.data.get('set_id')
        class_id = request.data.get('class_id')

        flashcard_set = get_object_or_404(FlashCardSet, id=set_id)
        class_instance = get_object_or_404(ClassTable, id=class_id)

        # Link the flashcard set to the class
        flashcard_set.class_id = class_instance
        flashcard_set.save()

        return Response({"message": "Flashcard set linked to class successfully."}, status=status.HTTP_200_OK)


class setLinkToUser(APIView):
    """
    Links a flashcard set to a specific user.
    """
    def post(self, request, *args, **kwargs):
        set_id = request.data.get('set_id')
        user_id = request.data.get('user_id')

        flashcard_set = get_object_or_404(FlashCardSet, id=set_id)
        user_instance = get_object_or_404(User, id=user_id)

        # Link the flashcard set to the user
        flashcard_set.user_id = user_instance
        flashcard_set.save()

        return Response({"message": "Flashcard set linked to user successfully."}, status=status.HTTP_200_OK)


class updateFlashCard(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update a flashcard",
        operation_description="This endpoint allows updating the question or answer of an existing flashcard.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'card_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard'),
                'question': openapi.Schema(type=openapi.TYPE_STRING, description='Updated question text'),
                'answer': openapi.Schema(type=openapi.TYPE_STRING, description='Updated answer text'),
            },
            required=['card_id'],
        ),
        responses={
            200: "Flashcard updated successfully",
            404: "Flashcard not found",
            400: "Bad Request - Validation Error",
        },
    )
    def put(self, request):
        data = request.data
        card_id = data.get('card_id')
        question = data.get('question')
        answer = data.get('answer')

        if not card_id:
            return Response({"error": "card_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flashcard = FlashCards.objects.get(card_id=card_id)
            if question:
                flashcard.question = question
            if answer:
                flashcard.answer = answer
            flashcard.save()

            return Response({"message": "Flashcard updated successfully."}, status=status.HTTP_200_OK)
        except FlashCards.DoesNotExist:
            return Response({"error": "Flashcard not found."}, status=status.HTTP_404_NOT_FOUND)

class updateFlashCardSet(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update a flashcard set",
        operation_description="This endpoint allows updating the name of an existing flashcard set.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'set_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard set'),
                'set_name': openapi.Schema(type=openapi.TYPE_STRING, description='Updated name of the flashcard set'),
            },
            required=['set_id', 'set_name'],
        ),
        responses={
            200: "Flashcard set updated successfully",
            404: "Flashcard set not found",
            400: "Bad Request - Validation Error",
        },
    )
    def put(self, request):
        data = request.data
        set_id = data.get('set_id')
        set_name = data.get('set_name')

        if not set_id or not set_name:
            return Response({"error": "set_id and set_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flashcard_set = FlashCardSet.objects.get(set_id=set_id)
            flashcard_set.set_name = set_name
            flashcard_set.save()

            return Response({"message": "Flashcard set updated successfully."}, status=status.HTTP_200_OK)
        except FlashCardSet.DoesNotExist:
            return Response({"error": "Flashcard set not found."}, status=status.HTTP_404_NOT_FOUND)

class deleteFlashCard(APIView):
    
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a flashcard",
        operation_description="This endpoint deletes a flashcard by its ID.",
        manual_parameters=[
            openapi.Parameter('card_id', openapi.IN_QUERY, description='ID of the flashcard to delete', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: "Flashcard deleted successfully",
            404: "Flashcard not found",
            400: "Bad Request - Validation Error",
        },
    )
    def delete(self, request):
        card_id = request.query_params.get('card_id')

        if not card_id:
            return Response({"error": "card_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flashcard = FlashCards.objects.get(card_id=card_id)
            flashcard.delete()

            return Response({"message": "Flashcard deleted successfully."}, status=status.HTTP_200_OK)
        except FlashCards.DoesNotExist:
            return Response({"error": "Flashcard not found."}, status=status.HTTP_404_NOT_FOUND)

class deleteFlashCardSet(APIView):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a flashcard set",
        operation_description="This endpoint deletes a flashcard set by its ID.",
        manual_parameters=[
            openapi.Parameter('set_id', openapi.IN_QUERY, description='ID of the flashcard set to delete', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: "Flashcard set deleted successfully",
            404: "Flashcard set not found",
            400: "Bad Request - Validation Error",
        },
    )
    def delete(self, request):
        set_id = request.query_params.get('set_id')

        if not set_id:
            return Response({"error": "set_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flashcard_set = FlashCardSet.objects.get(set_id=set_id)
            flashcard_set.delete()

            return Response({"message": "Flashcard set deleted successfully."}, status=status.HTTP_200_OK)
        except FlashCardSet.DoesNotExist:
            return Response({"error": "Flashcard set not found."}, status=status.HTTP_404_NOT_FOUND)