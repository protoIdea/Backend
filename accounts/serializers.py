from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'website', 'savings_goal', 'emergency_fund_goal',
            'default_budget_period', 'email_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            'date_of_birth', 'profile_picture', 'currency', 'monthly_income',
            'is_premium', 'email_notifications', 'push_notifications',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'profile', 'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'date_joined',
                            'last_login', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """Validate password confirmation"""
        if 'password' in attrs and 'password_confirm' not in attrs:
            raise serializers.ValidationError(
                "Password confirmation is required")

        if 'password' in attrs and attrs['password'] != attrs.get('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")

        return attrs

    def create(self, validated_data):
        """Create a new user with profile"""
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        # Create user
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()

        # Create profile
        UserProfile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()

        # Update profile
        if profile_data and hasattr(instance, 'profile'):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        elif profile_data:
            UserProfile.objects.create(user=instance, **profile_data)

        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 'first_name',
            'last_name', 'phone_number', 'currency', 'monthly_income', 'profile'
        ]

    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        # Check if username or email already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")

        return attrs

    def create(self, validated_data):
        """Create new user with profile"""
        profile_data = validated_data.pop('profile', {})
        validated_data.pop('password_confirm')

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create profile with default values
        UserProfile.objects.create(user=user, **profile_data)

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                "Must include username and password")

        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate password change data"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate email exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user found with this email address")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""

    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        """Validate password reset confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class UserDashboardSerializer(serializers.ModelSerializer):
    """Serializer for user dashboard data"""

    profile = UserProfileSerializer(read_only=True)
    total_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    total_expenses = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    remaining_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'profile_picture',
            'currency', 'monthly_income', 'is_premium', 'total_budget',
            'total_expenses', 'remaining_budget', 'profile'
        ]

