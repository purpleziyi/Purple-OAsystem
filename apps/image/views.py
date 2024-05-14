from rest_framework.views import APIView
from .serializers import UploadImageSerializer
from rest_framework.response import Response
from shortuuid import uuid
import os
from django.conf import settings

class UploadImageView(APIView):
    def post(self, request):
        # 1. 图片是xx.png，xx.py -> xx.png
        # 2. 接收.png/.jpg/.jpeg, 不接收.txt/.py，故而需要在序列化中作校验
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            # For the sake of network security, the filename uploaded by the user cannot be used directly.
            # abc.png => sdfsdafsdjag + '.png'
            # os.path.splitext('abc.png') = ('abc', '.png'), splitext()可以分隔扩展名，得到一个tuple
            filename = uuid() + os.path.splitext(file.name)[-1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path, 'wb') as fp:   # wb: 保存二进制文件
                    for chunk in file.chunks():
                        fp.write(chunk)      # 逐步保存文件直至保存完整
            except Exception:  # 此处需要结合wangEditor的文档资料
                return Response({
                    "errno": 1,
                    "message": "Image saving failed!"
                })
            # abc.png => /media/abc.png
            file_url = settings.MEDIA_URL + filename
            return Response({
                "errno": 0,    # 注意：值是数字，不 能是字符串
                "data": {
                    "url": file_url,  # 图片 src ，必须
                    "alt": "",  # 图片描述文字，非必须
                    "href": file_url  # 图片的链接，非必须
                }
            })
        else:
            print(serializer.errors)
            return Response({
                "errno": 1,  # 只要不等于 0 就行
                "message": list(serializer.errors.values())[0][0]
            })
