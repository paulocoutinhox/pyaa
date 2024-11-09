import base64
import calendar
import io

import matplotlib
import matplotlib.pyplot as plt
import weasyprint
from django.conf import settings
from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from apps.customer import filters
from apps.customer.enums import CustomerGender
from apps.report.filters import ExportDataFilter
from apps.report.models import CustomerGenderSummary


@admin.register(CustomerGenderSummary)
class CustomerGendeSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/report/customer-gender-summary/view.html"
    show_full_result_count = False

    list_filter = [
        ("created_at", filters.CreatedAtFilter),
        ExportDataFilter,
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def changelist_view(self, request, extra_context=None):
        matplotlib.use("Agg")

        # call the original changelist_view to get the queryset
        response = super().changelist_view(request, extra_context=extra_context)
        qs = response.context_data["cl"].queryset

        # fonts
        font_path = settings.BASE_DIR / "apps/web/static/vendor/fonts"
        response.context_data["font_path"] = font_path

        # filter the queryset to show only the current month if no filters are applied
        if not request.GET:
            now = timezone.now()
            start_of_month = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            last_day = calendar.monthrange(now.year, now.month)[1]
            end_of_month = now.replace(
                day=last_day, hour=23, minute=59, second=59, microsecond=999999
            )
            qs = qs.filter(created_at__gte=start_of_month, created_at__lte=end_of_month)

        # metrics to summarize installments
        metrics = {
            "total": Count("id"),
        }

        # add summary data to context
        summary = list(qs.values("gender").annotate(**metrics).order_by("-total"))
        has_data = len(summary) > 0

        for item in summary:
            item["gender_display"] = CustomerGender(item["gender"]).label

        # generate the pie chart only if there is data
        if has_data:
            labels = [item["gender_display"] for item in summary]
            sizes = [item["total"] for item in summary]

            # color map for different item
            color_map = {
                CustomerGender.MALE: "#36ACD9",
                CustomerGender.FEMALE: "#BA3A7B",
                CustomerGender.NONE: "#000000",
            }

            colors = [color_map.get(item["gender"], "#000000") for item in summary]

            # create the pie chart
            plt.figure(figsize=(6, 6))

            plt.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=140,
                colors=colors,
            )

            plt.axis("equal")

            # save the chart as a base64 image
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=300)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            plt.close()

            response.context_data["chart_image"] = (
                f"data:image/png;base64,{image_base64}"
            )
        else:
            response.context_data["chart_image"] = None

        response.context_data["has_data"] = has_data
        response.context_data["summary"] = summary
        response.context_data["summary_total"] = dict(qs.aggregate(**metrics))

        # check if export to pdf is requested
        if request.GET.get("export-data") == "pdf":
            html_content = render_to_string(
                "admin/report/customer-gender-summary/pdf.html",
                response.context_data,
            )
            pdf = weasyprint.HTML(string=html_content).write_pdf()
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = (
                'inline; filename="customer-gender-summary.pdf"'
            )

            return response

        return response
