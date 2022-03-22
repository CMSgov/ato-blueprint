from django.urls import path

import project.views as views

urlpatterns = [
    path("create", views.create_project, name="create_project"),
    path("<int:project_id>/", views.project, name="project_homepage"),
    path("<int:project_id>/components/", views.project, name="project_components"),
    path(
        "<int:project_id>/components/<int:component_id>/",
        views.project_component_detail,
        name="project_component_detail",
    ),
    path(
        "<int:project_id>/components/<int:component_id>/statements/<int:statement_id>/",
        views.project,
        name="project_component_detail_by_control",
    ),
    path("<int:project_id>/controls/", views.project, name="project_controls"),
    path(
        "<int:project_id>/controls/<int:control_id>/",
        views.project,
        name="project_control_detail",
    ),
    path(
        "<int:project_id>/controls/<int:control_id>/components/<int:component_id>/",
        views.project,
        name="project_control_detail_by_component",
    ),
    path("<int:project_id>/download/", views.project, name="project_export"),
    path("<int:project_id>/settings/", views.project, name="project_settings"),
    path(
        "<int:project_id>/settings/edit/", views.project, name="project_settings_edit"
    ),
]
