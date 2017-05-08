import productstatus
import productstatus.core.models


def get_expired_datainstances():
    """
    Returns a list of expired DataInstance resources, grouped by Product and ServiceBackend.
    """
    products = productstatus.core.models.Product.objects.all()
    servicebackends = productstatus.core.models.ServiceBackend.objects.all()
    results = []
    for product in products:
        for servicebackend in servicebackends:
            qs = productstatus.core.models.DataInstance.objects.filter(
                data__product_instance__product=product,
                service_backend=servicebackend,
                deleted=False,
                expires__lte=productstatus.now_with_timezone(),
            ).order_by('created')
            if qs.count() == 0:
                continue
            results += [(product, servicebackend, list(qs))]
    return results
