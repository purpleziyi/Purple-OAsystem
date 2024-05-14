from rest_framework import serializers
from django.core.validators import FileExtensionValidator, get_available_image_extensions

class UploadImageSerializer(serializers.Serializer):
    # ImageField：会校验上传的文件是否是图片
    # .png/.jpeg/jpg
    image = serializers.ImageField(   # 注意，此处的image就是以后Body中的字段名了
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif'])],# 文件后缀名验证器
        error_messages={'required': 'Please upload pictures!', 'invalid_image': 'Upload a valid image!'} #请上传图片！

    )

    # 校验网页图片的尺寸，因为过大的图片在网页上展示的效果差不多，对服务器资源占用较多
    def validate_image(self, value):
        # 图片大小单位是字节byte
        # 1024B: 1KB
        # 1024KB: 1MB
        max_size = 0.5 * 1024 * 1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError('The maximum image size cannot exceed 0.5MB!')  # 图片最大≤0.5MB！
        return value
