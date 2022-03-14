from django.contrib import admin

from .models import Package


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'acronym', 'impact_level', 'location', 'catalog', 'creator')
    search_fields = ('id', 'title', 'acronym')
    actions = ["export_as_csv"]

# TODO "PackageRename" update to replace Package with Project once the old Project class in /siteapp/models has been removed
admin.site.register(Package, ProjectAdmin)
