from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ResetPwdSerializer
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


# 以下方法适合项目中“有较多接口时不需要登录就可以访问”的情况
# class AuthenticatedRequiredView:
#     permission_classes = [IsAuthenticated]


# 以下方法适合项目中“除了login以外均需要登录才可以访问”的情况
class ResetPwdView(APIView):
    def post(self, request):
        from rest_framework.request import Request
        # request：是DRF封装的，rest_framework.request.Request （不同于middelwares.py中的request对象）
        # 这个对象是针对django的HttpRequest对象进行了封装
        serializer = ResetPwdSerializer(data=request.data, context={'request': request})  # context参数是一个字典

        if serializer.is_valid():    # 如果验证成功就获取新密码
            pwd1 = serializer.validated_data.get('pwd1')   # 拿到pwd1（也可以是pwd2，因为此时pwd1 == pwd2）的值
            request.user.set_password(pwd1)    # 通过request获取用户，然后把pwd1传给这个用户
            request.user.save()      # 然后保存
            return Response()      # 返回Response对象，不一定要传参，只要status是200即可
        else:                        # 验证失败
            print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

