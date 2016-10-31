from django import template
from django.utils.safestring import mark_safe

import productstatus.core.models
import productstatus.check.models


register = template.Library()


@register.simple_tag
def uuid(uuid):
    return mark_safe('<a class="ui teal label" href="/explore/?q=%(text)s">%(text)s</a>' % {'text': uuid})

@register.simple_tag
def slug(uuid):
    return mark_safe('<div class="ui purple label">%s</div>' % uuid)

@register.simple_tag
def version(uuid):
    return mark_safe('<div class="ui label">Version %s</div>' % uuid)

@register.simple_tag
def label(uuid):
    return mark_safe('<div class="ui label">%s</div>' % uuid)

@register.simple_tag
def hash_type(text):
    return mark_safe('<div class="ui label">Type: %s</div>' % text)

@register.simple_tag
def admin(type_, uuid):
    values = {
        'type': type_,
        'uuid': uuid,
    }
    return mark_safe('<a class="ui orange label" href="/admin/core/%(type)s/%(uuid)s/change/">Admin</a>' % values)

@register.simple_tag
def deleted(status):
    values = {
        'status': 'Exists' if not status else 'Deleted',
        'color': 'green' if not status else 'red',
    }
    return mark_safe('<div class="ui %(color)s label">%(status)s</div>' % values)

@register.simple_tag
def check_result_code(code):
    if code == productstatus.check.OK:
        color = 'green'
    elif code == productstatus.check.WARNING:
        color = 'yellow'
    elif code == productstatus.check.CRITICAL:
        color = 'red'
    elif code == productstatus.check.UNKNOWN:
        color = 'orange'
    else:
        raise RuntimeError('Invalid check result code: %s' % str(code))
    return mark_safe('<div class="ui %s label">%s</div>' % (color, code[1]))

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

@register.inclusion_tag('core/include/empty.html')
def core_object(object_):
    template = template_from_class(object_)
    return {
        'template': 'core/include/%s.html' % template,
        'object_class': str(object_.__class__),
        'object_type': template,
        template: object_,
    }

@register.inclusion_tag('core/include/empty.html')
def core_object_mini(object_):
    template = template_from_class(object_)
    return {
        'template': 'core/include/mini/%s.html' % template,
        'object_class': str(object_.__class__),
        'object_type': template,
        template: object_,
    }

@register.inclusion_tag('check/include/checks.html')
def product_checks(product):
    checks = productstatus.check.models.Check.objects.filter(product=product)
    return {
        'product': product,
        'checks': checks,
    }

def template_from_class(instance):
    class_list = [
        (productstatus.core.models.Data, 'data'),
        (productstatus.core.models.DataFormat, 'dataformat'),
        (productstatus.core.models.DataInstance, 'datainstance'),
        (productstatus.core.models.Institution, 'institution'),
        (productstatus.core.models.License, 'license'),
        (productstatus.core.models.Person, 'person'),
        (productstatus.core.models.Product, 'product'),
        (productstatus.core.models.ProductInstance, 'productinstance'),
        (productstatus.core.models.ServiceBackend, 'servicebackend'),
    ]
    for class_, template in class_list:
        if isinstance(instance, class_):
            return template
    return 'blank'
