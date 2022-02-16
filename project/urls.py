from django.urls import path
import project.views as views

urlpatterns = [
    path('<project_id>/', views.project, name='project_homepage'),
    path('<project_id>/components/', views.project, name='project_components'),
    path('<project_id>/component/<component_id>/', views.project_component_detail, name='project_component_detail'),
    path('<project_id>/components/component_id/statement/<statement_id>/', views.project, name='project_component_detail_by_control'),
    path('<project_id>/controls/', views.project, name='project_controls'),
    path('<project_id>/control/<control_id>/', views.project, name='project_control_detail'),
    path('<project_id>/control/<control_id>/component/<component_id>/', views.project, name='project_control_detail_by_component'),
    path('<project_id>/download/', views.project, name='project_export'),
    path('<project_id>/settings/', views.project, name='project_settings'),
    path('<project_id>/settings/edit/', views.project, name='project_settings_edit'),
]
