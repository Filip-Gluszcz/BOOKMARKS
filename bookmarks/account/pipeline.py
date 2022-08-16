from .models import Profile

def save_profile(backend, user, response, *args, **kwargs):
    try:
        user.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=user)