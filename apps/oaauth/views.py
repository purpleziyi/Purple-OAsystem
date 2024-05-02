from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class LoginView(APIView):
    def post(self, request):
        # check the data is available or not 验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token, 'user': UserSerializer(user).data})  # 返回token和user信息
        else:  # verification failed 验证失败
            # person = ｛"username": "张三", "age": 18｝
            # person.values() = ['张三', 18] dict_values
            print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            # drf在返回响应是非200的时候，他的错误参数名叫detail，所以我们这里也叫做detail
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)