from unittest.mock import patch

from django.core.cache import cache
from django.http import QueryDict
from django.test import TestCase, override_settings

from pyaa.utils import cached_paginator
from pyaa.utils.cached_paginator import (
    CachedPaginatorViewMixin,
    Paginator,
    paginate_object_list,
)

# the dev settings use a dummy cache, so a real in-memory cache is used here
# to exercise the caching behavior of the paginator
LOCMEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cached-paginator-tests",
    }
}


@override_settings(CACHES=LOCMEM_CACHE)
class PaginatorTest(TestCase):
    def setUp(self):
        self.object_list = list(range(1, 101))

    def tearDown(self):
        cache.clear()

    def test_cache_key_spaces_are_replaced(self):
        paginator = Paginator(self.object_list, 10, cache_key="my key with spaces")
        self.assertEqual(paginator.cache_key, "my_key_with_spaces")

    def test_count_timeout_defaults_to_cache_timeout_when_falsy(self):
        paginator = Paginator(
            self.object_list, 10, cache_key="k", cache_timeout=120, count_timeout=0
        )
        self.assertEqual(paginator.count_timeout, 120)

    def test_count_timeout_is_respected_when_provided(self):
        paginator = Paginator(
            self.object_list, 10, cache_key="k", cache_timeout=120, count_timeout=999
        )
        self.assertEqual(paginator.count_timeout, 999)

    def test_build_cache_key(self):
        paginator = Paginator(
            self.object_list,
            10,
            cache_key="key",
            cache_timeout=300,
            count_timeout=600,
        )
        self.assertEqual(paginator.build_cache_key(2), "key:10:2:300:600")

    def test_build_cache_key_total(self):
        paginator = Paginator(
            self.object_list,
            10,
            cache_key="key",
            cache_timeout=300,
            count_timeout=600,
        )
        self.assertEqual(
            paginator.build_cache_key_total("total_number"),
            "key:total_number:300:600",
        )

    def test_page_populates_cache_on_miss(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")
        key = paginator.build_cache_key(1)
        self.assertIsNone(cache.get(key))

        page = paginator.page(1)

        self.assertEqual(list(page.object_list), list(range(1, 11)))
        self.assertEqual(list(cache.get(key)), list(range(1, 11)))

    def test_page_returns_cached_object_list_on_hit(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")
        key = paginator.build_cache_key(2)
        cache.set(key, ["cached", "values"], 300)

        with patch.object(cached_paginator.DjangoPaginator, "page") as mock_super_page:
            page = paginator.page(2)

        # super().page should not be called on a cache hit
        mock_super_page.assert_not_called()
        self.assertEqual(list(page.object_list), ["cached", "values"])
        self.assertEqual(page.number, 2)

    def test_count_caches_total(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")
        key = paginator.build_cache_key_total("total_number")

        self.assertEqual(paginator.count, 100)
        self.assertEqual(cache.get(key), 100)

    def test_count_reads_from_cache(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")
        key = paginator.build_cache_key_total("total_number")
        cache.set(key, 42, 600)

        self.assertEqual(paginator.count, 42)

    def test_count_is_memoized_on_instance(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")

        self.assertEqual(paginator.count, 100)

        # clearing the cache should not affect the memoized value
        cache.clear()
        self.assertEqual(paginator.count, 100)

    def test_num_pages_uses_cached_count(self):
        paginator = Paginator(self.object_list, 10, cache_key="key")
        self.assertEqual(paginator.num_pages, 10)


class CachedPaginatorViewMixinTest(TestCase):
    def tearDown(self):
        cache.clear()

    def test_get_paginator_uses_defaults(self):
        class View(CachedPaginatorViewMixin):
            def get_cache_key(self):
                return "view-key"

        view = View()
        paginator = view.get_paginator(list(range(20)), 5)

        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(paginator.cache_key, "view-key")
        self.assertEqual(paginator.cache_timeout, 60)
        self.assertEqual(paginator.count_timeout, 3600)
        self.assertEqual(paginator.per_page, 5)

    def test_get_paginator_uses_custom_timeouts(self):
        class View(CachedPaginatorViewMixin):
            cache_timeout = 111
            count_timeout = 222

            def get_cache_key(self):
                return "custom"

        view = View()
        paginator = view.get_paginator(list(range(10)), 2)

        self.assertEqual(paginator.cache_timeout, 111)
        self.assertEqual(paginator.count_timeout, 222)


@override_settings(CACHES=LOCMEM_CACHE)
class PaginateObjectListTest(TestCase):
    def tearDown(self):
        cache.clear()

    def _query_string(self):
        qd = QueryDict(mutable=True)
        qd["foo"] = "bar"
        return qd

    def test_requires_a_page_instance(self):
        with self.assertRaises(AssertionError):
            paginate_object_list(self._query_string(), [1, 2, 3])

    def test_first_page_has_no_first_or_previous_links(self):
        # 20 pages so navigation links beyond the visible window appear
        paginator = Paginator(list(range(200)), 10, cache_key="key")
        page = paginator.page(1)

        result = paginate_object_list(self._query_string(), page)

        ids = [entry["id"] for entry in result["paginator_list"]]
        self.assertNotIn("paginator_page_first", ids)
        self.assertNotIn("paginator_page_prev", ids)
        # next/last should be present since there are more pages
        self.assertIn("paginator_page_next", ids)
        self.assertIn("paginator_page_last", ids)

    def test_middle_page_has_all_navigation_links(self):
        paginator = Paginator(list(range(200)), 10, cache_key="key")
        page = paginator.page(10)

        result = paginate_object_list(self._query_string(), page)

        ids = [entry["id"] for entry in result["paginator_list"]]
        self.assertIn("paginator_page_first", ids)
        self.assertIn("paginator_page_prev", ids)
        self.assertIn("paginator_page_next", ids)
        self.assertIn("paginator_page_last", ids)

    def test_last_page_has_no_next_or_last_links(self):
        paginator = Paginator(list(range(200)), 10, cache_key="key")
        page = paginator.page(20)

        result = paginate_object_list(self._query_string(), page)

        ids = [entry["id"] for entry in result["paginator_list"]]
        self.assertNotIn("paginator_page_next", ids)
        self.assertNotIn("paginator_page_last", ids)
        self.assertIn("paginator_page_first", ids)
        self.assertIn("paginator_page_prev", ids)

    def test_active_class_marks_current_page(self):
        paginator = Paginator(list(range(100)), 10, cache_key="key")
        page = paginator.page(3)

        result = paginate_object_list(self._query_string(), page)

        active = [
            entry for entry in result["paginator_list"] if entry["class"] == "active"
        ]
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["page"], 3)

    def test_links_preserve_existing_query_string(self):
        paginator = Paginator(list(range(100)), 10, cache_key="key")
        page = paginator.page(1)

        result = paginate_object_list(self._query_string(), page)

        first_numbered = result["paginator_list"][0]
        self.assertIn("foo=bar", first_numbered["link"])
        self.assertIn("page=", first_numbered["link"])

    def test_single_page_has_no_navigation_links(self):
        paginator = Paginator(list(range(5)), 10, cache_key="key")
        page = paginator.page(1)

        result = paginate_object_list(self._query_string(), page)

        ids = [entry["id"] for entry in result["paginator_list"]]
        self.assertNotIn("paginator_page_first", ids)
        self.assertNotIn("paginator_page_next", ids)
        self.assertEqual(result["object_list"], page)
