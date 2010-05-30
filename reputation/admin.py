from django.contrib import admin
from reputation.models import Reputation, ReputationAction, UserReputationAction

admin.site.register(Reputation)
admin.site.register(ReputationAction)
admin.site.register(UserReputationAction)
