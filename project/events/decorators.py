from functools import wraps
from django.http import HttpResponseForbidden

def donor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_association:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied. Associations cannot perform this action.")
    return _wrapped_view
