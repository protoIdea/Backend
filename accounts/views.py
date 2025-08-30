from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserLoginSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, UserDashboardSerializer
)


class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()

                    # Generate tokens
                    refresh = RefreshToken.for_user(user)

                    return Response({
                        'message': 'User registered successfully',
                        'user': UserSerializer(user).data,
                        'tokens': {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)
                        }
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Registration failed',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Update last login
            user.save()

            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            logout(request)
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDashboardView(APIView):
    """User dashboard data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDashboardSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Request password reset"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)

                # Generate reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Send reset email
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                return Response({
                    'message': 'Password reset email sent successfully'
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                # Don't reveal if email exists or not
                return Response({
                    'message': 'Password reset email sent successfully'
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(
                    serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)

                if default_token_generator.check_token(user, serializer.validated_data['token']):
                    user.set_password(
                        serializer.validated_data['new_password'])
                    user.save()

                    return Response({
                        'message': 'Password reset successfully'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Invalid reset token'
                    }, status=status.HTTP_400_BAD_REQUEST)

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'error': 'Invalid reset link'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """List all users (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['is_active', 'is_premium', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User detail view (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics"""
    user = request.user

    stats = {
        'total_budgets': user.budget_set.count(),
        'total_expenses': user.expense_set.count(),
        'total_categories': user.category_set.count(),
        'account_age_days': (user.date_joined.date() - user.date_joined.date()).days,
        'is_premium': user.is_premium,
        'currency': user.currency,
    }

    return Response(stats, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_notifications(request):
    """Toggle user notification preferences"""
    user = request.user
    notification_type = request.data.get('type')

    if notification_type == 'email':
        user.email_notifications = not user.email_notifications
    elif notification_type == 'push':
        user.push_notifications = not user.push_notifications
    else:
        return Response({
            'error': 'Invalid notification type'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.save()

    return Response({
        'message': f'{notification_type.title()} notifications toggled',
        'enabled': getattr(user, f'{notification_type}_notifications')
    }, status=status.HTTP_200_OK)

