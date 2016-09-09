import django.http
import django.shortcuts
import django.template
import django.views.generic

import productstatus.core.lookup
import productstatus.core.models


def root(request):
    return django.http.HttpResponseRedirect('/categories/')


def explore(request):
    objects = []
    if 'q' in request.GET and len(request.GET['q']) > 0:
        objects = productstatus.core.lookup.lookup_any(request.GET['q'])
    return django.shortcuts.render_to_response(
        'core/explore.html',
        {
            'q': request.GET['q'] if 'q' in request.GET else '',
            'objects': objects,
        },
        context_instance=django.template.RequestContext(request))


def categories(request):
    return django.shortcuts.render_to_response(
        'core/categories.html',
        {
            'products': productstatus.core.models.Product.objects.all().order_by('name'),
            'dataformats': productstatus.core.models.DataFormat.objects.all().order_by('name'),
            'servicebackends': productstatus.core.models.ServiceBackend.objects.all().order_by('name'),
        },
        context_instance=django.template.RequestContext(request))
