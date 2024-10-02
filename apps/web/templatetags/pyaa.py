from django import template
from django.conf import settings
from django.template.base import FilterExpression, kwarg_re
from django.template.loader import render_to_string
from django.template.loader_tags import ExtendsNode
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

register = template.Library()


SLOTS_CONTEXT_KEY = "slots_context"
LAYOUT_CONTEXT_KEY = "layout_context"


# ------------------------------------------------------------------------------
class SlotNode(template.Node):
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        slots = context.render_context.get(SLOTS_CONTEXT_KEY)

        with context.push():
            if slots is None:
                if self.name in context["slots"]:
                    return "".join(context["slots"][self.name])
                return self.nodelist.render(context)
            else:
                result = self.nodelist.render(context)
                slot_list = slots.setdefault(self.name, [])
                slot_list.append(result)
                return ""


class ElementNode(template.Node):
    def __init__(self, nodelist, element, kwargs):
        self.element = element
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context):
        slots = {}
        extends_context = context.render_context.get(ExtendsNode.context_key)
        layout = None

        if extends_context:
            # extract layout from the {% extends %} tags
            for ec in extends_context:
                prefix = "pyaa/layouts/"

                if ec.template_name.startswith(prefix):
                    layout = ec.template_name[len(prefix) :].replace(".html", "")
                    break
        if not layout:
            # in case we're in a {% element %} element, the extends context is not there
            layout = context.render_context.get(LAYOUT_CONTEXT_KEY)
        if not layout:
            # or, similarly, for {% include %} we also lose the extends context.
            layout = context.get("page_layout")

        template_names = []

        if layout:
            template_names.append(f"pyaa/elements/{self.element}__{layout}.html")

        template_names.append(f"pyaa/elements/{self.element}.html")

        with context.render_context.push(
            **{
                SLOTS_CONTEXT_KEY: slots,
                LAYOUT_CONTEXT_KEY: layout,
            }
        ):
            slots["default"] = [self.nodelist.render(context)]
            attrs = {}

            for k, v in self.kwargs.items():
                attrs[k] = v.resolve(context)

            tags = attrs.get("tags")

            if tags:
                attrs["tags"] = tags.split(",")
            return render_to_string(
                template_names,
                {
                    "attrs": attrs,
                    "slots": slots,
                    "origin": self.origin.template_name.replace(".html", ""),
                },
            )


class SetVarNode(template.Node):
    def __init__(self, nodelist, var):
        self.nodelist = nodelist
        self.var = var

    def render(self, context):
        context[self.var] = mark_safe(self.nodelist.render(context).strip())
        return ""


class ValueFromSettings(template.Node):
    def __init__(self, var):
        self.arg = template.Variable(var)

    def render(self, context):
        return settings.__getattr__(str(self.arg))


# ------------------------------------------------------------------------------
def parse_tag(token, parser):
    bits = token.split_contents()
    tag_name = bits.pop(0)
    args = []
    kwargs = {}

    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return (tag_name, args, kwargs)


@register.simple_tag(takes_context=True)
def nav_active(context, url_name):
    try:
        pattern = reverse(url_name)
    except NoReverseMatch:
        pattern = url_name
    path = context["request"].path
    return "active" if path == pattern else ""


@register.tag(name="slot")
def do_slot(parser, token):
    nodelist = parser.parse(("endslot",))
    bits = token.split_contents()
    bits.pop(0)
    slot_name = bits.pop(0) if bits else "default"
    parser.delete_first_token()
    return SlotNode(slot_name, nodelist)


@register.tag(name="element")
def do_element(parser, token):
    nodelist = parser.parse(("endelement",))
    tag_name, args, kwargs = parse_tag(token, parser)
    usage = f'{{% {tag_name} "element" argument=value %}} ... {{% end{tag_name} %}}'

    if len(args) > 1:
        raise template.TemplateSyntaxError("Usage: %s" % usage)

    parser.delete_first_token()
    return ElementNode(nodelist, args[0], kwargs)


@register.tag(name="setvar")
def do_setvar(parser, token):
    nodelist = parser.parse(("endsetvar",))
    bits = token.split_contents()

    if len(bits) != 2:
        tag_name = bits[0]
        usage = f'{{% {tag_name} "setvar" var %}} ... {{% end{tag_name} %}}'
        raise template.TemplateSyntaxError("Usage: %s" % usage)

    parser.delete_first_token()
    return SetVarNode(nodelist, bits[1])


@register.tag(name="value_from_settings")
def value_from_settings(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0],
        )
    return ValueFromSettings(var)
