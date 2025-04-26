from django.contrib import admin
from django.db.models import Count, Q
from django.utils.translation import gettext as _

from apps.banner.enums import BannerAccessType
from apps.banner.models import Banner
from apps.customer import filters
from apps.report.admin.base_report import BaseReportAdmin
from apps.report.models import BannerAccessSummary


@admin.register(BannerAccessSummary)
class BannerAccessSummaryAdmin(BaseReportAdmin):
    change_list_template = "admin/report/banner-access-summary/view.html"
    pdf_template = "admin/report/banner-access-summary/pdf.html"

    def get_report_title(self):
        return _("title.report.banner-access-summary")

    def has_chart(self):
        return False

    def get_list_filter(self, request):
        return super().get_list_filter(request) + [
            "active",
            ("created_at", filters.CreatedAtFilter),
        ]

    def get_queryset(self, request):
        return Banner.objects.all()

    def generate_report_data(self, request):
        qs = self.get_queryset(request)

        # get date range and apply filter
        date_gte, date_lte = self.get_date_range("created_at", request)
        qs = self.apply_date_filter(qs, "accesses__created_at", date_gte, date_lte)

        # apply active filter if set
        active_filter = request.GET.get("active__exact")
        if active_filter is not None:
            qs = qs.filter(active=active_filter)

        # group by banner and include site and language as banner info
        data = list(
            qs.values("id", "title", "active", "site__name", "language__name")
            .annotate(
                total_views=Count(
                    "accesses",
                    filter=Q(accesses__access_type=BannerAccessType.VIEW),
                    distinct=True,
                ),
                total_clicks=Count(
                    "accesses",
                    filter=Q(accesses__access_type=BannerAccessType.CLICK),
                    distinct=True,
                ),
            )
            .order_by("title")
        )

        # format the data
        for item in data:
            item["site"] = item.pop("site__name") or "-"
            item["language"] = item.pop("language__name") or "-"
            item["total_views"] = item["total_views"] or 0
            item["total_clicks"] = item["total_clicks"] or 0

        data_footer = {
            "total_views": sum(item["total_views"] for item in data),
            "total_clicks": sum(item["total_clicks"] for item in data),
        }

        return {
            "data": data,
            "data_footer": data_footer,
            "has_data": bool(data),
        }
