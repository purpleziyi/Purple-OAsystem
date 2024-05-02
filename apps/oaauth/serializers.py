from rest_framework import serializers
from .models import OAUser,UserStatusChoices,OADepartment

# Login的序列化类
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={"required": "please enter your email!"})
    password = serializers.CharField(max_length=20, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # checked whether the email and password exist in the DB
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("please enter the correct email!")
            if not user.check_password(password):
                raise serializers.ValidationError("Please enter the correct password!")

            # check status 判断状态
            if user.status == UserStatusChoices.INACTIVE:
                raise serializers.ValidationError("This user has not been activated yet!")
            elif user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError("This user has been locked, please contact the administrator!")
            # 为了节省执行SQL语句的次数，这里我们把user直接放到attrs中，方便在视图中使用
            attrs['user'] = user

        else:
            raise serializers.ValidationError("please input your email and password!")

        return attrs  # 校验成功时返回属性attrs


# 实现department的序列化嵌套
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):  # 继承ModelSerializer而不是Serializer，可以不用逐一写字段
    department = DepartmentSerializer()  # 将department的值以object的形式返回
    class Meta:
        model = OAUser
        # fields = "__all__"
        exclude = ('password', 'groups', 'user_permissions')
