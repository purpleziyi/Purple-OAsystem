from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse  #将view的名字反转成链接



OAUser = get_user_model()

aes = aeser.AESCipher(settings.SECRET_KEY)

# Create your views here.
class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer

class ActiveStaffView(APIView):
    def get(self, request):
        return Response()
        # pass


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
        token = aes.encrypt(email)
        # /staff/active?token=xxx
        active_path = reverse("staff:active_staff") + "?token=" + token
        # http://127.0.0.1:8000/staff/active?token=xxx
        active_url = self.request.build_absolute_uri(active_path)  # 构建绝对的uri
        # 发送一个链接，让用户点击这个链接后，跳转到激活的页面，才能激活。
        # 为了区分用户，在发送链接邮件中，该链接中应该要包含这个用户的邮箱
        # 针对邮箱要进行加密：AES
        # http://localhost:8000/staff/active?token=4dFLaXTbbzciZKGm0LIafmhOuuW11S+7kEtqdUSeFf4=
        message = f"Please click the following link to activate your account: {active_url}"  #账号激活
        send_mail(f'[purpleOA] Account activation', recipient_list=[email], message=message, from_email=settings.DEFAULT_FROM_EMAIL)