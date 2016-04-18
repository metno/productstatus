from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def uuid(uuid):
    return mark_safe('<div class="ui teal label">%s</div>' % uuid)

@register.simple_tag
def slug(uuid):
    return mark_safe('<div class="ui purple label">%s</div>' % uuid)

@register.simple_tag(takes_context=True)
def active(context, view):
    return 'active' if context.request.resolver_match.url_name == view else ''

@register.simple_tag
def operational(product):
    if product.operational:
        values = { 'text': 'Operational', 'color': 'green' }
    else:
        values = { 'text': 'Non-operational', 'color': 'red' }
    return mark_safe('<span class="ui %(color)s label">%(text)s</span>' % values)

@register.simple_tag
def data_instances_with_data_format_on_service_backend(product_instance,
                                                       format,
                                                       service_backend):
    return product_instance.data_instances_with_data_format_on_service_backend(
        format,
        service_backend,
    )

@register.simple_tag
def data_formats_on_service_backend(product_instance, service_backend):
    return product_instance.data_formats_on_service_backend(service_backend)
