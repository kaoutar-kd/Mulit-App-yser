from django.urls import path
from api.views import RegisterView, LoginAPIView, ImageDetailsView, RoleDetailsView, RoleListView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/',LoginAPIView.as_view(),name="login"),
    path('images/<int:id>/', ImageDetailsView.as_view(), name='image-details'),
    path('roles/<str:id>/', RoleDetailsView.as_view(), name='role-details'),
    path('images/', ImageDetailsView.as_view(), name='image-details'),
    path('roles/', RoleListView.as_view(), name='role-details'),
]
