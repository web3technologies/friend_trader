from rest_framework.throttling import UserRateThrottle


class ThrottleMixin:
    throttle_classes = [UserRateThrottle]