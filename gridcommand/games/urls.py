from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from games import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
]
