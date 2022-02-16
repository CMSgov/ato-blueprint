from django.shortcuts import render

from .models import Package

from utils import project_navigation

def project(request, project_id):
    project = Package.objects.get(id=project_id)

    return render(request, "project.html", {
        "project": project,
        "security_sensitivity": project.impact_level,
        # "controls_status_count": project.system.controls_status_count,
        # "poam_status_count": project.system.poam_status_count,
        # "is_admin": request.user in project.get_admins(),
        # "title": project.title,
        # "columns": columns,
        # "elements": elements,
        # "total_controls_count": control_compliance_stats.get('total_controls_count'),
        # "controls_addressed_count": control_compliance_stats.get('controls_addressed_count'),
        # "percent_compliant": control_compliance_stats.get('percent_compliant'),
        # "nav": project_navigation(request, project),
    })

def project_component_detail(request, project_id, component_id):
    project = Package.objects.get(id=project_id)

    return render(request, "project.html", {
        "project": project,
    })
