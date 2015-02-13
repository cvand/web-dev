from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'socialnetwork.views.home', name='home'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'socialnetwork/login.html'}),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register$', 'socialnetwork.views.register', name='register'),

    url(r'^profile/(?P<id>\d+)$', 'socialnetwork.views.profile', name='profile'),
    
    url(r'^add-post', 'socialnetwork.views.add_post', name='add'),
    url(r'^delete-post/(?P<post_id>\d+)/(?P<pageref>\w+)$', 'socialnetwork.views.delete_post', name='delete'),
)
