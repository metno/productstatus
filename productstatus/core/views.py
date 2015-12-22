import django.http
import django.shortcuts
import django.views.generic

import productstatus.core.models


def root(request):
    return django.http.HttpResponseRedirect('/datainstance/')


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
