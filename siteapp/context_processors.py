from django.conf import settings


def environment_name(request):
    return {'METRICS_ENV_NAME': settings.METRICS_ENV_NAME}
