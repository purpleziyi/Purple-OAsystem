from django.core.management.base import BaseCommand
from apps.oaauth.models import OADepartment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # initialize department
        boarder = OADepartment.objects.create(name='Board', intro="Board")   # 董事会
        developer = OADepartment.objects.create(name='PD Department',
                                                intro="Product design, technical development")   # 产品开发部
        operator = OADepartment.objects.create(name='Operations Department',
                                               intro="Customer operations, product operations")     # 运营部
        saler = OADepartment.objects.create(name='Sales Department', intro="Product sales")      # 销售部
        hr = OADepartment.objects.create(name='HR Department',
                                         intro="Employee recruitment, employee training, employee assessment") # HR
        finance = OADepartment.objects.create(name='Fin Department',
                                              intro="Financial statements, financial auditing")    # 财务部
        self.stdout.write('Department data initialization successful!')

