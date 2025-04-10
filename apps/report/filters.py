from django.contrib.admin import SimpleListFilter


class ExportDataFilter(SimpleListFilter):
    title = ""
    parameter_name = "export-data"
    template = "admin/filter/hidden_filter.html"

    def lookups(self, request, model_admin):
        return ((request.GET.get(self.parameter_name), ""),)

    def queryset(self, request, queryset):
        return queryset
