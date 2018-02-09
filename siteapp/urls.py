from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

import siteapp.views as views
from .good_settings_helpers import signup_wrapper

urlpatterns = [
    url(r"^$", views.homepage, name="homepage"),

    # apps
    url(r"^tasks/", include("guidedmodules.urls")),
    url(r"^discussion/", include("discussion.urls")),

    # app store
    url(r'^store$', views.apps_catalog),
    url(r'^store/(?P<app_namespace>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

    # projects
    url(r"^projects$", views.project_list),
    url(r'^projects/(\d+)/__rename$', views.rename_project, name="rename_project"),
    url(r'^projects/(\d+)/__delete$', views.delete_project, name="delete_project"),
    url(r'^projects/(\d+)/__export$', views.export_project, name="export_project"),
    url(r'^projects/(\d+)/__import$', views.import_project_data, name="import_project_data"),
    url(r'^projects/(\d+)/(?:[\w\-]+)()$', views.project), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/startapps)$', views.project_start_apps), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/list)$', views.project_list_all_answers), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/outputs)$', views.project_outputs), # must be last because regex matches some previous URLs
    url(r'^projects/(\d+)/(?:[\w\-]+)(/api)$', views.project_api), # must be last because regex matches some previous URLs
    url(r'^projects/folders/(\d+)/(?:[\w\-]+)$', views.folder_view),
    url(r'^__rename_folder$', views.rename_folder, name="rename_folder"),
    url(r'^__set_folder_description$', views.set_folder_description, name="set_folder_description"),
    url(r'^__new_folder$', views.new_folder, name="new_folder"),
    url(r'^__delete_folder$', views.delete_folder, name="delete_folder"),

    # api
    url(r'^api-keys$', views.show_api_keys, name="show_api_keys"),

    # invitations
    url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
    url(r'^invitation/_cancel$', views.cancel_invitation, name="cancel_invitation"),
    url(r'^invitation/accept/(?P<code>.+)$', views.accept_invitation, name="accept_invitation"),

    # auth
    # next line overrides signup with our own view so we can monitor signup attempts, can comment out to go back to allauth's functionality
    url(r'^accounts/signup/', signup_wrapper, name="account_signup"),
    url(r'^accounts/', include('allauth.urls')),
]

import notifications.urls
urlpatterns += [
    url('^user/notifications/', include(notifications.urls, namespace='notifications')),
    url('^_mark_notifications_as_read', views.mark_notifications_as_read),
]

if settings.DEBUG: # also in urls_landing
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug_toolbar__/', include(debug_toolbar.urls)),
    ]

if settings.SINGLE_ORGANIZATION_KEY:
    # If we're operating in single-organization mode, then non-org URLs must be made available
    # here because the landing domain is not used.
    from .urls_landing import urlpatterns as urls_landing_urlpatterns
    urlpatterns += urls_landing_urlpatterns
