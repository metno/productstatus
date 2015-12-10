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
        qs.select_related('data__time_period_begin')
        qs.select_related('data__time_period_end')
        qs.select_related('data__productinstance__product__name')
        qs.select_related('data__productinstance__version')
        qs.select_related('format__name')
        qs.order_by('-modified')
        return qs[:100]
