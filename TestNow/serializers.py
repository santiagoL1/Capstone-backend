from rest_framework import serializers
from .models import User, ClassTable, UserClass, FlashCardSet, FlashCards, ActivityLog

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        """
        Validate user credentials.
        """
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'university']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'university', 'password', 'confirm_password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'university': {'required': True},
        }

    def validate(self, data):
        """
        Ensure password and confirm_password match, and perform additional validation on user fields.
        """
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Password match validation
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Email validation (example: check if it's already taken)
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError("A user with this username already exists.")

        return data

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        """
        # Remove confirm_password from the data, as it's not needed for user creation
        validated_data.pop('confirm_password')

        # Create and save the user object with the hashed password
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            university=validated_data.get('university', ''),
            password=validated_data['password']  # This will be hashed by create_user
        )
        return user



