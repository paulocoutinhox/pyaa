from django.template import Context, TemplateSyntaxError
from django.template.base import Origin, Template
from django.template.engine import Engine
from django.test import TestCase, override_settings


def render(template_string, context=None):
    engine = Engine.get_default()
    origin = Origin(name="test", template_name="test")
    template = Template(template_string, origin=origin, engine=engine)
    return template.render(Context(context or {}))


class SetVarTagTest(TestCase):
    def test_setvar_assigns_rendered_content(self):
        output = render(
            "{% load pyaa %}{% setvar greeting %}Hello{% endsetvar %}{{ greeting }}"
        )
        self.assertEqual(output.strip(), "Hello")

    def test_setvar_requires_single_argument(self):
        with self.assertRaises(TemplateSyntaxError):
            render("{% load pyaa %}{% setvar %}Hello{% endsetvar %}")


class ValueFromSettingsTagTest(TestCase):
    @override_settings(LANGUAGE_CODE="en-us")
    def test_value_from_settings_outputs_setting(self):
        output = render("{% load pyaa %}{% value_from_settings LANGUAGE_CODE %}")
        self.assertEqual(output, "en-us")

    def test_value_from_settings_requires_argument(self):
        with self.assertRaises(TemplateSyntaxError):
            render("{% load pyaa %}{% value_from_settings %}")


class SlotTagTest(TestCase):
    def test_slot_renders_default_content_when_slot_is_empty(self):
        output = render(
            "{% load pyaa %}{% slot body %}Content{% endslot %}",
            {"slots": {}},
        )
        self.assertEqual(output.strip(), "Content")

    def test_slot_renders_provided_slot_content(self):
        output = render(
            "{% load pyaa %}{% slot body %}Default{% endslot %}",
            {"slots": {"body": ["Injected"]}},
        )
        self.assertEqual(output.strip(), "Injected")


class ElementTagTest(TestCase):
    def test_element_renders_matching_template(self):
        output = render("{% load pyaa %}{% element hr %}{% endelement %}")
        self.assertIn('class="divider"', output)

    def test_element_passes_attrs_to_template(self):
        output = render(
            "{% load pyaa %}{% element button tags='outline-error' %}Save{% endelement %}"
        )
        self.assertIn("btn-outline", output)
        self.assertIn("btn-error", output)
        self.assertIn("Save", output)

    def test_element_rejects_multiple_positional_arguments(self):
        with self.assertRaises(TemplateSyntaxError):
            render("{% load pyaa %}{% element button extra %}{% endelement %}")
