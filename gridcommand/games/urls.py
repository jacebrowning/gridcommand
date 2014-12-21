from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from games import views

# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^$', views.api_root),
    url(r'^games/$',
        views.GameList.as_view(),
        name='game-list'),
    url(r'^games/(?P<pk>[0-9]+)/$',
        views.GameDetail.as_view(),
        name='game-detail'),
    url(r'^users/$',
        views.UserList.as_view(),
        name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$',
        views.UserDetail.as_view(),
        name='user-detail'),
])

# Login and logout views for the browsable API
urlpatterns += [
    url(r'^auth/', include('rest_framework.urls',
                           namespace='rest_framework')),
]
