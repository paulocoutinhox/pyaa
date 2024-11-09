import matplotlib
import weasyprint
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.report.filters import ExportDataFilter


class BaseReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/report/base-report/view.html"
    show_full_result_count = False

    # default chart settings
    chart_format = "png"
    chart_dpi = 300

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_chart(self):
        """method to indicate if the report should include a chart"""
        return False

    def has_pdf_export(self):
        """method to indicate if the report supports PDF export"""
        return False

    def init_chart_lib(self):
        """method to initialize the chart library"""
        matplotlib.use("Agg")

    def get_list_filter(self, request):
        """method to get the list of filters for the report"""
        return [ExportDataFilter]

    def add_general_context(self, request):
        """method to add general context data"""

        return {
            "font_path": settings.BASE_DIR / "apps/web/static/vendor/fonts",
        }

    def export_to_pdf(self, context, template_name):
        """method to export report to PDF"""
        css_path = settings.BASE_DIR / "apps/web/static/admin/css/report-pdf.css"

        html_content = render_to_string(
            template_name,
            context,
        )

        pdf = weasyprint.HTML(string=html_content).write_pdf(
            stylesheets=[
                weasyprint.CSS(str(css_path)),
            ],
        )

        response = HttpResponse(
            pdf,
            content_type="application/pdf",
        )

        response["Content-Disposition"] = (
            f'inline; filename="{self.__class__.__name__.lower()}-report.pdf"'
        )

        return response

    def changelist_view(self, request, extra_context=None):
        self.init_chart_lib()
        response = super().changelist_view(request, extra_context=extra_context)

        # add general context data
        context_data = self.add_general_context(request)
        response.context_data.update(context_data)

        # generate report and chart data from the subclass
        report_data = self.generate_report_data(request)
        chart_data = self.generate_chart_data(report_data)

        response.context_data.update(report_data)
        response.context_data["chart_image"] = chart_data
        response.context_data["has_chart"] = chart_data is not None

        if self.has_pdf_export() and request.GET.get("export-data") == "pdf":
            return self.export_to_pdf(response.context_data, self.pdf_template)

        return response

    def generate_report_data(self, request):
        """method to be overridden in subclasses to provide report data"""
        return {}

    def generate_chart_data(self, report_data):
        """method to be overridden in subclasses to generate chart from report data"""
        return None
