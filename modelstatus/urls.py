"""modelstatus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

import modelstatus.core.api
import tastypie.api

v1_api = tastypie.api.Api(api_name='v1')
v1_api.register(modelstatus.core.api.ModelResource())
v1_api.register(modelstatus.core.api.ModelRunResource())
v1_api.register(modelstatus.core.api.DataResource())
v1_api.register(modelstatus.core.api.DataFileResource())
v1_api.register(modelstatus.core.api.DataFormatResource())
v1_api.register(modelstatus.core.api.ServiceBackendResource())
v1_api.register(modelstatus.core.api.VariableResource())
v1_api.register(modelstatus.core.api.PersonResource())
v1_api.register(modelstatus.core.api.InstitutionResource())
v1_api.register(modelstatus.core.api.ProjectionResource())

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
]
