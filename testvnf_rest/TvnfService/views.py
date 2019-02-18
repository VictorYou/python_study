# -*- coding: utf-8 -*-

from models import Tvnf 

from serializers import TvnfSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class QueryStateReq(GenericAPIView): 
  def get(self, request, *args, **kwargs):
    response = Response()
    try:
      response.data = {'result': 'OK'}
    except Exception as e:
      response.data = {'result': 'NOK'}
      print "exception caught"
      print e.__doc__
      print e.message
    response.data.update({'class': 'QueryStateReq'})
    return response

class AbortTestExecutionReq(GenericAPIView):
  def post(self, request, sessionId, *args, **kwargs):
    response = Response()
    try:
      print "sessionId: {}".format(sessionId)
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    response.data['class'] = 'AbortTestExecutionReq'
    return response

class TvnfViewSet(ModelViewSet):
  queryset = Tvnf.objects.all()
  serializer_class = TvnfSerializer
