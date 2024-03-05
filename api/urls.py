from django.urls import path
from api.views import (
    ImageListView,
    RegisterView,
    LoginAPIView,
    ImageDetailsView,
    RoleDetailsView,
    RoleListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('images/<int:id>/', ImageDetailsView.as_view(), name='image-details'),
    path('roles/<str:id>/', RoleDetailsView.as_view(), name='role-details'),
    path('images/', ImageListView.as_view(), name='image-list'),
    path('roles/', RoleListView.as_view(), name='role-list'),
]
