from django.urls import path
from api.views import RegisterView, LoginAPIView, ImageDetailsView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('image-details/<int:id>/', ImageDetailsView.as_view(), name='image-details'),
]
