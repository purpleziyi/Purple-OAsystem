from rest_framework import serializers
from .models import Inform, InformRead
from apps.oaauth.serializers import UserSerializer, DepartmentSerializer
from apps.oaauth.models import OADepartment



class InformSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)
    # department_ids 是一个包含了部门id的列表，后端若要接收列表，就需要用到ListField
    department_ids = serializers.ListField( write_only=True)   # 校验时会用到，将模型序列化字典时不需要用到该字段

    class Meta:
         model = Inform
         fields = '__all__'
         read_only_fields = ('public',)

     # 重写保存Inform对象的create方法
    def create(self, validated_data):
         # 后续需要将validated_data中的数据都放入Inform中以便创建Inform对象，所以不相关的字段在创建时会删除
         request = self.context['request']
         department_ids = validated_data.pop('department_ids')   # 该字段不需要传给Inform，故而用pop删除
         # department_ids['0','1','2']
         # 对列表中的某个值都做相同的操作，可以用map方法

         department_ids = list(map(lambda value: int(value), department_ids))
         if 0 in department_ids:
             inform = Inform.objects.create(public=True, author=request.user, **validated_data)
         else:
             departments = OADepartment.objects.filter(id__in=department_ids).all()
             inform = Inform.objects.create(public=False, author=request.user, **validated_data)
             inform.departments.set(departments)
             inform.save()
         return inform

class ReadInformSerializer(serializers.Serializer):
    inform_pk = serializers.IntegerField(error_messages={"required": 'Please pass in the inform id!'})