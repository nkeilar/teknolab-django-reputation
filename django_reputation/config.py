from django.conf import settings

MAX_REPUTATION_GAIN_PER_DAY = getattr(settings, 'MAX_REPUTATION_GAIN_PER_DAY', 250)
MAX_REPUTATION_LOSS_PER_DAY = getattr(settings, 'MAX_REPUATATION_LOSS_PER_DAY', -250)
BASE_REPUTATION = getattr(settings, 'BASE_REPUTATION', 5)
REPUTATION_REQUIRED_TEMPLATE = getattr(settings, 'REPUTATION_REQUIRED_TEMPLATE', 'django_reputation/reputation_required.html')