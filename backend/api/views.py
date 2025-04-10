from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *


class RegisterView(APIView):

    def post(self, request):
        serializer = AccountRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

    def post(self, request):
        serializer = AccountLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        return Response(serializer.errors,
                        status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.data['old_password']):
                return Response({
                    "error": "Wrong password"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data['new_password'])
            user.save()

            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        serializer = UpdateUserSerializer(user,
                                          data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UpdateUserSerializer(request.user)

        return Response(serializer.data)
