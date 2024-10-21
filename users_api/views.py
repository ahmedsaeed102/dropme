from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, generics, permissions, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from faker import Faker
import jwt
import string
import random
from datetime import date

from machine_api.models import PhoneNumber, RecycleLog
from .models import LocationModel, Feedback, UserModel, generate_referral_code
from competition_api.models import Competition
from marketplace.models import SpecialOffer
from .services import send_otp, send_reset_password_email, send_welcome_email, otp_set
from .serializers import LocationModelserializers, UserSerializer, UserProfileSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, OTPSerializer, OTPOnlySerializer, FeedbackSerializer, PreferredLanguageSerializer, TopUserSerializer
from marketplace.serializers import SpecialOfferSerializer
from competition_api.serializers import CompetitionSerializer
from machine_api.utlis import get_total_recycled_items

User = get_user_model()

"""
    SIGNUP APIS
"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().list(request, *args, **kwargs)
        return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(methods=["delete"], detail=False)
    def delete(self, request):
        User.objects.filter(id=request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["PATCH"], serializer_class=OTPOnlySerializer)
    def verify_otp(self, request, pk=None):
        """to check if the user entered the correct otp or if he/she is already verified (is_active=True)"""
        instance = self.get_object()
        if not instance.is_active and instance.otp_expiration and instance.otp == request.data.get("otp") and timezone.now() < instance.otp_expiration:
            instance.is_active = True
            instance.otp_expiration = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.max_otp_out = None
            send_welcome_email(instance.email)
            # check if user phone number was used to recycle before and add the points to user account
            phone = PhoneNumber.objects.filter(phone_number=instance.phone_number).first()
            if phone:
                instance.total_points += phone.points
                RecycleLog.objects.filter(phone=phone).update(user=instance)
                phone.delete()
            instance.save()
            return Response("Successfully verfied the user.", status=status.HTTP_200_OK)
        return Response(_("User already verfied or OTP is incorrect."), status=status.HTTP_400_BAD_REQUEST,)

    @action(detail=True, methods=["GET"])
    def regenerate_otp(self, request, pk=None):
        """to regenerate otp until max try"""
        instance = self.get_object()
        if instance.max_otp_out and timezone.now() < instance.max_otp_out:
            waiting_time = instance.max_otp_out - timezone.now()
            return Response(f"Max OTP try reached, try after: {waiting_time.seconds // 60} minute.", status=status.HTTP_400_BAD_REQUEST)
        instance = otp_set(user=instance)
        send_otp(instance)
        return Response("Successfully regenrated the new OTP.", status=status.HTTP_200_OK)

"""
    FORGOT PASSWORD APIS
"""
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data.get("email", "")
        user = User.objects.filter(email=email).first()
        if user:
            if user.max_otp_out and timezone.now() < user.max_otp_out:
                waiting_time = user.max_otp_out - timezone.now()
                return Response(f"Max OTP try reached, try after: {waiting_time.seconds // 60} minute.", status=status.HTTP_400_BAD_REQUEST)
            user = otp_set(user=user)
            send_reset_password_email(email, user.otp)
            return Response("Reset password email sent",status=status.HTTP_200_OK,)
        else:
            raise exceptions.NotFound({"detail": _("There is no account registered with this email.")},)

class VerifyPasswordResetOTP(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"valid": True},status=status.HTTP_200_OK,)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"success": True, "message": "Password reset success"}, status=status.HTTP_200_OK)

"""
    PROFILE UPDATE APIS
"""
class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    lookup_field = "pk"
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["head", "get", "put"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user.id != instance.id:
            raise exceptions.PermissionDenied()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "user profile updated successfully"})

    def get(self, request, pk):
        if request.user.id != pk:
            raise exceptions.PermissionDenied()
        return super().get(request, pk)

class PreferredLanguageView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PreferredLanguageSerializer

    def get(self, request):
        return Response({"preferred_language": request.user.preferred_language}, status=status.HTTP_200_OK)

    def patch(self, request):
        request.user.preferred_language = request.data.get("preferred_language")
        request.user.save()
        return Response({"message": "Preferred language updated successfully"}, status=status.HTTP_200_OK)

class ReferralCodeView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        if not request.user.referral_code:
            request.user.referral_code = generate_referral_code(request.user)
            request.user.save()
        return Response({"referral_code": request.user.referral_code, "referral_usage_count": request.user.referral_usage_count}, status=status.HTTP_200_OK)

class LocationList(generics.ListCreateAPIView):
    queryset = LocationModel.objects.all()
    serializer_class = LocationModelserializers
    permission_classes = (permissions.IsAuthenticated,)

class CurrentUserDetailsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id, 
            "username": user.username,
            "email": user.email, 
            "phone_number": user.phone_number,
            "profile_photo": user.profile_photo.url,
            "age": user.age,
            "gender": user.gender,
            "address": user.address.address if user.address else None,
            "referral_code": user.referral_code,
            "referral_usage_count": user.referral_usage_count,
            "preferred_language": user.preferred_language,
            "total_points": user.total_points, 
            "total_recycled_items": get_total_recycled_items(user.id), 
        }, status=status.HTTP_200_OK)

class FeedbacksList(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (permissions.IsAdminUser,)

class FeedbackCreate(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (permissions.IsAuthenticated,)

class AnonymousUser(generics.GenericAPIView):
    def get(self, *args, **kwargs):
        fake = Faker()
        user = User.objects.create(username=fake.name(), email=f"{fake.word()}@anonymous.com", is_active=True)
        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

class HomePageView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_points = user.total_points
        top_users = UserModel.objects.order_by("-total_points")[:3]
        top_users_Serializer = TopUserSerializer(top_users, many=True).data
        special_offers = SpecialOffer.objects.filter(end_date__gte=date.today(), is_finished=False).order_by('-created_at')[:3]
        special_offers_Serializer = SpecialOfferSerializer(special_offers, many=True, context={'request':request}).data
        competition = Competition.objects.filter(end_date__gte=date.today()).order_by('-created_at')[:1]
        competition_Serializer = CompetitionSerializer(competition, many=True, context={'request':request}).data
        return Response(
            {
                "user_points": user_points,
                "recycled_items": get_total_recycled_items(user.id),
                "top_users": top_users_Serializer,
                "special_offers": special_offers_Serializer,
                "competition": competition_Serializer,
            }
        )

from .serializers import UserPointsSerializer
class UsersPointsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        users = UserModel.objects.all()
        users_serializer = UserPointsSerializer(users, many=True)
        return Response(users_serializer.data, status=status.HTTP_200_OK)


class GoogleAuth(generics.GenericAPIView):

    def post(self, request):
        token= request.data['token']
        payload = jwt.decode(jwt=token,options={"verify_signature": False}, audience="851033294233-3n144jdfadc2adqheoqbukpo3hehppt4.apps.googleusercontent.com", algorithms=["ES256"])
        print(payload)
        email=payload['email']

        if(UserModel.objects.filter(email=email).exists()):
            user=UserModel.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'id': user.id,
            }, status=status.HTTP_200_OK)
        else:
            user=UserModel.objects.create(email=email, username=payload['name'])
            user.set_password(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))
            return Response({
            "id": user.id,
            "username": user.username,
            "phone_number": user.phone_number,
            "email": user.email,
            },status=status.HTTP_200_OK)
