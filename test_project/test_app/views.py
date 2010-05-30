from django.contrib.auth.decorators import permission_required
from test_app.models import Link

@permission_required('test_app.can_vote_up')
def vote_up(request):
    user, c = User.objects.get_or_create(username='test_user')
    link, c = Link.objects.get_or_create(link='test.com', user=user, vote=1)
