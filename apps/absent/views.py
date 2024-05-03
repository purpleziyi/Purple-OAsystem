from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response


from .models import Absent, AbsentType, AbsentStatusChoices
from .serializers import AbsentSerializer, AbsentTypeSerializer
from rest_framework.views import APIView
from .utils import get_responder
from apps.oaauth.serializers import UserSerializer


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

    def update(self, request, *args, **kwargs):
        # 默认情况下，如果要修改某一条数据，那么要把这个数据的序列化中指定的字段都上传
        # 如果想只修改一部分数据，那么可以在kwargs中设置partial为True
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


    # 视图集中的方法，用于处理 HTTP GET 请求，返回一个包含查询结果的响应
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        who = request.query_params.get('who')    # 从请求的查询参数中获取名为'who'的参数
        if who and who == 'sub':
            result = queryset.filter(responder=request.user)  # 若who为下属，则可以获取登陆者的下属考勤信息
        else:
            result = queryset.filter(requester=request.user)  # 没有传递who的话，则只能获取自己的考勤信息

        # result：代表符合要求的数据,是一个列表，但里面存储的是ORM模型
        # pageinage_queryset方法：会做分页的逻辑处理
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response：除了返回序列化后的数据外，还会返回总数据多少，上一页url是什么
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(result, many=True)  # result是ORM模型，要序列化之后才能给前端
        return Response(data=serializer.data)

# 1. 请假类型
class AbsentTypeView(APIView):
    def get(self, request):
        types = AbsentType.objects.all()    # 获取所有的请假类型
        serializer = AbsentTypeSerializer(types, many=True)    # 获取之后进行序列化，导入AbsentTypeSerializer，因为是queryset对象，所以many为true
        return Response(data=serializer.data)


# 2. 显示审批者
class ResponderView(APIView):
    def get(self, request):
        responder = get_responder(request)   # 获取responder
        # Serializer：如果序列化的对象是一个None，那么不会报错，而是返回一个包含除了主键外的所有字段的空字典
        serializer = UserSerializer(responder)
        return Response(data=serializer.data)