#!/usr/bin/env python3
"""
数据迁移脚本：将用户书架数据从用户表迁移到新的书架表
"""

import json
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, UserBookshelf
from django.db import transaction

def backup_data():
    """备份现有书架数据"""
    print("开始备份书架数据...")
    users = User.objects.all()
    backup_data = []
    
    for user in users:
        try:
            bookshelf = json.loads(user.bookshelf)
            if bookshelf:
                backup_data.append({
                    'user_id': user.id,
                    'bookshelf': bookshelf
                })
        except Exception as e:
            print(f"备份用户 {user.id} 数据失败: {e}")
    
    if backup_data:
        with open('bookshelf_backup.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        print(f"备份完成，共备份 {len(backup_data)} 个用户的书架数据")
    else:
        print("没有需要备份的书架数据")

def migrate_data():
    """迁移书架数据"""
    print("开始迁移书架数据...")
    users = User.objects.all()
    migrated_count = 0
    
    for user in users:
        try:
            bookshelf = json.loads(user.bookshelf)
            if bookshelf:
                # 清除用户已有的书架记录
                UserBookshelf.objects.filter(user=user).delete()
                
                # 添加新的书架记录
                for i, book_id in enumerate(bookshelf):
                    UserBookshelf.objects.create(
                        user=user,
                        book_id=book_id,
                        sort_order=i
                    )
                migrated_count += 1
                print(f"迁移用户 {user.id} 的书架数据成功")
        except Exception as e:
            print(f"迁移用户 {user.id} 数据失败: {e}")
    
    print(f"数据迁移完成，共迁移 {migrated_count} 个用户的书架数据")

def remove_bookshelf_field():
    """从用户表中删除bookshelf字段"""
    print("开始删除用户表中的bookshelf字段...")
    
    # 这里我们修改models.py文件，移除bookshelf字段
    # 然后运行Django迁移命令
    
    print("请在修改models.py文件后运行: python manage.py makemigrations api")
    print("然后运行: python manage.py migrate")

def verify_data():
    """验证数据迁移是否成功"""
    print("开始验证数据迁移...")
    users = User.objects.all()
    verified_count = 0
    
    for user in users:
        try:
            # 从旧字段读取数据
            old_bookshelf = json.loads(user.bookshelf)
            
            # 从新表读取数据
            new_bookshelf = list(UserBookshelf.objects.filter(user=user).order_by('sort_order').values_list('book_id', flat=True))
            
            if old_bookshelf == new_bookshelf:
                verified_count += 1
                print(f"用户 {user.id} 数据验证成功")
            else:
                print(f"用户 {user.id} 数据验证失败:")
                print(f"  旧数据: {old_bookshelf}")
                print(f"  新数据: {new_bookshelf}")
        except Exception as e:
            print(f"验证用户 {user.id} 数据失败: {e}")
    
    print(f"数据验证完成，共验证 {verified_count} 个用户的数据")

def main():
    print("=== 书架数据迁移脚本 ===")
    
    # 1. 备份数据
    backup_data()
    
    # 2. 迁移数据
    migrate_data()
    
    # 3. 验证数据
    verify_data()
    
    # 4. 提示删除字段
    remove_bookshelf_field()
    
    print("=== 迁移脚本执行完成 ===")

if __name__ == "__main__":
    main()
