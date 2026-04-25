from django.core.management.base import BaseCommand
from api.models import Admin

class Command(BaseCommand):
    help = '初始化管理员数据'
    
    def handle(self, *args, **options):
        # 检查是否已有管理员数据
        if Admin.objects.exists():
            self.stdout.write(self.style.WARNING('管理员数据已存在，跳过初始化'))
            return
        
        # 初始化3个管理员账户
        admins = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': 'manager', 'password': 'manager123'},
            {'username': 'root', 'password': 'root123'}
        ]
        
        for admin_data in admins:
            admin = Admin(username=admin_data['username'])
            admin.set_password(admin_data['password'])
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'创建管理员: {admin_data["username"]}'))
        
        self.stdout.write(self.style.SUCCESS('管理员数据初始化完成'))