import json
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

_manifest_cache = None


def get_manifest():
    global _manifest_cache

    if settings.DEBUG:
        _manifest_cache = None

    if _manifest_cache is not None:
        return _manifest_cache

    manifest_path = Path(settings.BASE_DIR) / "static/frontend/.vite/manifest.json"
    _manifest_cache = json.loads(manifest_path.read_text())
    return _manifest_cache


def _get_entry(manifest, entry):
    if entry in manifest:
        return manifest[entry]

    for data in manifest.values():
        if data.get("name") == entry:
            return data

    raise ValueError(f"Vite entry '{entry}' not found in manifest.json")


@register.simple_tag
def vite_js(entry):
    """
    Get the hashed JS asset path from Vite manifest.

    Usage:
        {% load pyaa_vite %}
        <script src="{% vite_js 'frontend' %}" defer></script>
    """
    manifest = get_manifest()
    entry_data = _get_entry(manifest, entry)
    return static(f"frontend/{entry_data['file']}")


@register.simple_tag
def vite_css(entry):
    """
    Get the hashed CSS asset path from Vite manifest.

    Usage:
        {% load pyaa_vite %}
        <link rel="stylesheet" href="{% vite_css 'frontend' %}">
    """
    manifest = get_manifest()
    entry_data = _get_entry(manifest, entry)
    css_files = entry_data.get("css", [])
    if not css_files:
        return ""
    return static(f"frontend/{css_files[0]}")


@register.simple_tag
def vite_all_css():
    """
    Get all CSS assets from all entries in Vite manifest.

    Usage:
        {% load pyaa_vite %}
        {% vite_all_css %}

    Returns:
        HTML link tags for all CSS files.
    """
    manifest = get_manifest()
    css_tags = []

    for entry_data in manifest.values():
        if entry_data.get("isEntry"):
            css_files = entry_data.get("css", [])
            for css_file in css_files:
                url = static(f"frontend/{css_file}")
                css_tags.append(f'<link rel="stylesheet" href="{url}">')

    return mark_safe("\n    ".join(css_tags))


@register.simple_tag
def vite_all_js():
    """
    Get all JS assets from all entries in Vite manifest.

    Usage:
        {% load pyaa_vite %}
        {% vite_all_js %}

    Returns:
        HTML script tags for all JS files.
    """
    manifest = get_manifest()
    js_tags = []

    for entry_data in manifest.values():
        if entry_data.get("isEntry"):
            js_file = entry_data.get("file")
            if js_file:
                url = static(f"frontend/{js_file}")
                js_tags.append(f'<script src="{url}" defer></script>')

    return mark_safe("\n    ".join(js_tags))
