from django.template import Context
from django.template.base import Origin, Template
from django.template.engine import Engine
from django.test import RequestFactory, TestCase


def render(template_string, context=None):
    engine = Engine.get_default()
    origin = Origin(name="test", template_name="test")
    template = Template(template_string, origin=origin, engine=engine)
    return template.render(Context(context or {}))


class NavActiveTagTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_active_when_path_matches(self):
        request = self.factory.get("/")
        output = render(
            "{% load pyaa %}{% nav_active 'home' %}",
            {"request": request},
        )
        self.assertEqual(output, "active")

    def test_returns_empty_when_path_differs(self):
        request = self.factory.get("/contact/")
        output = render(
            "{% load pyaa %}{% nav_active 'home' %}",
            {"request": request},
        )
        self.assertEqual(output, "")

    def test_falls_back_to_raw_pattern_on_no_reverse_match(self):
        # an unresolvable name is used directly as the pattern path
        request = self.factory.get("/custom/path/")
        output = render(
            "{% load pyaa %}{% nav_active '/custom/path/' %}",
            {"request": request},
        )
        self.assertEqual(output, "active")

    def test_path_match_with_extra_request_query_params_returns_active(self):
        # the pattern has no query params, so the query check iterates nothing
        # and the path match alone yields active
        request = self.factory.get("/list/?page=2")
        output = render(
            "{% load pyaa %}{% nav_active '/list/' %}",
            {"request": request},
        )
        self.assertEqual(output, "active")

    def test_pattern_query_params_mismatch_returns_empty(self):
        # the pattern carries a query param that the request does not satisfy
        request = self.factory.get("/list/?page=1")
        output = render(
            "{% load pyaa %}{% nav_active '/list/?page=2' %}",
            {"request": request},
        )
        self.assertEqual(output, "")


class ElementLayoutResolutionTest(TestCase):
    def test_element_resolves_layout_from_page_layout_context(self):
        # the page_layout context var drives layout-specific template lookup,
        # falling back to the base element template when no variant exists
        output = render(
            "{% load pyaa %}{% element hr %}{% endelement %}",
            {"page_layout": "default"},
        )
        self.assertIn('class="divider"', output)

    def test_element_splits_tags_kwarg_into_list(self):
        output = render(
            "{% load pyaa %}{% element button tags='outline-error' %}Go{% endelement %}"
        )
        self.assertIn("btn-outline", output)
        self.assertIn("btn-error", output)

    def test_element_inside_include_uses_page_layout(self):
        output = render(
            "{% load pyaa %}{% element button %}Save{% endelement %}",
            {"page_layout": "admin"},
        )
        self.assertIn("Save", output)


class NamedSlotCollectionTest(TestCase):
    def test_named_slot_in_element_body_is_collected(self):
        # a named slot inside an element body is collected into the slots
        # context and rendered in the matching slot of the element template
        output = render(
            "{% load pyaa %}"
            "{% element card %}{% slot header %}Title{% endslot %}Body"
            "{% endelement %}"
        )
        self.assertIn("Title", output)
        self.assertIn("Body", output)
        self.assertIn("card-header", output)
