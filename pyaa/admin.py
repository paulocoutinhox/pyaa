from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

from pyaa.forms import AdminAuthenticationFormWithCaptcha


class AppAdmin(AdminSite):
    site_header = _("admin.name")

    def get_app_list(self, request, app_label=None):
        """
        Returns a list of applications, allowing for duplicates within custom groups but
        removing them from the general list if they're not grouped, and optionally filters by app_label.
        """
        app_dict = self._build_app_dict(request)

        if app_label is not None:
            # filter the app_dict to only include the specified app_label if it's provided
            app_dict = {
                key: value
                for key, value in app_dict.items()
                if value["app_label"] == app_label
            }

        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        # define a list of groups with their names and the apps they contain
        groups = [
            {
                "name": _("admin.group.site-content"),
                "app_labels": [
                    "customer",
                    "language",
                    "content",
                    "gallery",
                ],
                "group_label": "site-content",
            },
            # you can add more groups here as needed
            # {
            #     "name": _("admin.group.xyz"),
            #     "app_labels": ["app1", "app2"],
            #     "group_label": "group_xyz",
            # },
        ]

        # collect all app_labels from groups to know which ones to exclude later
        grouped_app_labels = [app for group in groups for app in group["app_labels"]]

        # variable to store the final app list after filtering and grouping
        filtered_app_list = []

        for group in groups:
            group_models = []

            # collect models for the current group
            for app in app_list:
                if app["app_label"].lower() in group["app_labels"]:
                    group_models.extend(app["models"])

            # only add the group if it matches the filtered app_label or if no app_label is specified
            if not app_label or group["group_label"] == app_label:
                filtered_app_list.insert(
                    0,
                    {
                        "name": group["name"],
                        "app_label": group["group_label"],
                        "models": group_models,
                    },
                )

        # filter out apps that have been grouped if no specific app_label is provided for filtering
        if app_label is None:
            app_list = [
                app
                for app in app_list
                if app["app_label"].lower() not in grouped_app_labels
            ]
        else:
            # if a specific app_label is provided, include only apps with that label
            app_list = [
                app for app in app_list if app["app_label"].lower() == app_label.lower()
            ]

        # combine the filtered app list with the rest of the apps
        final_app_list = filtered_app_list + app_list

        return final_app_list


site = AppAdmin()
admin.AdminSite.login_form = AdminAuthenticationFormWithCaptcha
