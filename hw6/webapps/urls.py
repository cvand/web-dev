from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/$', include(admin.site.urls)),
    url(r'^socialnetwork/', include('socialnetwork.urls')),
    url(r'^$', RedirectView.as_view(url='/socialnetwork', permanent=False), name='index'),
)
