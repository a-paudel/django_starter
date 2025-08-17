from django import template
from django.core.paginator import Page
from django.http import HttpRequest

register = template.Library()


def _get_link(request: HttpRequest, page: int | str):
    if isinstance(page, str):
        return None
    query = request.GET.copy()
    query["page"] = str(page)
    url = request.path + "?" + query.urlencode()
    return url


@register.inclusion_tag("core/components/pagination.html")
def paginate(request: HttpRequest, page: Page, object_name="Results", on_each_side=2, on_ends=2):
    labels: list[int | str] = []

    # start
    for i in range(1, on_ends + 1):
        if i < (page.number - on_each_side):
            labels.append(i)

    # ellipses
    if (page.number - on_each_side) - (on_ends) > 1:
        if (page.number - on_each_side) - (on_ends) > 2:
            labels.append("...")
        else:
            labels.append(on_ends + 1)

    # before
    for i in range(page.number - on_each_side, page.number):
        if i > 0:
            labels.append(i)

    # current page
    labels.append(page.number)

    # after
    for i in range(page.number + 1, page.number + on_each_side + 1):
        if i <= page.paginator.num_pages:
            labels.append(i)

    if (page.paginator.num_pages - on_ends + 1) - (page.number + on_each_side) > 1:
        if (page.paginator.num_pages - on_ends + 1) - (page.number + on_each_side) > 2:
            labels.append("...")
            pass
        else:
            labels.append(page.number + on_each_side + 1)

    # end
    for i in range(page.paginator.num_pages - on_ends + 1, page.paginator.num_pages + 1):
        if i > page.number + on_each_side:
            labels.append(i)

    # create links
    links = [
        {
            "label": label,
            "active": label == page.number,
            "link": _get_link(request, label),
        }
        for label in labels
    ]

    return {
        "links": links,
        "page": page,
        "object_name": object_name,
    }
