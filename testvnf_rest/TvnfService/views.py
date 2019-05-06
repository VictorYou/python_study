# -*- coding: utf-8 -*-

from models import Tvnf, Sut 

from serializers import TvnfSerializer, SutSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView

import json

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
    ''' can test in this way:
    curl --noproxy '*' -X POST http://127.0.0.1:8000/testvnf/v1/abortTests/123456
    '''
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

class SetupEnvReq(GenericAPIView):
  def post(self, request, *args, **kwargs):
    ''' can test in this way:
    curl --noproxy '*' -X POST -d tvnfId=1234 -d sutId=1234 -d deploymentInfo='info' http://127.0.0.1:8000/testvnf/v1/suts
    '''
    response = Response()
    print "hello"
    for sut in Sut.objects.all():
      print "sut id: {}".format(sut.sutId)
      print "pk: {}".format(sut.pk)
    try:
      sutId = request.data['sutId']
      tvnfId = request.data['tvnfId']
      sut = Sut.objects.create(sutId=sutId, version='0.0.1', sutStatus='A')
      Tvnf.objects.create(tvnfId=tvnfId, tvnfStatus='A')
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    response.data['class'] = 'SetupEnvReq'
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
      response.data.update({'tc list': [1, 2, 3]})
    except Exception as e:
      response.data = {'result': 'NOK'}
      print "exception caught"
      print e.__doc__
      print e.message
    response.data['class'] = 'TestcaseReq'
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
    response.data.update({'class': 'RunTestcaseReq'})
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
    response.data.update({'class': 'ResetReq'})
    return response

class TestResetReq(GenericAPIView):
  def delete(self, request, *args, **kwargs):
    response = Response()
    try:
      sut = Sut.objects.get(sutId=sutId)
      sut.delete()
      response.data = {'result': 'OK'}
    except Exception as e:
      print e.message
      response.data = {'result': 'NOK'}
    response.data.update({'class': 'ResetReq'})
    return response

class ReportTestResultReq(APIView):
  def put(self, request, sessionId, *args, **kwargs):
    ''' can be tested with:
        curl --noproxy '*' -X PUT -F logfile=@/home/viyou/github/python_study/testvnf_rest/manage.py -F TestResults="{\"info\":{\"testCaseId\": \"Create MR\", \"result\": \"pass\"}}" http://127.0.0.1:8000/testvnf/v1/testResults/12345/
    '''
    response = Response()
    try:
      print "sessionId: {}".format(sessionId)
      logfile = request.FILES['logfile']
      fs = FileSystemStorage()
      print("saving logfile filename")
      filename = fs.save('logfile', logfile)
      print("filename: {}".format(filename))
      TestResults = json.loads(request.data.get('TestResults', '[]'))
      if 'info' in TestResults:
        testResult = TestResults['info']
        testResults = [testResult]
      else:  # MultiTestResult, this is not yet implemented
        testResults = []
      print("testResults: {}".format(testResults))  
      for testResult in testResults:
        receivedResult = testResult['result']
        print("test result: {}".format(testResult['result']))
      response.data = {'result': 'OK'}
    except Exception as e:
      print("exception caught: {}, {}".format(e.message, e.__doc__))
      response.data = {'result': 'NOK'}
    response.data['class'] = 'ReportTestResultReq'
    return response

class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer
