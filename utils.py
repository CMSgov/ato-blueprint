def project_navigation(request, project):
  task = project.root_task.get_or_create_subtask(request.user, "ssp_intro")
  nav = {
      "controls": {
          "url": "/systems/" + str(project.system.id) + "/controls/selected",
          "title": "Review Controls",
          "id": "project-controls",
      },
      "components": {
          "url": "/systems/" + str(project.system.id) + "/components/selected",
          "title": "Manage Components",
          "id": "project-components",
      },
      "ssp": {
          "url": task.get_absolute_url(),
          "title": "Export System Security Plan",
          "id": "project-ssp"
      },
  }
  return nav
