from django.http import Http404


def product_admin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == "ProductAdmin":
            return view_func(request, *args, **kwargs)
        else:
            raise Http404("Page not found")
    return wrapper_func