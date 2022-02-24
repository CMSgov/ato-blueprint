from django.conf.urls import url
from django.contrib import admin

from . import views_api

admin.autodiscover()

urlpatterns = [
    url(
        r"^(?P<system_id>.*)/assessment/new$",
        views_api.manage_system_assessment_result_api,
        name="new_system_assessment_result_api",
    ),
]
