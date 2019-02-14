from rest_framework.serializers import ModelSerializer, CharField
from models import Sut, Tvnf

class SutSerializer(ModelSerializer):
  class Meta:
    model = Sut
    fields = ("id", "version", "sutId", "sutStatus",)

class TvnfSerializer(ModelSerializer):
  class Meta:
    model = Tvnf 
    fields = ("id", "tvnfId", "tvnfStatus",)
