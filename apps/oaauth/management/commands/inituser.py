from django.core.management.base import BaseCommand
from apps.oaauth.models import OAUser, OADepartment
from rest_framework.response import Response


class Command(BaseCommand):
    def handle(self, *args, **options):
        boarder = OADepartment.objects.get(name='Board')
        developer = OADepartment.objects.get(name='PD Department')
        operator = OADepartment.objects.get(name='Operations Department')
        saler = OADepartment.objects.get(name='Sales Department')
        hr = OADepartment.objects.get(name='HR Department')
        finance = OADepartment.objects.get(name='Fin Department')

        # Employees on the board of directors are all superuser users (董事会的员工，都是superuser用户)
        # 1. 东东：属于董事会的leader
        dongdong = OAUser.objects.create_superuser(email="dongdong@qq.com", username='dongdong', password='111111',
                                                   department=boarder)
        # 2. 多多：董事会
        duoduo = OAUser.objects.create_superuser(email="duoduo@qq.com", username='duoduo', password='111111',
                                                 department=boarder)
        # 3. 张三：产品开发部的leader
        zhang = OAUser.objects.create_user(email="zhang@qq.com", username='zhang', password='111111',
                                              department=developer)
        # 4. 李四：运营部leader
        lee = OAUser.objects.create_user(email="lee@qq.com", username='lee', password='111111',
                                          department=operator)
        # 5. 王五：人事部的leader
        wang = OAUser.objects.create_user(email="wang@qq.com", username='wang', password='111111',
                                            department=hr)
        # 6. 赵六：财务部的leader
        zhao = OAUser.objects.create_user(email="zhao@qq.com", username='zhao', password='111111',
                                             department=finance)
        # 7. 孙七：销售部的leader
        sun = OAUser.objects.create_user(email="sun@qq.com", username='sun', password='111111',
                                           department=saler)

        # Assign leader and manager to the department (给部门指定leader和manager)
        # Department in charge (分管的部门)
        # dongdong：PD、OPS、SALES
        # duoduo：HR, FIN
        # 1. Board 董事会
        boarder.leader = dongdong
        boarder.manager = None

        # 2. PD Department 产品开发部
        developer.leader = zhang
        developer.manager = dongdong

        # 3. Operations Department 运营部
        operator.leader = lee
        operator.manager = dongdong

        # 4. Sales Department 销售部
        saler.leader = sun
        saler.manager = dongdong

        # 5. HR Department 人事部
        hr.leader = wang
        hr.manager = duoduo

        # 6. 财务部
        finance.leader = zhao
        finance.manager = duoduo

        boarder.save()
        developer.save()
        operator.save()
        saler.save()
        hr.save()
        finance.save()

        self.stdout.write('Initial user created successfully!')
