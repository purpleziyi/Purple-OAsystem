from django.core.management.base import BaseCommand  # 基类
from apps.absent.models import AbsentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        # "事假", "病假", "工伤假", "婚假", "丧假", "产假", "探亲假", "公假", "年休假"
        absent_types = ["Personal Leave", "Sick Leave", "Work-related Injury Leave",
                        "Marriage Leave", "Funeral Leave", "Maternity Leave",
                        "Family Visiting Leave", "Public Holiday Leave", "Annual Leave"]
        absents = []
        for absent_type in absent_types:
            absents.append(AbsentType(name=absent_type))  # 通过AbsentType模型创建新的实例，每个对象的name属性都是不同的假期类型
        AbsentType.objects.bulk_create(absents)   # bulk_create(absents)代表批量创建absents
        self.stdout.write('Attendance type data initialized successfully!')