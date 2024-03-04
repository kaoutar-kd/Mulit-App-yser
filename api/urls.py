from django.urls import path
from api.views import RegisterView, LoginAPIView, LogoutAPIView, ImageDetailsView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('image-details/<int:id>/', ImageDetailsView.as_view(), name='image-details'),
]
