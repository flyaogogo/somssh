"""somssh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from deploy import views as dviews
from sprocess import views as sviews
from userauth import views as uviews
from somssh import views as ssviews

urlpatterns = [
    url(r'^$', ssviews.index, name='index'),
    url(r'^system/config/$', ssviews.sys_config, name='sys_config'),
    url(r'^projects$', dviews.job_index, name='job_index_project'),
    url(r'^admin/', admin.site.urls),
    url(r'', include('userauth.urls')),
    url(r'^audit/log_release/$', dviews.release_log, name='log_release'),
    url(r'^audit/log_process/$', sviews.process_log, name='log_process'),
    url(r'^audit/log_audit/(?P<log_type>[\w-]+)/$', uviews.audit_log, name='log_audit'),
    url(r'^manage/', include('deploy.urls')),
    url(r'^manage/', include('sconf.urls')),
    url(r'^manage/', include('sprocess.urls')),
    url(r'^qcloud/', include('qcloud.urls')),
    url(r'^nginx/', include('snginx.urls')),
    url(r'^about/$', dviews.about, name='about'),
]
