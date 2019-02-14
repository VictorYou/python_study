# -*- coding: utf-8 -*-

from models import Sut, Tvnf

from serializers import SutSerializer, TvnfSerializer

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
      tvnfId = request.data['tvnfId']
      sut = Sut.objects.create(sutId=sutId, version='0.0.1', sutStatus='A')
      Tvnf.objects.create(tvnfId=tvnfId, tvnfStatus='A')
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    return response
    
class TestcaseReq(GenericAPIView): 
  def get(self, request, sutId, *args, **kwargs):
    response = Response()
    sutlist = Sut.objects.all()
    tc_list = [1, 2, 3]
    print "arg sutId: {}".format(sutId)
    try:
      for sut in Sut.objects.all():
        print "sut id: {}".format(sut.sutId)
        print "pk: {}".format(sut.pk)
      sut = Sut.objects.get(sutId=sutId)
      response.data = {'result': 'OK'}
      response.data.update({'tc list': tc_list})
    except Exception as e:
      response.data = {'result': 'NOK'}
      print "exception caught"
      print e.__doc__
      print e.message
    return response

class RunTestcaseReq(GenericAPIView):  
  def post(self, request, sutId, *args, **kwargs):
    response = Response()
    print "hello, run sutId: {}".format(sutId)
    try:
      testcases = request.data['testcases']
      sessionId = request.data['sessionId']
      tvnfId = request.data['tvnfId']
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    return response

class ResetReq(GenericAPIView):
  def delete(self, request, sutId, *args, **kwargs):
    response = Response()
    print "delete, sutId: {}".format(sutId)
    try:
      sut = Sut.objects.get(sutId=sutId)
      sut.delete()
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    return response

class QueryStateReq(GenericAPIView): 
  def get(self, request, *args, **kwargs):
    response = Response()
    try:
      sut = Sut.objects.get(sutId=sutId)
      response.data = {'result': 'OK'}
      response.data.update({'tc list': tc_list})
    except Exception as e:
      response.data = {'result': 'NOK'}
      print "exception caught"
      print e.__doc__
      print e.message
    return response

class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer

class TvnfViewSet(ModelViewSet):
  queryset = Tvnf.objects.all()
  serializer_class = TvnfSerializer
