from rest_framework import serializers
from .models import User, Group, ClassTable, UserClass

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'university']  

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            university=validated_data.get('university', '')
        )
        return user

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group_id', 'group_name', 'members']

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTable
        fields = ['class_id', 'class_name', 'university']

class UserClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserClass
        fields = ['user', 'class_instance']
