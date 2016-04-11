import django.http
import django.shortcuts
import django.template
import django.views.generic

import productstatus.core.models


def root(request):
    return django.http.HttpResponseRedirect('/overview/')


def detailed(request):
    qs = productstatus.core.models.Product.objects.all().order_by('name')
    return django.shortcuts.render_to_response(
        'core/detailed.html',
        {
            'products': qs,
        },
        context_instance=django.template.RequestContext(request))


def uuid(request):
    return django.shortcuts.render_to_response(
        'core/uuid.html',
        {
            'products': productstatus.core.models.Product.objects.all().order_by('name'),
            'dataformats': productstatus.core.models.DataFormat.objects.all().order_by('name'),
            'servicebackends': productstatus.core.models.ServiceBackend.objects.all().order_by('name'),
        },
        context_instance=django.template.RequestContext(request))


def overview(request):
    return django.shortcuts.render_to_response(
        'core/overview.html',
        {
            'products': productstatus.core.models.Product.objects.all().order_by('name'),
        },
        context_instance=django.template.RequestContext(request))


class DataInstanceView(django.views.generic.ListView):
    model = productstatus.core.models.DataInstance
    context_object_name = 'datainstances'

    def get_queryset(self):
        qs = productstatus.core.models.DataInstance.objects.all()
        qs = qs.order_by('-created')
        qs = qs.select_related('data__time_period_begin')
        qs = qs.select_related('data__time_period_end')
        qs = qs.select_related('data__product_instance__product__name')
        qs = qs.select_related('data__product_instance__version')
        qs = qs.select_related('format__name')
        qs = qs.select_related('service_backend__name')
        return qs[:100]
