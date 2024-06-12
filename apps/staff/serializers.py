from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

OAUser = get_user_model()

class AddStaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, error_messages={"required": "please enter username!"})
    email = serializers.EmailField(error_messages={"required": "please enter your email!", 'invalid': 'Please enter the correct email format!'})
    password = serializers.CharField(max_length=20, error_messages={"required": 'Please enter your password!'})

    def validate(self, attrs):
        request = self.context['request']
        email = attrs.get('email')
        # 1. 验证邮箱是否存在， 如果存在则不能添加 会抛出异常
        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email address already exists!')

        # 2. 验证当前用户是否是部门的leader， 不是部门leader则不能添加staff
        if request.user.department.leader.uid != request.user.uid:
            raise serializers.ValidationError('If you are not a department leader, you cannot add employees!')
        return attrs  # 一切正常的话就返回属性

class ActiveStaffSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={"required": "please input your email", 'invalid': 'Please enter the correct email address!'})
    password = serializers.CharField(max_length=20, error_messages={"required": 'Please enter your password!'})

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = OAUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Email or password is incorrect!")  #邮箱或密码错误！
        attrs['user'] = user
        return attrs


class StaffUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xlsx', 'xls'])],
        error_messages={'required': 'Please upload a file!'}  #请上传文件！
    )