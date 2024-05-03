from rest_framework import serializers
from .models import Absent, AbsentType, AbsentStatusChoices
from apps.oaauth.serializers import UserSerializer
from rest_framework import exceptions
from .utils import get_responder


class AbsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentType
        fields = "__all__"    # 序列化所有字段


class AbsentSerializer(serializers.ModelSerializer):
    # read_only：这个参数，只会在将ORM模型序列化成字典时会将这个字段序列化
    # write_only：这个参数，只会在将data进行校验的时候才会用到
    absent_type = AbsentTypeSerializer(read_only=True)  # 将ORM序列化为字典时才会有效
    absent_type_id = serializers.IntegerField(write_only=True) # 前端上传的数据会把这个字段进行校验，但把ORM变为字典时不会把这个字段生成
    requester = UserSerializer(read_only=True)  # 无需前端来指定发起人，所以是“只读”字段
    responder = UserSerializer(read_only=True)  # 审批人也不需要前端来指定，这是后端制定好的流程，故而“只读”字段
    class Meta:
        model = Absent
        fields = "__all__"

    # 验证absent_type_id是否在数据库中存在
    def validate_absent_type_id(self, value):
        # 判断与pk相同的value是否存在
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError("Attendance type does not exist!")
        return value

    # create 更新时调用此函数，validated_data是一个字典，存储title，request_content...
    def create(self, validated_data):
        request = self.context['request']    # 获取request对象
        user = request.user    # 把当先登录用户保存到request上
        # 获取审批者
        responder = get_responder(request)

        # 如果是董事会的leader，请假就直接通过
        if responder is None:
            validated_data['status'] = AbsentStatusChoices.PASS
        else:
            validated_data['status'] = AbsentStatusChoices.AUDITING
        absent = Absent.objects.create(**validated_data, requester=user, responder=responder)  #‘**validated_data’表示将字典变为关键字参数
        return absent  # 将创建好的对象返回

    # update 多了一个instance，有instance是因为这个方法已经帮你找到实例对象了，我们只需修改实例上的值
    def update(self, instance, validated_data):
        if instance.status != AbsentStatusChoices.AUDITING:  # 如果实例已经被处理过（即或者通过、或者被拒）就不能再修改了
            raise exceptions.APIException(detail='The confirmed data cannot be modified!')  # 不能修改已经确定的请假数据！
        request = self.context['request']   # 先获取request对象
        user = request.user    # 再通过request对象获取user对象
        if instance.responder.uid != user.uid:  # 判断审批者是不是登录用户自己
            raise exceptions.AuthenticationFailed(detail='You cannot process this attendance!') # 您无权处理该考勤！
        # 一切正常时，则把validated_data的值赋值给实例中的值
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance