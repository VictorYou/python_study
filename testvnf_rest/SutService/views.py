# -*- coding: utf-8 -*-

from models import Sut

from serializers import SutSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class SetupEnvReq(GenericAPIView):
  def post(self, request, *args, **kwargs):
    response = Response()
    print "hello"
    try:
      sutId = request.data['sutId']
      sut = Sut.objects.create(sutId=sutId, version='0.0.1', sutStatus='A')
    except Exception as e:
      print e.message
    response.data = {'sutId': sut.sutId}
    return response
    
  def get(self, request, *args, **kwargs):
    response = Response()
    sutlist = Sut.objects.all()
    try:
      sut = sutlist.first()
    except Exception as e:
      print "exception caught"
      print e.__doc__
      print e.message

    for sut in sutlist:
      print "sut id: {}".format(sut.sutId)
    response.data = "OK"
    return response

class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer
