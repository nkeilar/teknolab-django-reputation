from django.conf.urls.defaults import *

urlpatterns = patterns('reputation.views',
    url(r'^reputation_required/(?P<permission_name>.+)/$',  'reputation_required',  name='reputation-required'), 
)
