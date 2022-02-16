from django.conf import settings


def environment_name(request):
    return {'ENV_NAME': settings.APP_ENV_NAME}
