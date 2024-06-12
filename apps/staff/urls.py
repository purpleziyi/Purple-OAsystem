from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('departments', views.DepartmentListView.as_view(), name='departments'),
    path('staff', views.StaffView.as_view(), name='staff_view'),
    path('active', views.ActiveStaffView.as_view(), name='active_staff'),
    path('test/celery', views.TestCeleryView.as_view(), name='test_celery')
]