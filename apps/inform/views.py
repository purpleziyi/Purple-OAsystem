from rest_framework import viewsets
from .serializers import InformSerializer
from .models import Inform

# 使用ModelViewSet自动实现增删改查的工作
class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

