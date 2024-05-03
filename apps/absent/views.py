from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response

from .models import Absent, AbsentType, AbsentStatusChoices
from .serializers import AbsentSerializer, AbsentTypeSerializer
# from rest_framework.views import APIView
# from .utils import get_responder
# from apps.oaauth.serializers import UserSerializer


# Create your views here.
# 1. 发起考勤（create）
# 2. 处理考勤（update）
# 3. 查看自己的考勤列表（list?who=my）
# 4. 查看下属的考勤列表（list?who=sub）
class AbsentViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):   #  此处继承的是视图集viewsets
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer

