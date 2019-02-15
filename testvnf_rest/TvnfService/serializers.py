from rest_framework.serializers import ModelSerializer, CharField
from models import Tvnf

class TvnfSerializer(ModelSerializer):
  class Meta:
    model = Tvnf 
    fields = ("id", "tvnfId", "tvnfStatus",)
