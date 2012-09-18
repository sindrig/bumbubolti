from django.conf.urls import patterns, include, url

urlpatterns = patterns('bolti.views',
    url(r'^$', 'main', name='main'),
    url(r'^autocomplete/$', 'autocomplete', name='autocomplete'),
    url(r'^register/(\d+)/$', 'register', name='register'),
    url(r'^newplayer/(\d+)/$', 'newplayer', name='newplayer'),
    url(r'^remove/(\d+)/$', 'remove', name='remove'),
    url(r'^register_scores/(\d+)/$', 'register_scores', name='register_scores'),
    url(r'^get_scoreboard_table/(\d+)?/?$', 'get_scoreboard_table', name='get_scoreboard_table'),
)
