from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from games import views

urlpatterns = [
    url(r'^games/$', views.GameList.as_view()),
    url(r'^games/(?P<pk>[0-9]+)/$', views.GameDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^auth/', include('rest_framework.urls',
                           namespace='rest_framework')),
]
