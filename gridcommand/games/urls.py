from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from games import views

urlpatterns = [
    url(r'^games/$', views.GameList.as_view()),
    url(r'^games/(?P<pk>[0-9]+)/$', views.GameDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
