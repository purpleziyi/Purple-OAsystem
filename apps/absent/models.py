from django.db import models
from django.contrib.auth import get_user_model

OAUser = get_user_model()   # 构建一个对象

class AbsentStatusChoices(models.IntegerChoices):
    # 审批中
    AUDITING = 1
    # 审核通过
    PASS = 2
    # 审核拒绝
    REJECT = 3

class AbsentType(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

class Absent(models.Model):
    # 1. 标题
    title = models.CharField(max_length=200)
    # 2. 请假详细内容
    request_content = models.TextField()
    # 3. 请假类型（事假、婚假）
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE, related_name='absents', related_query_name='absents')
    # 如果在一个模型中，有多个字段对同一个模型引用了外键，那么必须指定related_name为不同的值
    # 4. 发起人 (此字段需要跟User关系产生外键关联)
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='my_absents', related_query_name='my_absents')
    # 5. 审批人（can be null）
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='sub_absents', related_query_name='sub_absents', null=True)
    # 6. 状态
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.AUDITING)
    # 7. 请假开始日期
    start_date = models.DateField()
    # 8. 请假结束日期
    end_date = models.DateField()
    # 9. 请假发起时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 10. 审批回复内容
    response_content = models.TextField(blank=True)

    class Meta:
        ordering = ('-create_time',)   # 按照时间从大到小来排序，也就是最新的排在最前面 ，所以在create_time前加一个负号
