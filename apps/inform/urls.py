from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inform'
router = DefaultRouter(trailing_slash=False)  # 路由的末尾不加/
router.register('inform', views.InformViewSet, basename='inform')

urlpatterns = [] + router.urls