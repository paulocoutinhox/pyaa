import calendar

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
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

        # apply date filter if no filters are set (default to current month)
        if request.GET:
            # apply date range filter if set
            date_gte = request.GET.get("created_at__range__gte")
            date_lte = request.GET.get("created_at__range__lte")

            if date_gte or date_lte:
                date_filter = Q()

                if date_gte:
                    date_filter &= Q(accesses__created_at__gte=date_gte)

                if date_lte:
                    date_filter &= Q(accesses__created_at__lte=date_lte)

                qs = qs.filter(date_filter).distinct()
        else:
            # default to current month if no filters are set
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

            qs = qs.filter(
                accesses__created_at__gte=start_of_month,
                accesses__created_at__lte=end_of_month,
            ).distinct()

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
