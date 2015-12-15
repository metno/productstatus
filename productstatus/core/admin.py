# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Product, ProductInstance, Data, DataInstance, DataFormat, ServiceBackend, Variable, Person, Institution, Projection, License


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'contact',
        'institution',
        'license',
        'name',
        'created',
        'modified',
    )
    list_filter = (
        'projection',
        'contact',
        'institution',
        'license',
        'created',
        'modified',
    )
    raw_id_fields = ('parents', 'variables')
    search_fields = ('name',)
admin.site.register(Product, ProductAdmin)


class ProductInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'reference_time',
        'version',
        'created',
        'modified',
    )
    list_filter = ('product', 'reference_time', 'created', 'modified')
admin.site.register(ProductInstance, ProductInstanceAdmin)


class DataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product_instance',
        'time_period_begin',
        'time_period_end',
        'created',
        'modified',
    )
    list_filter = (
        'product_instance',
        'time_period_begin',
        'time_period_end',
        'created',
        'modified',
    )
    raw_id_fields = ('variables',)
admin.site.register(Data, DataAdmin)


class DataInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'data',
        'format',
        'service_backend',
        'url',
        'expires',
        'created',
        'modified',
    )
    list_filter = (
        'data',
        'format',
        'service_backend',
        'expires',
        'created',
        'modified',
    )
admin.site.register(DataInstance, DataInstanceAdmin)


class DataFormatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(DataFormat, DataFormatAdmin)


class ServiceBackendAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'documentation_url', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(ServiceBackend, ServiceBackendAdmin)


class VariableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Variable, VariableAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Person, PersonAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Institution, InstitutionAdmin)


class ProjectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'definition', 'created', 'modified')
    list_filter = ('created', 'modified')
    search_fields = ('name',)
admin.site.register(Projection, ProjectionAdmin)


class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'url',
        'public',
        'created',
        'modified',
    )
    list_filter = ('public', 'created', 'modified')
    search_fields = ('name',)
admin.site.register(License, LicenseAdmin)