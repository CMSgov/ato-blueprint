from guidedmodules.models import (Task)

def get_project_acronym(project):
    acronym = None
    task = Task.objects.filter(project=project.id)
    for i in task:
        if i.module.module_name == 'system_basic_info':
            s = i.get_answers().with_extended_info()
            acronym = s.as_dict().get('system_acronym')
    return acronym
