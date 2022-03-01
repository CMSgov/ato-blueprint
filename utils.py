# TODO this is part of the old project related code and will be replaced by the "package_navigation" function below.
# This function can be removed when no longer in use.
def project_navigation(request, project):
  task = project.root_task.get_or_create_subtask(request.user, 'ssp_intro')
  project_url = project.get_absolute_url()
  nav = {
      'controls': {
          'url': f'/systems/{project.system.id}/controls/selected',
          'title': 'Review Controls',
          'id': 'project-controls',
      },
      'components': {
          'url': f'/systems/{project.system.id}/components/selected',
          'title': 'Manage Components',
          'id': 'project-components',
      },
      'ssp': {
          'url': f'{project_url}/downloads',
          'title': 'Export System Security Plan',
          'id': 'project-ssp',
      },
  }
  return nav

# TODO rename package_navigation to project_navigation once old project related code is removed
def package_navigation(project):
  project_url = project.get_absolute_url()
  nav = {
      'controls': {
          'url': f'{project_url}/controls',
          'title': 'Review Controls',
          'id': 'project-controls',
      },
      'components': {
          'url': f'{project_url}/components',
          'title': 'Manage Components',
          'id': 'project-components',
      },
      'ssp': {
          'url': f'{project_url}/download',
          'title': 'Export System Security Plan',
          'id': 'project-ssp',
      },
  }
  return nav
