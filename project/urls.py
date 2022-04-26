from django.urls import path

import project.views as views

urlpatterns = [
    path("", views.PackageList.as_view(), name="projects_list"),
    path("create", views.create_project, name="create_project"),
    path("<int:project_id>/", views.project, name="project_homepage"),
]
