import base64
import calendar
import io

import matplotlib.pyplot as plt
from django.contrib import admin
from django.db.models import Count
from django.utils import timezone

from apps.customer import filters
from apps.customer.enums import CustomerGender
from apps.report.admin.base_report import BaseReportAdmin
from apps.report.models import CustomerGenderSummary


@admin.register(CustomerGenderSummary)
class CustomerGendeSummaryAdmin(BaseReportAdmin):
    change_list_template = "admin/report/customer-gender-summary/view.html"
    pdf_template = "admin/report/customer-gender-summary/pdf.html"

    def has_chart(self):
        return True

    def has_pdf_export(self):
        return True

    def get_list_filter(self, request):
        return super().get_list_filter(request) + [
            ("created_at", filters.CreatedAtFilter),
        ]

    def generate_report_data(self, request):
        qs = self.get_queryset(request)

        if not request.GET:
            now = timezone.now()

            start_of_month = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            last_day = calendar.monthrange(now.year, now.month)[1]

            end_of_month = now.replace(
                day=last_day,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )

            qs = qs.filter(created_at__gte=start_of_month, created_at__lte=end_of_month)

        metrics = {"total": Count("id")}
        data = list(qs.values("gender").annotate(**metrics).order_by("-total"))

        for item in data:
            item["gender_display"] = CustomerGender(item["gender"]).label

        data_footer = dict(qs.aggregate(**metrics))

        return {"data": data, "data_footer": data_footer, "has_data": bool(data)}

    def generate_chart_data(self, report_data):
        data = report_data.get("data")
        if not data:
            return None

        labels = [item["gender_display"] for item in data]
        sizes = [item["total"] for item in data]
        color_map = {
            CustomerGender.MALE: "#36ACD9",
            CustomerGender.FEMALE: "#BA3A7B",
            CustomerGender.NONE: "#000000",
        }
        colors = [color_map.get(item["gender"], "#000000") for item in data]

        # generate chart as base64 string
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=colors)
        plt.axis("equal")

        buffer = io.BytesIO()
        plt.savefig(buffer, format=self.chart_format, dpi=self.chart_dpi)
        buffer.seek(0)
        chart_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()

        return f"data:image/png;base64,{chart_image}"
