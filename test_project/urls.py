from django.conf.urls.defaults import *
from django.contrib import admin
from reputation.registry import reputation_registry
from test_app.models import VotingReputationHandler

admin.autodiscover()

reputation_registry.register(VotingReputationHandler)
print reputation_registry._handlers

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
