from rest_framework import permissions

from car.models import Car


class IsCarOwner(permissions.BasePermission):
    """Check user is owner of car or cars"""

    def has_permission(self, request, view):
        is_owner = True
        cars = view.get_queryset()
        if view.kwargs.get('car_id'):
            cars = Car.objects.filter(pk=view.kwargs.get('car_id'))

        for car in cars:
            if car.user != request.user:
                is_owner = False
        return is_owner
