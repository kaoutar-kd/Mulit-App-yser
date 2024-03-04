from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Image
from rest_framework import generics,status, permissions
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer, ImageSerializer
from rest_framework import status

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        user_data = request.data
        print(f"Received data: {user_data}")
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid():
            print("Serializer is valid.")
            serializer.save()
            user_data = serializer.data
            print(f"User data after saving: {user_data}")
            return Response(user_data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ImageDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = User.objects.get(id=request.user.id)
        try:
            image = Image.objects.get(id=id)
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        if user.role != 'Beta Player':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        user = User.objects.get(id=request.user.id)
        if user.role != 'Beta Player':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = Image.objects.get(id=id)
            serializer = ImageSerializer(image, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        user = User.objects.get(id=request.user.id)
        if user.role != 'Beta Player':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = Image.objects.get(id=id)
            operator = image.delete()
            if operator:
                return Response(data={'data': 'deleted successfully'})
            else:
                return Response(data={'data': 'delete failed'})
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
