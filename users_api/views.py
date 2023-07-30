from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from machine_api.models import PhoneNumber, RecycleLog
from .models import LocationModel
from .services import (
    send_otp,
    send_reset_password_email,
    send_welcome_email,
    otp_set,
)
from .serializers import (
    LocationModelserializers,
    UserSerializer,
    UserProfileSerializer,
    SetNewPasswordSerializer,
    ResetPasswordEmailRequestSerializer,
    OTPSerializer,
    OTPOnlySerializer,
)

User = get_user_model()


# for signup
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=["PATCH"], serializer_class=OTPOnlySerializer)
    def verify_otp(self, request, pk=None):
        """to check if the user entered the correct otp or if he/she is already verified (is_active=True)"""
        instance = self.get_object()
        if (
            not instance.is_active
            and instance.otp_expiration
            and instance.otp == request.data.get("otp")
            and timezone.now() < instance.otp_expiration
        ):
            instance.is_active = True
            instance.otp_expiration = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.max_otp_out = None

            # send welcome email
            send_welcome_email(instance.email)

            # check if user phone number was used to recycle before and add the points to user account
            phone = PhoneNumber.objects.filter(
                phone_number=instance.phone_number
            ).first()

            if phone:
                instance.total_points += phone.points
                RecycleLog.objects.filter(phone=phone).update(user=instance)
                phone.delete()

            instance.save()

            return Response("Successfully verfied the user.", status=status.HTTP_200_OK)

        return Response(
            "User already verfied or otp is incorrect.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["GET"])
    def regenerate_otp(self, request, pk=None):
        """to regenerate otp until max try"""
        instance = self.get_object()
        if instance.max_otp_out and timezone.now() < instance.max_otp_out:
            waiting_time = instance.max_otp_out - timezone.now()

            return Response(
                f"Max OTP try reached, try after: {waiting_time.seconds // 60} minute.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = otp_set(user=instance)

        send_otp(instance)

        return Response(
            "Successfully regenrated the new OTP.", status=status.HTTP_200_OK
        )


# for edit_profile
class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    lookup_field = "pk"
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "user profile updated successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class RequestPasswordResetEmail(generics.GenericAPIView):
    """Send password reset email"""

    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data.get("email", "")
        user = User.objects.filter(email=email).first()

        if user:
            if user.max_otp_out and timezone.now() < user.max_otp_out:
                waiting_time = user.max_otp_out - timezone.now()
                return Response(
                    f"Max OTP try reached, try after: {waiting_time.seconds // 60} minute.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = otp_set(user=user)

            # send email with otp
            send_reset_password_email(email, user.otp)

            return Response(
                "Reset password email sent",
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                "There is no account registered with this email.",
                status=status.HTTP_404_NOT_FOUND,
            )


class VerifyPasswordResetOTP(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(str(e))
            return Response(
                {"valid": False},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"valid": True},
            status=status.HTTP_200_OK,
        )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(str(e))
            return Response(
                {"success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": True, "message": "Password reset success"},
            status=status.HTTP_200_OK,
        )


class LocationList(generics.ListCreateAPIView):
    queryset = LocationModel.objects.all()
    serializer_class = LocationModelserializers


class CurrentUserTotalPointsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(
            {"total_points": request.user.total_points}, status=status.HTTP_200_OK
        )
