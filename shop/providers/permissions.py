from django.core.exceptions import PermissionDenied

def provider_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not hasattr(request.user, 'provider_profile'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
