import abc

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Page
from django.core.paginator import Paginator as DjangoPaginator

PAGINATOR_TOTAL_PAGES = getattr(settings, "PAGINATOR_TOTAL_PAGES", 10)
PAGINATOR_TEMPLATE = getattr(settings, "PAGINATOR_TEMPLATE", "partials/paginator.html")
PAGINATOR_ID_PREFIX = getattr(settings, "PAGINATOR_ID_PREFIX", "paginator_page")
PAGINATOR_FIRST_CLASS = getattr(settings, "PAGINATOR_FIRST_CLASS", "first")
PAGINATOR_FIRST_VERBOSE = getattr(settings, "PAGINATOR_FIRST_VERBOSE", "First")
PAGINATOR_PREVIOUS_CLASS = getattr(settings, "PAGINATOR_PREVIOUS_CLASS", "previous")
PAGINATOR_PREVIOUS_VERBOSE = getattr(settings, "PAGINATOR_PREVIOUS_VERBOSE", "Previous")
PAGINATOR_NEXT_CLASS = getattr(settings, "PAGINATOR_NEXT_CLASS", "next")
PAGINATOR_NEXT_VERBOSE = getattr(settings, "PAGINATOR_NEXT_VERBOSE", "Next")
PAGINATOR_LAST_CLASS = getattr(settings, "PAGINATOR_LAST_CLASS", "last")
PAGINATOR_LAST_VERBOSE = getattr(settings, "PAGINATOR_LAST_VERBOSE", "Last")
PAGINATOR_PAGE_PARAMETER = getattr(settings, "PAGINATOR_PAGE_PARAMETER", "page")


class Paginator(DjangoPaginator):
    """
    A paginator that caches the results and the total amount of object list on a page-by-page basis.
    """

    def __init__(
        self,
        object_list,
        per_page,
        cache_key,
        cache_timeout=300,
        count_timeout=600,
        orphans=0,
        allow_empty_first_page=True,
    ):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.cache_key = cache_key.replace(" ", "_")
        self.cache_timeout = cache_timeout
        self._cached_num_pages = None
        self._cached_num_objects = None
        self.count_timeout = count_timeout or cache_timeout

    def page(self, number):
        number = self.validate_number(number)
        cached_object_list = cache.get(self.build_cache_key(number))

        if cached_object_list is not None:
            return Page(cached_object_list, number, self)

        page = super().page(number)
        cache.set(self.build_cache_key(number), page.object_list, self.cache_timeout)
        return page

    def build_cache_key(self, page_number):
        return f"{self.cache_key}:{self.per_page}:{page_number}:{self.cache_timeout}:{self.count_timeout}"

    def build_cache_key_total(self, key):
        return f"{self.cache_key}:{key}:{self.cache_timeout}:{self.count_timeout}"

    @property
    def count(self):
        if self._cached_num_objects is None:
            key = self.build_cache_key_total("total_number")
            _total = cache.get(key)
            if _total is None:
                _total = super().count
                cache.set(key, _total, self.count_timeout)
            self._cached_num_objects = _total
        return self._cached_num_objects


class CachedPaginatorViewMixin(abc.ABC):
    """
    A Class Based View Mixin to use cached paginator instead of Django's stock one.
    """

    paginator_class = Paginator
    paginate_by = 10

    @abc.abstractmethod
    def get_cache_key(self):
        pass

    def get_paginator(
        self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs
    ):
        cache_timeout = getattr(self, "cache_timeout", 60)
        count_timeout = getattr(self, "count_timeout", 3600)

        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            cache_key=self.get_cache_key(),
            cache_timeout=cache_timeout,
            count_timeout=count_timeout,
            **kwargs,
        )


def paginate_object_list(query_string, object_list):
    assert isinstance(
        object_list, Page
    ), "The object_list should be a page of paginator object"

    paginator_list = []
    middle_page = PAGINATOR_TOTAL_PAGES // 2
    current_page = object_list.number
    domain_min = max(1, current_page - middle_page + 1)
    domain_max = min(
        object_list.paginator.num_pages + 1, domain_min + PAGINATOR_TOTAL_PAGES
    )
    domain_min = max(
        1, min(domain_min, object_list.paginator.num_pages - PAGINATOR_TOTAL_PAGES + 1)
    )

    if current_page > 1:
        query_string[PAGINATOR_PAGE_PARAMETER] = 1
        paginator_list.append(
            {
                "verbose_name": PAGINATOR_FIRST_VERBOSE,
                "page": 1,
                "class": PAGINATOR_FIRST_CLASS,
                "id": f"{PAGINATOR_ID_PREFIX}_first",
                "link": query_string.urlencode(),
            }
        )

        query_string[PAGINATOR_PAGE_PARAMETER] = current_page - 1
        paginator_list.append(
            {
                "verbose_name": PAGINATOR_PREVIOUS_VERBOSE,
                "page": current_page - 1,
                "class": PAGINATOR_PREVIOUS_CLASS,
                "id": f"{PAGINATOR_ID_PREFIX}_prev",
                "link": query_string.urlencode(),
            }
        )

    for i in range(domain_min, domain_max):
        query_string[PAGINATOR_PAGE_PARAMETER] = i
        paginator_list.append(
            {
                "verbose_name": i,
                "page": i,
                "class": "active" if i == current_page else "",
                "id": f"{PAGINATOR_ID_PREFIX}_{i}",
                "link": query_string.urlencode(),
            }
        )

    if domain_max < object_list.paginator.num_pages + 1:
        query_string[PAGINATOR_PAGE_PARAMETER] = current_page + 1
        paginator_list.append(
            {
                "verbose_name": PAGINATOR_NEXT_VERBOSE,
                "page": current_page + 1,
                "class": PAGINATOR_NEXT_CLASS,
                "id": f"{PAGINATOR_ID_PREFIX}_next",
                "link": query_string.urlencode(),
            }
        )

        query_string[PAGINATOR_PAGE_PARAMETER] = object_list.paginator.num_pages
        paginator_list.append(
            {
                "verbose_name": PAGINATOR_LAST_VERBOSE,
                "page": object_list.paginator.num_pages,
                "class": PAGINATOR_LAST_CLASS,
                "id": f"{PAGINATOR_ID_PREFIX}_last",
                "link": query_string.urlencode(),
            }
        )

    return {"object_list": object_list, "paginator_list": paginator_list}
