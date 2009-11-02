from django.conf.urls.defaults import *

urlpatterns = patterns('django_reputation.views',
    url(r'^reputation_required/(?P<reputation_action>.+)/$',  'reputation_required',  name='reputation-required'), 
)
