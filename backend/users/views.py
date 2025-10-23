from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import (PasswordResetConfirmSerializer,
                                  PasswordResetRequestSerializer,
                                  UserRegistrationSerializer, UserSerializer)

from api.utils import is_valid_email


from .services import VerificationService


@api_view(["POST"])
def send_confirmation_code_to_email(request):
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        email = email.strip().lower()

    if not is_valid_email(email):
        return Response(
            {"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token = VerificationService.send_verification_code(email)
        return Response({
            "message": "A confirmation code has been sent to your email",
            "user_verify_token": token,
            "user_verify_email": email
        })
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": "Something went wrong"}, status=500)
    

@api_view(["POST"])
def resend_confirmation_code_to_email(request):
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        email = email.strip().lower()

    if not is_valid_email(email):
        return Response(
            {"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        VerificationService.resend_verification_code(email)
        return Response(
            {"message": "A confirmatio34cn code has been sent to your email"}
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": "Something went wrong"}, status=500) 


@api_view(["POST"])
def verify_email(request):
    user_code = request.data.get("code")
    token = request.data.get("token")

    if not user_code:
        return Response(
            {"error": "User code required"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    if not token:
        return Response(
            {"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_email = VerificationService.verify_email(user_code, token)
        return Response({"message": "Email verification successful", "email": user_email})
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        print(e)
        return Response({"error": "Something went wrong"}, status=500)    


@api_view(["POST"])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User registration successful"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email:
        return Response({"error": "Please enter your email"}, status=400)

    if not password:
        return Response({"error": "Please enter your password"}, status=400)

    email = email.strip().lower()
    user = authenticate(email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
        )
