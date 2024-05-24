from rest_framework import viewsets
from .models import Inform, InformRead
from .serializers import InformSerializer, ReadInformSerializer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Prefetch

# 使用ModelViewSet自动实现增删改查的工作
class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()    # 默认情况下会返回所有的通知列表
    serializer_class = InformSerializer

    # situations that users can see notifications 通知列表：
    # 1. inform.public=True
    # 2. inform.departments包含了用户所在的部门
    # 3. inform.author = request.user
    def get_queryset(self):
        # 如果多个条件的并查，那么就需要用到Q函数
        queryset = self.queryset.select_related('author').prefetch_related("reads","departments").filter(
            Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)).distinct()


        # queryset = self.queryset.select_related('author').prefetch_related(
        #     Prefetch("reads", queryset=InformRead.objects.filter(user_id=self.request.user.uid)), 'departments').filter(
        #     Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)).distinct()
        return queryset
        # for inform in queryset:
        #     inform.is_read = InformRead.objects.filter(inform=inform, user=self.request.user).exsits()
        # return queryset

    # 删除通知的功能（自己发布的才有权删除）
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author.uid == request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)   # uid相等时可以删除
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)  # uid不同时无权删除

    #
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # 此时的instance就是inform对象
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['read_count'] = InformRead.objects.filter(inform_id=instance.id).count()  # 获取阅读量  即统计InformRead中一共有多少数据
        return Response(data=data)

# 与前端“阅读量”views相关
class ReadInformView(APIView):
    def post(self, request):
        # 通知的id
        serializer = ReadInformSerializer(data=request.data)
        if serializer.is_valid():
            inform_pk = serializer.validated_data.get('inform_pk')
            if InformRead.objects.filter(inform_id=inform_pk, user_id=request.user.uid).exists():  # 如果阅读过
                return Response()   # 此时返回的是200
            else:   # 如果没有阅读过
                try:
                    InformRead.objects.create(inform_id=inform_pk, user_id=request.user.uid)
                except Exception as e:
                    print(e)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response()
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]},
                            status=status.HTTP_400_BAD_REQUEST)

