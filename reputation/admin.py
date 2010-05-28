from django.contrib import admin
from reputation.models import Reputation, ReputationAction, UserReputationAction, ReputationContent

admin.site.register(Reputation)
admin.site.register(ReputationAction)
admin.site.register(UserReputationAction)
admin.site.register(ReputationContent)
