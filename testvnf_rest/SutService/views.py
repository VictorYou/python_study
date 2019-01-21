# -*- coding: utf-8 -*-

from models import Sut

from serializers import SutSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class TestVNFReq(GenericAPIView):
  def post(self, request, *args, **kwargs):
    response = Response()
    print "tester"
    response.data = {'sutId': 1}
    return response
    
  def get(self, request, *args, **kwargs):
    response = Response()
    response.data = "OK"
    return response

class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer
