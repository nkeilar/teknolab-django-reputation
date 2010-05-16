from django.contrib import admin
import reputation.models as models

admin.site.register(models.Reputation)
admin.site.register(models.ReputationAction)
admin.site.register(models.UserReputationAction)
admin.site.register(models.Permission)
admin.site.register(models.ReputationContent)
