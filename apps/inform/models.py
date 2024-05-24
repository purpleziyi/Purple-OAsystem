from django.db import models
from django.contrib.auth import get_user_model
from apps.oaauth.models import OADepartment

OAUser = get_user_model()

# Create your models here.
class Inform(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    """If the department uploaded by the front end contains 0, such as [0], auth_group
    then this notification is considered to be visible to all departments."""
    # 如果前端上传的department中包含了0，比如[0]，那么就认为这个通知是所有部门可见
    public = models.BooleanField(default=False)
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='informs', related_query_name='informs')
    # departments: 序列化的时候用，前端上传部门id，我们通过department_ids来获取
    departments = models.ManyToManyField(OADepartment, related_name='informs', related_query_name='informs') # 一个通知可以被多个部门看到，一个部门也可以看到多个通知

    class Meta:
        ordering = ("-create_time",)   # 根据创建时间来倒序排列，即最新的排在最上方

# 记录用户查看过哪些通知,与前端“阅读量”views相关
class InformRead(models.Model):
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    user = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    read_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inform', 'user')  # inform和user组合起来就必须是唯一的