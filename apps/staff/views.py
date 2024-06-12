from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment, UserStatusChoices
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer, ActiveStaffSerializer, StaffUploadSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse  #将view的名字反转成链接
from django_OAsystemback.celery import debug_task
from .tasks import send_mail_task
from django.views import View
from django.http.response import JsonResponse
from urllib import parse
# from rest_framework import generics
# from rest_framework import exceptions
# from apps.oaauth.serializers import UserSerializer
# from .paginations import StaffListPagination
# from rest_framework import viewsets
# from rest_framework import mixins
# from datetime import datetime
# import json
# import pandas as pd
# from django.http.response import HttpResponse
# from django.db import transaction


OAUser = get_user_model()

aes = aeser.AESCipher(settings.SECRET_KEY)

# Create your views here.
class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer

# 激活员工的过程：
# 1. 用户访问激活的链接的时候，会返回一个含有表单的页面，视图中可以获取到token，为了在用户提交表单的时候，post函数中能知道这个token
# 我们可以在返回页面之前，先把token存储在cookie中
# 2. 校验用户上传的邮箱和密码是否正确，并且解密token中的邮箱，与用户提交的邮箱进行对比，如果都相同，那么就是激活成功
class ActiveStaffView(View):
    def get(self, request):
        # 获取token，并把token存储到cookie中，方便下次用户传过来
        # http://127.0.0.1:8000/staff/active?token=6AkzQXz+uIIlV/+I6gXMitowszWkiiDIj9J/XBfctIY=
        token = request.GET.get('token')
        response = render(request, 'active.html')
        response.set_cookie('token', token)
        return response

    def post(self, request):
        # 从cookie中获取token
        try:
            token = request.COOKIES.get('token')
            email = aes.decrypt(token)  # 将token解密
            serializer = ActiveStaffSerializer(data=request.POST)
            if serializer.is_valid():
                form_email = serializer.validated_data.get('email')  # 表单传过来的email
                user = serializer.validated_data.get('user')
                if email != form_email:
                    return JsonResponse({"code": 400, "message": "Email error!"})
                user.status = UserStatusChoices.ACTIVED
                user.save()
                return JsonResponse({"code": 200, "message": ""})
            else:
                detail = list(serializer.errors.values())[0][0]
                return JsonResponse({"code": 400, "message": detail})
        except Exception as e:
            print(e)
            return JsonResponse({"code": 400, "message": "token error!"})


class StaffView(APIView):
    # 新增员工
    def post(self, request):
        # 如果用的是视图集，那么视图集会自动把request放到context中
        # 如果是直接继承自APIView，那么就需要手动将request对象传给serializer.context中
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 1. 保存用户数据
            user = OAUser.objects.create_user(email=email, username=username, password=password)
            department = request.user.department
            user.department = department
            user.save()

            # 2. 发送激活邮件
            # send_mail(f'Ziyi active account', recipient_list=[email],message='Ziyi active account', from_email=settings.DEFAULT_FROM_EMAIL)
            self.send_active_email(email)

            return Response()
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def send_active_email(self, email):
        token = aes.encrypt(email)  # 将用户的邮箱用AES加密
        # /staff/active?token=xxx
        active_path = reverse("staff:active_staff") + "?" + parse.urlencode({"token": token})
        # http://127.0.0.1:8000/staff/active?token=xxx
        active_url = self.request.build_absolute_uri(active_path)  # 构建绝对的uri
        # 发送一个链接，让用户点击这个链接后，跳转到激活的页面，才能激活。
        # 为了区分用户，在发送链接邮件中，该链接中应该要包含这个用户的邮箱
        # 针对邮箱要进行加密：AES
        # http://localhost:8000/staff/active?token=4dFLaXTbbzciZKGm0LIafmhOuuW11S+7kEtqdUSeFf4=
        message = f"Please click the following link to activate your account: {active_url}"  #账号激活
        subject = f'[purpleOA] Account activation'
        # send_mail(subject, recipient_list=[email], message=message, from_email=settings.DEFAULT_FROM_EMAIL)
        send_mail_task.delay(email, subject, message)

class TestCeleryView(APIView):
    def get(self, request):
        # 用celery异步执行debug_task这个任务
        debug_task.delay()
        return Response({"detail": "successfully!"})