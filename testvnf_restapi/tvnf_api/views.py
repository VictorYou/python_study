# -*- coding: utf-8 -*-

from models import Sut

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class AddReq(GenericAPIView):
  def post(self, request, *args, **kwargs):
    response = Response()
    response.data = {'sutId': 1}
    return response
    

class SutVnfViewSet(ModelViewSet):
    queryset = Sut.objects.all()
    serializer_class = SutSerializer

