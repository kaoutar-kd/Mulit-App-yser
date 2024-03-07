from rest_framework.views import APIView
from rest_framework.response import Response
from api.utils import check_access, encode_token
from .models import Role, SubscriptionPlan, User, Image
from rest_framework import generics, status
from .serializers import RoleSerializer, SubscriptionPlanSerializer, UserSerializer, ImageSerializer
from rest_framework.exceptions import AuthenticationFailed


class RegisterView(generics.GenericAPIView):
    def post(self, request):
        """
        Handles user registration.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with user data.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(generics.GenericAPIView):
    def post(self, request):
        """
        Handles user login.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with JWT token.
        """
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
        """
        Retrieves a list of roles.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with role data.
        """
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Handles the creation of a new role.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with role data or error message.
        """
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleDetailsView(APIView):

    def get(self, request, id=str):
        """
        Retrieves details of a specific role.

        Args:
            request: The HTTP request.
            id: The ID of the role.

        Returns:
            Response: A Response object with role data or error message.
        """
        check_access(request.headers)
        try:
            role = Role.objects.get(role=id)
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id=str):
        """
        Updates details of a specific role.

        Args:
            request: The HTTP request.
            id: The ID of the role.

        Returns:
            Response: A Response object with updated role data or error message.
        """
        check_access(request.headers)
        try:
            role = Role.objects.get(role=id)
            serializer = RoleSerializer(role, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id=str):
        """
        Deletes a specific role.

        Args:
            request: The HTTP request.
            id: The ID of the role.

        Returns:
            Response: A Response object indicating success or failure.
        """
        check_access(request.headers)
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
        """
        Retrieves a list of images.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with image data.
        """
        check_access(request.headers)
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Handles the creation of a new image.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object indicating success or failure.
        """
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

    def get(self, request, id: int):
        """
        Retrieves details of a specific image.

        Args:
            request: The HTTP request.
            id: The ID of the image.

        Returns:
            Response: A Response object with image data or error message.
        """
        check_access(request.headers)
        try:
            image = Image.objects.get(id=id)
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id: int):
        """
        Updates details of a specific image.

        Args:
            request: The HTTP request.
            id: The ID of the image.

        Returns:
            Response: A Response object with updated image data or error message.
        """
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

    def delete(self, request, id: int):
        """
        Deletes a specific image.

        Args:
            request: The HTTP request.
            id: The ID of the image.

        Returns:
            Response: A Response object indicating success or failure.
        """
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

class SubscriptionPlanListView(APIView):
    def get(self, request):
        """
        Retrieves a list of subscription plans.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object with subscription plan data.
        """
        check_access(request.headers)
        subscription_plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(subscription_plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Handles the creation of a new subscription plan.

        Args:
            request: The HTTP request.

        Returns:
            Response: A Response object indicating success or failure.
        """
        check_access(request.headers)
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": "Subscription plan created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionPlanDetailsView(APIView):
    def get(self, request, subscription_plan: str):
        """
        Retrieves details of a specific subscription plan.

        Args:
            request: The HTTP request.
            subscription_plan: The subscription_plan of the subscription plan.

        Returns:
            Response: A Response object with subscription plan data or error message.
        """
        check_access(request.headers)
        try:
            subscription_plan = SubscriptionPlan.objects.get(subscription_plan=subscription_plan)
            serializer = SubscriptionPlanSerializer(subscription_plan)
            return Response(serializer.data)
        except SubscriptionPlan.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, subscription_plan: str):
        """
        Updates details of a specific subscription plan.

        Args:
            request: The HTTP request.
            subscription_plan: The subscription_plan of the subscription plan.

        Returns:
            Response: A Response object with updated subscription plan data or error message.
        """
        check_access(request.headers)
        try:
            subscription_plan = SubscriptionPlan.objects.get(subscription_plan=subscription_plan)
            serializer = SubscriptionPlanSerializer(subscription_plan, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            return Response("Subscription plan does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, subscription_plan: str):
        """
        Deletes a specific subscription plan.

        Args:
            request: The HTTP request.
            subscription_plan: The subscription_plan of the subscription plan.

        Returns:
            Response: A Response object indicating success or failure.
        """
        check_access(request.headers)
        try:
            subscription_plan = SubscriptionPlan.objects.get(subscription_plan=subscription_plan)
            operator = subscription_plan.delete()
            if operator:
                return Response(data={'data': 'deleted successfully'})
            else:
                return Response(data={'data': 'delete failed'})
        except SubscriptionPlan.DoesNotExist:
            return Response("Subscription plan does not exist", status=status.HTTP_404_NOT_FOUND)