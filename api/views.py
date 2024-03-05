from rest_framework.views import APIView
from rest_framework.response import Response

from api.utils import check_access, decode_token, encode_token, get_token
from .models import Role, User, Image
from rest_framework import generics,status
from .serializers import RoleSerializer, UserSerializer, ImageSerializer
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
import jwt, datetime

class RegisterView(generics.GenericAPIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginAPIView(generics.GenericAPIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        token = encode_token(user)

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return Response(response.data, status=status.HTTP_200_OK)
    
class RoleListView(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleDetailsView(APIView):

    def get(self, request, id = None):
        try:
            role = Role.objects.get(role=id)
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id=None):
        try:
            role = Role.objects.get(role=id)
            serializer = RoleSerializer(role, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id=None):
        try:
            role = Role.objects.get(role=id)
            operator = role.delete()
            if operator:
                return Response(data={'data': 'deleted successfully'})
            else:
                return Response(data={'data': 'delete failed'})
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ImageListView(APIView):
    def get(self, request):
        check_access(request.headers)
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = check_access(request.headers)
        user = User.objects.get(username=username)
        if user.role.role != 'beta_player':
            return Response("User not allowed to add the image", status=status.HTTP_401_UNAUTHORIZED)

        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Image uploaded successfully", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageDetailsView(APIView):

    def get(self, request, id):
        check_access(request.headers)
        try:
            image = Image.objects.get(id=id)
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        username = check_access(request.headers)
        user = User.objects.get(username=username)
        if user.role.role != 'beta_player':
            return Response("User not allowed to update the image", status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = Image.objects.get(id=id)
            serializer = ImageSerializer(image, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Image.DoesNotExist:
            return Response("Image does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        username = check_access(request.headers)
        user = User.objects.get(username=username)
        if user.role.role != 'beta_player':
            return Response("User not allowed to delete the image", status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = Image.objects.get(id=id)
            operator = image.delete()
            if operator:
                return Response(data={'data': 'deleted successfully'})
            else:
                return Response(data={'data': 'delete failed'})
        except Image.DoesNotExist:
            return Response("Image does not exist", status=status.HTTP_404_NOT_FOUND)
