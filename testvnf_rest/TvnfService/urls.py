"""example URL Configuration

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
from rest_framework import serializers, viewsets, routers
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register(prefix='suts', viewset=views.TestResetReq, basename='suts')
#router.register(prefix='testvnf', viewset=TvnfViewSet)

urlpatterns = [ 
  url(r'^', include(router.urls)),
  url(r'suts/(?P<sutId>\w+)$', views.TestcaseReq.as_view(), name="TestEnvCapabilityReq"),
  url(r'suts/(?P<sutId>\w+)/runTests', views.RunTestcaseReq.as_view(), name="executeTestsReq"),
  url(r'suts/(?P<sutId>\w+)', views.ResetReq.as_view(), name="ResetReq"),
#  url(r'suts/testdelete', views.TestResetReq.as_view(), name="TestResetReq"),
  url(r'suts', views.SetupEnvReq.as_view(), name="SetupEnvReq"),
  url(r'status', views.QueryStateReq.as_view(), name="QueryStateReq"),
  url(r'abortTests/(?P<sessionId>\w+)', views.AbortTestExecutionReq.as_view(), name="AbortTestExecutionReq"),
  url(r'testResults/(?P<sessionId>[\w\-]+)$', views.ReportTestResultReq.as_view(), name="ReportTestResultReq"),
#  url(r'^', include(router.urls)),
]

