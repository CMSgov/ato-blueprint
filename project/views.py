from django.shortcuts import redirect, render
from .models import Package
from .forms import PackageForm

from utils import package_navigation

def project(request, project_id):
    project = Package.objects.get(id=project_id)

    return render(request, "project/project-home.html", {
        "project": project,
        "acronym": project.acronym,
        "project_title": project.title,
        "impact_level": project.impact_level,
        # "controls_status_count": project.system.controls_status_count,
        # "poam_status_count": project.system.poam_status_count,
        # "is_admin": request.user in project.get_admins(),
        # "columns": columns,
        # "elements": elements,
        # "total_controls_count": control_compliance_stats.get('total_controls_count'),
        # "controls_addressed_count": control_compliance_stats.get('controls_addressed_count'),
        # "percent_compliant": control_compliance_stats.get('percent_compliant'),
        "nav": package_navigation(project),
    })

# Example def that is not yet functional
def project_component_detail(request, project_id, component_id):
    project = Package.objects.get(id=project_id)

    return render(request, "project.html", {
        "project": project,
    })

def create_project(request):
    # If this is a POST request then process the form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request
        form = PackageForm(request.POST)

        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.creator_id = request.user.id
            new_project.save()

            return redirect('projects')

    # If this is a GET (or any other method) create the default form
    else:
        form = PackageForm()

    context = {
        "form": form,
    }

    return render(request, "project/project-create.html", context)
