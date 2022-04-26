from django.contrib.auth.models import Group
from access_management.permission_constants import * # noqa: F403
from guardian.shortcuts import assign_perm

from pprint import pprint

PERMISSION_GROUP_SUFFIX = '_permission_group'
current_module_variables = vars()

# Create a list of groups and assign associated permissions to that group
# using the naming convention and permission mapping in the permission_constants file.
def generate_groups_and_permission(model_name, instance_name, instance):
    print("*----- generate_groups_and_permission function -----*")
    print("permission group suffix: " + PERMISSION_GROUP_SUFFIX)

    # package
    pprint("---model name")
    pprint(model_name)

    # id number for the package
    pprint("---instance name")
    pprint(instance_name)
        
    groups = current_module_variables[model_name+PERMISSION_GROUP_SUFFIX]
    pprint("---groups")
    pprint(groups)

    for k, v in groups.items():
        print("X -- inside for loop --")
        pprint("X ---k")
        pprint(k)
        pprint("X ---v")
        pprint(v)
        try:
            # append the object id to the partial name of the group
            # e.g. 10_project_admin_group
            group_name = instance_name + k
            print("X group name: " + group_name)

            # create a group based on the generated group name
            group = Group.objects.create(name=group_name)
            pprint("X ---group")
            pprint(group)

            # loop through the array of partial permissions 
            for permission in v:
                pprint("---permission")
                pprint(permission)

                # Add the permission to the associated group that was just created.
                # The instance indicates the object that this object level permission is for.
                assign_perm(permission[0], group, instance)

        except Exception as e:
            raise e
