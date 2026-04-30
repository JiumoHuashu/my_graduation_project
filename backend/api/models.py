from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import os

class FalooBook(models.Model):
    book_id = models.CharField(max_length=20, primary_key=True, unique=True, verbose_name="书籍ID")
    title = models.CharField(max_length=100, verbose_name="书名")
    author = models.CharField(max_length=50, verbose_name="作者")
    cover_url = models.URLField(max_length=255, verbose_name="封面URL")
    main_category = models.CharField(max_length=20, verbose_name="主分类")
    sub_category = models.CharField(max_length=20, verbose_name="子分类")
    word_count = models.IntegerField(default=0, verbose_name="字数")
    read_count = models.IntegerField(default=0, verbose_name="阅读量")
    monthly_read = models.IntegerField(default=0, verbose_name="月阅读")
    total_read = models.IntegerField(default=0, verbose_name="总阅读")
    monthly_flowers = models.IntegerField(default=0, verbose_name="月鲜花")
    total_flowers = models.IntegerField(default=0, verbose_name="总鲜花")
    introduction = models.TextField(verbose_name="简介")
    tags = models.CharField(max_length=100, verbose_name="标签")
    onboarding_time = models.CharField(max_length=20, default="2024-01-01", verbose_name="上架时间")
    update_time = models.CharField(max_length=20, default="2024-01-01", verbose_name="更新时间")

    class Meta:
        db_table = 'faloo_books'
        verbose_name = '飞卢书籍'
        verbose_name_plural = '飞卢书籍'

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=100, verbose_name="密码")

    class Meta:
        db_table = 'faloo_admin'
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def check_password(self, password):
        return check_password(password, self.password)

class User(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="用户ID")
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    password = models.CharField(max_length=128, verbose_name="密码")
    avatar = models.CharField(max_length=255, default="https://img2.baidu.com/it/u=1871712030,2993625157&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500", verbose_name="头像")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        db_table = 'faloo_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class UserBookshelf(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="书架ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    book_id = models.CharField(max_length=20, verbose_name="书籍ID")
    sort_order = models.IntegerField(default=0, verbose_name="排序序号")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        db_table = 'user_bookshelf'
        verbose_name = '用户书架'
        verbose_name_plural = '用户书架'
        unique_together = ('user', 'book_id')

class Rating(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="评分ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    book_id = models.CharField(max_length=20, verbose_name="书籍ID")
    score = models.FloatField(verbose_name="评分")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'user_ratings'
        verbose_name = '用户评分'
        verbose_name_plural = '用户评分'
        unique_together = ('user', 'book_id')


class UserActionLog(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="行为ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    book_id = models.CharField(max_length=20, verbose_name="书籍ID")
    action_type = models.CharField(max_length=10, choices=[('like', '收藏'), ('dislike', '不感兴趣')], verbose_name="行为类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'user_action_logs'
        verbose_name = '用户行为日志'
        verbose_name_plural = '用户行为日志'
