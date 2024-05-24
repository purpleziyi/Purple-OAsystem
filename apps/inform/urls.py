from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.urls import path

app_name = 'inform'
router = DefaultRouter(trailing_slash=False)  # 路由的末尾不加/
router.register('inform', views.InformViewSet, basename='inform')

urlpatterns = [
    path('inform/read', views.ReadInformView.as_view(), name='read_inform')
] + router.urls