from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from guardian.shortcuts import get_objects_for_user

from access_management.permission_constants import (
    edit_project_permission,
    view_project_permission,
)
from utils import package_navigation

from .forms import PackageForm
from .models import Package


@method_decorator(login_required, name="dispatch")
class PackageList(ListView):
    model = Package
    template_name = "packages.html"
    context_object_name = "projects"
    ordering = ["created"]
    paginate_by = 9

    def get_queryset(self):
        # Get Project objects for which the given user has either edit or view permission
        projects_list = get_objects_for_user(
            self.request.user,
            [edit_project_permission[0], view_project_permission[0]],
            any_perm=True,
            klass=Package,
        )
        pprint("---project list")
        pprint(projects_list)

        return list(projects_list)

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
            "nav": package_navigation(project),
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
