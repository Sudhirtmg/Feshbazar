from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email    = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = ["phone", "email", "password", "role"]

    def validate_role(self, value):
        allowed = [User.Role.CUSTOMER, User.Role.SHOP_OWNER]
        if value not in allowed:
            raise serializers.ValidationError(
                "You can only register as a customer or shop owner."
            )
        return value

    def create(self, validated_data):
        email = validated_data.pop("email", None)
        # convert empty string to None so unique constraint allows multiple blank emails
        if not email:
            email = None
        user = User.objects.create_user(email=email, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["phone"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid phone or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "phone", "email", "role", "profile_image", "date_joined"]
        read_only_fields = ["role", "date_joined"]