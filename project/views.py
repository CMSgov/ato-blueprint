from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView

from utils import package_navigation

from .forms import PackageForm
from .models import Package


@login_required
class PackageList(ListView):
    model = Package
    template_name = "packages.html"
    context_object_name = "projects"
    ordering = ["created"]
    paginate_by = 9

    def get_queryset(self):
        projects = Package.objects.all()
        return list(projects)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def project(request, project_id):
    project = Package.objects.get(id=project_id)

    return render(
        request,
        "project/project-home.html",
        {
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
        },
    )


# TODO Example def that is not yet functional
@login_required
def project_component_detail(request, project_id, component_id):
    project = Package.objects.get(id=project_id)

    return render(
        request,
        "project.html",
        {
            "project": project,
        },
    )


@login_required
def create_project(request):
    # If this is a POST request then process the form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request
        form = PackageForm(request.POST)

        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.creator_id = request.user.id
            new_project.save()

            return redirect("projects")

    # If this is a GET (or any other method) create the default form
    else:
        form = PackageForm()

    context = {
        "form": form,
    }

    return render(request, "project/project-create.html", context)
