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
