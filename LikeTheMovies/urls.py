from django.conf.urls import patterns, include, url

from django.contrib import admin

from LikeTheMovies import settings

from .views import login_user, index

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', login_user),
    url(r'^index/$', index),

    url(r'^admin/', include(admin.site.urls)),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
    (r'^static/media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
