from functools import wraps

from django.shortcuts import render

def require_object(model, custom_response=None):
    """Decorator to only call the view if an object with the given id exists
    and automatically pass it instead of the id."""

    def decorator(function):
        @wraps(function)
        def wrap(request, object_id, *args, **kwargs):
            if model.objects.filter(pk=object_id).exists():
                obj = model.objects.get(pk=object_id)
                return function(request, obj, *args, **kwargs)

            if custom_response:
                return custom_response

            return render(request, 'mlmtree/error.html', status=404)
        return wrap
    return decorator


def require_objects(config, custom_response=None):
    """Decorator to only call the view if objects with given ids exist
    and automatically pass them instead of the ids.

    Format: [("fieldname_in", Model, "fieldname_out")]"""

    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            for field_in, model, field_out in config:
                objpk = kwargs.pop(field_in)

                if model.objects.filter(pk=objpk).exists():
                    kwargs[field_out] = model.objects.get(pk=objpk)
                    continue

                if custom_response:
                    return custom_response

                return render(request, 'mlmtree/error.html', status=404)

            return function(request, *args, **kwargs)
        return wrap
    return decorator
