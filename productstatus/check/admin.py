from django.contrib import admin

from .models import Check, CheckConditionDataInstance, CheckConditionAge


class CheckConditionDataInstanceInline(admin.TabularInline):
    model = CheckConditionDataInstance


class CheckConditionAgeInline(admin.TabularInline):
    model = CheckConditionAge


class CheckAdmin(admin.ModelAdmin):
    readonly_fields = [
        'pagerduty_incident',
    ]
    inlines = [
        CheckConditionDataInstanceInline,
        CheckConditionAgeInline,
    ]
admin.site.register(Check, CheckAdmin)
