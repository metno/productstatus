import re

import django.core.exceptions

import productstatus.core.models


UUID_REGEX = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def get_objects_from_field(field, value):
    results = []
    for subclass in productstatus.core.models.BaseModel.__subclasses__():
        try:
            qs = subclass.objects.filter(**{field: value}).order_by('-modified')
        except django.core.exceptions.FieldError:
            continue
        results += list(qs[:1000])
    return results


def lookup_uuid(query):
    matches = UUID_REGEX.search(query)
    if not matches:
        return []
    return get_objects_from_field('id', matches.group(0))


def lookup_slug(query):
    return get_objects_from_field('slug', query)


def lookup_source_key(query):
    return get_objects_from_field('source_key', query)


def lookup_name(query):
    return get_objects_from_field('name__icontains', query)


def lookup_url(query):
    return get_objects_from_field('url__contains', query)


def lookup_any(query):
    for func in [lookup_uuid, lookup_slug, lookup_source_key, lookup_name, lookup_url]:
        o = func(query)
        if not o:
            continue
        return o
    return []
