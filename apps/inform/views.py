from rest_framework import viewsets
from .serializers import InformSerializer
from .models import Inform
from django.db.models import Q   # "or"条件的满足

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
        queryset = self.queryset.prefetch_related('reads').filter(
            Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user))


        # queryset = self.queryset.select_related('author').prefetch_related(
        #     Prefetch("reads", queryset=InformRead.objects.filter(user_id=self.request.user.uid)), 'departments').filter(
        #     Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)).distinct()
        return queryset
        # for inform in queryset:
        #     inform.is_read = InformRead.objects.filter(inform=inform, user=self.request.user).exsits()
        # return queryset

