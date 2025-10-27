from django import template

register = template.Library()


@register.filter(name="force_https")
def force_https(url):
    if url and isinstance(url, str):
        if url.startswith("http://"):
            return url.replace("http://", "https://", 1)

    return url
