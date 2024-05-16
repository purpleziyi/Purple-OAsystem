from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN   # 不允许访问页面
from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth.models import AnonymousUser   # 创建匿名用户

OAUser = get_user_model()


class LoginCheckMiddleware(MiddlewareMixin):
    keyword = "JWT"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 对于那些不需要登录就能访问的接口，可以写在这里
        self.white_list = ['/auth/login']

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1. 如果返回None，那么会正常执行（包括执行视图、执行其他中间件的代码）
        # 2. 如果返回一个HttpResponse对象，那么将不会执行视图，以及后面的中间件代码
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()  # 访问中间件时创建一个没有登陆的匿名用户
            request.auth = None
            return None
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError("Please enter JWT!")

            if len(auth) == 1:
                msg = "Unavailable JWT request header!"
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = 'Unavailable JWT request header! There should be no spaces in the JWT Token!'
                raise exceptions.AuthenticationFailed(msg)

            try:
                jwt_token = auth[1]
                jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
                userid = jwt_info.get('userid')
                try:
                    # 绑定当前user到request对象上
                    user = OAUser.objects.get(pk=userid)
                    # return user, jwt_token  这是中间件，无返回内容就会正常执行，有返回内容反而不会执行，所以去掉return行
                    # HttpRequest对象：是Django内置的 （不用于views.py中ResetPwdView类中的request对象）
                    request.user = user    # 将user绑定在request上
                    request.auth = jwt_token   # 将token绑定在request上
                except:
                    msg = 'User does not exist!'
                    raise exceptions.AuthenticationFailed(msg)
            except ExpiredSignatureError:
                msg = "JWT Token has expired!"
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            print(e)
            return JsonResponse(data={"detail": "Please login first"}, status=HTTP_403_FORBIDDEN)