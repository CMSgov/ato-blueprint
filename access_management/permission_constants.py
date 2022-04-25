# # Project permissions name and code
manage_project_users_permission = ('project_can_manage_users', 'Can manage users on project')
edit_project_permission = ('project_can_edit', 'Can edit project')
view_project_permission = ('project_can_view', 'Can view project')

# # Project permission list associated with groups
project_admin_permissions = [manage_project_users_permission, edit_project_permission, view_project_permission]
project_contributor_permissions = [edit_project_permission, view_project_permission]
project_view_only_permissions = [view_project_permission]

# Group names
PROJECT_ADMIN_GROUP = '_project_admin_group'
PROJECT_CONTRIBUTOR_GROUP = '_project_contributor_group'
PROJECT_VIEW_ONLY_GROUP = '_project_view_only_group'

# TODO rename to project_permission_group when model name switches from package to project
# Group and permission list mappings
package_permission_group = {PROJECT_ADMIN_GROUP: project_admin_permissions,
                            PROJECT_CONTRIBUTOR_GROUP: project_contributor_permissions,
                            PROJECT_VIEW_ONLY_GROUP: project_view_only_permissions}
