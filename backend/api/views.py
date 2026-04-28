from django.http import JsonResponse
from .models import FalooBook, Admin, User, Rating, UserBookshelf, UserActionLog
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .cache_utils import CacheManager
import json
import os
import subprocess
import threading
import time
from django.conf import settings
from django.core.files.storage import default_storage

# Task management variables
task_processes = {}
task_logs = {}
task_status = {}

# Script paths
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts')
CRAWLER_SCRIPT = os.path.join(SCRIPTS_DIR, 'crawler.py')
IMPORT_SCRIPT = os.path.join(SCRIPTS_DIR, 'import_to_db.py')

# Log file paths
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Simple admin authentication decorator
def admin_required(func):
    def wrapper(request, *args, **kwargs):
        # For simplicity, we'll just check if the request is from admin
        # In a production environment, you should implement proper authentication
        if not request.META.get('HTTP_AUTHORIZATION'):
            return JsonResponse({"code": 401, "msg": "需要管理员权限"}, status=401)
        return func(request, *args, **kwargs)
    return wrapper

def capture_process_output(process, task_id):
    """Capture subprocess output and store it in task_logs"""
    task_logs[task_id] = []
    
    # Read stdout line by line
    for line in iter(process.stdout.readline, b''):
        # 明确使用 utf-8 解码，替换无法识别的字符
        line_str = line.decode('utf-8', errors='replace').strip()
        # 清理控制字符
        line_str = ''.join(char for char in line_str if ord(char) >= 32 or char in '\n\t')
        if line_str:
            task_logs[task_id].append(line_str)
            # Limit log size to prevent memory issues
            if len(task_logs[task_id]) > 1000:
                task_logs[task_id] = task_logs[task_id][-1000:]
    
    # Read stderr
    for line in iter(process.stderr.readline, b''):
        # 明确使用 utf-8 解码，替换无法识别的字符
        line_str = line.decode('utf-8', errors='replace').strip()
        # 清理控制字符
        line_str = ''.join(char for char in line_str if ord(char) >= 32 or char in '\n\t')
        if line_str:
            task_logs[task_id].append(f"[ERROR] {line_str}")
            if len(task_logs[task_id]) > 1000:
                task_logs[task_id] = task_logs[task_id][-1000:]
    
    process.wait()
    task_status[task_id] = 'completed'
    task_processes.pop(task_id, None)

def book_rank_api(request):
    """
    排行榜接口：支持分类筛选，按阅读量排序
    URL: /api/rank/?category=xxx
    """
    try:
        category = request.GET.get('category')

        cache_key = CacheManager.get_book_rank_key(category)
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data}, safe=False)

        books = FalooBook.objects.all().order_by('-read_count')

        if category and category != '全部':
            books = books.filter(main_category=category)

        data = []
        for b in books[:30]:
            data.append({
                "book_id": b.book_id,
                "title": b.title,
                "author": b.author,
                "cover_url": b.cover_url,
                "category": b.main_category,
                "sub_category": b.sub_category,
                "read_count": b.read_count,
                "monthly_read": b.monthly_read,
                "total_read": b.total_read,
                "monthly_flowers": b.monthly_flowers,
                "total_flowers": b.total_flowers,
                "word_count": b.word_count,
                "introduction": b.introduction[:60] + "..." if b.introduction else "暂无简介",
                "update_time": b.update_time,
                "tags": b.tags
            })

        CacheManager.set(cache_key, data, 300)

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def book_detail_api(request, book_id):
    """
    书籍详情接口：根据 book_id 获取单本书的完整信息
    URL: /api/book/<book_id>/
    """
    try:
        cache_key = CacheManager.get_book_detail_key(book_id)
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data})

        book = FalooBook.objects.get(book_id=book_id.strip())

        data = {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "cover_url": book.cover_url,
            "onboarding_time": book.onboarding_time,
            "update_time": book.update_time,
            "category": book.main_category,
            "sub_category": book.sub_category,
            "word_count": book.word_count,
            "tags": book.tags,
            "introduction": book.introduction,
            "read_count": book.read_count,
            "monthly_read": book.monthly_read,
            "total_read": book.total_read,
            "monthly_flowers": book.monthly_flowers,
            "total_flowers": book.total_flowers
        }

        CacheManager.set(cache_key, data, 3600)

        return JsonResponse({"code": 200, "msg": "success", "data": data})

    except FalooBook.DoesNotExist:
        return JsonResponse({
            "code": 404,
            "msg": f"未找到 ID 为 {book_id} 的书籍，请检查数据库记录"
        }, status=404)

    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": f"内部逻辑错误: {str(e)}"
        }, status=500)


@csrf_exempt
def admin_login(request):
    """
    管理员登录接口
    URL: /api/admin/login/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"code": 400, "msg": "用户名和密码不能为空"}, status=400)

            admin = Admin.objects.filter(username=username).first()
            if not admin:
                return JsonResponse({"code": 401, "msg": "用户名或密码错误"}, status=401)

            if not admin.check_password(password):
                return JsonResponse({"code": 401, "msg": "用户名或密码错误"}, status=401)

            return JsonResponse({"code": 200, "msg": "登录成功", "data": {"username": admin.username}})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
def admin_books(request):
    """
    管理员管理书籍接口
    GET: 获取书籍列表
    POST: 添加书籍
    URL: /api/admin/books/
    """
    if request.method == 'GET':
        try:
            books = FalooBook.objects.all()
            data = []
            for book in books:
                data.append({
                    "id": book.book_id,
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": book.cover_url,
                    "main_category": book.main_category,
                    "sub_category": book.sub_category,
                    "word_count": book.word_count,
                    "read_count": book.read_count,
                    "monthly_read": book.monthly_read,
                    "total_read": book.total_read,
                    "monthly_flowers": book.monthly_flowers,
                    "total_flowers": book.total_flowers,
                    "introduction": book.introduction,
                    "tags": book.tags,
                    "onboarding_time": book.onboarding_time,
                    "update_time": book.update_time
                })
            return JsonResponse({"code": 200, "msg": "success", "data": data})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            book = FalooBook(
                book_id=data.get('book_id'),
                title=data.get('title'),
                author=data.get('author'),
                cover_url=data.get('cover_url'),
                main_category=data.get('main_category'),
                sub_category=data.get('sub_category'),
                word_count=data.get('word_count', 0),
                read_count=data.get('read_count', 0),
                monthly_read=data.get('monthly_read', 0),
                total_read=data.get('total_read', 0),
                monthly_flowers=data.get('monthly_flowers', 0),
                total_flowers=data.get('total_flowers', 0),
                introduction=data.get('introduction', ''),
                tags=data.get('tags', ''),
                onboarding_time=data.get('onboarding_time', ''),
                update_time=data.get('update_time', '')
            )
            book.save()

            CacheManager.invalidate_book_cache(data.get('book_id'))

            return JsonResponse({"code": 200, "msg": "添加成功", "data": {"id": book.book_id}})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持GET和POST请求"}, status=405)


@csrf_exempt
def admin_book_detail(request, book_id):
    """
    管理员管理书籍详情接口
    PUT: 更新书籍
    DELETE: 删除书籍
    URL: /api/admin/books/<book_id>/
    """
    if request.method == 'PUT':
        try:
            book = FalooBook.objects.get(book_id=book_id)
            data = json.loads(request.body)

            for key, value in data.items():
                if hasattr(book, key):
                    setattr(book, key, value)

            book.save()

            CacheManager.invalidate_book_cache(book_id)

            return JsonResponse({"code": 200, "msg": "更新成功"})

        except FalooBook.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "书籍不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'DELETE':
        try:
            book = FalooBook.objects.get(book_id=book_id)
            book.delete()

            CacheManager.invalidate_book_cache(book_id)

            return JsonResponse({"code": 200, "msg": "删除成功"})

        except FalooBook.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "书籍不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持PUT和DELETE请求"}, status=405)


@csrf_exempt
def user_register(request):
    """
    用户注册接口
    URL: /api/user/register/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not email or not password:
                return JsonResponse({"code": 400, "msg": "用户名、邮箱和密码不能为空"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"code": 400, "msg": "用户名已存在"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"code": 400, "msg": "邮箱已存在"}, status=400)

            user = User(username=username, email=email)
            user.set_password(password)
            user.save()

            return JsonResponse({"code": 200, "msg": "注册成功", "data": {"username": user.username, "email": user.email, "avatar": user.avatar}})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
def user_login(request):
    """
    用户登录接口
    URL: /api/user/login/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"code": 400, "msg": "用户名和密码不能为空"}, status=400)

            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({"code": 401, "msg": "用户名或密码错误"}, status=401)

            if not user.check_password(password):
                return JsonResponse({"code": 401, "msg": "用户名或密码错误"}, status=401)

            return JsonResponse({"code": 200, "msg": "登录成功", "data": {"id": user.id, "username": user.username, "email": user.email, "avatar": user.avatar}})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
def user_bookshelf(request):
    """
    用户书架管理接口
    GET: 获取书架列表
    POST: 添加书籍到书架
    URL: /api/user/bookshelf/
    """
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            if not user_id:
                return JsonResponse({"code": 400, "msg": "用户ID不能为空"}, status=400)

            user = User.objects.get(id=user_id)
            # 从新的书架表获取数据
            bookshelf_items = UserBookshelf.objects.filter(user=user).order_by('sort_order')
            bookshelf = [item.book_id for item in bookshelf_items]

            return JsonResponse({"code": 200, "msg": "success", "data": bookshelf})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            if not user_id or not book_id:
                return JsonResponse({"code": 400, "msg": "用户ID和书籍ID不能为空"}, status=400)

            user = User.objects.get(id=user_id)
            
            # 检查是否已在书架中
            existing = UserBookshelf.objects.filter(user=user, book_id=book_id).first()
            if not existing:
                # 获取当前最大排序号
                max_order = UserBookshelf.objects.filter(user=user).aggregate(models.Max('sort_order'))['sort_order__max'] or -1
                UserBookshelf.objects.create(
                    user=user,
                    book_id=book_id,
                    sort_order=max_order + 1
                )

            # 重新获取书架数据
            bookshelf_items = UserBookshelf.objects.filter(user=user).order_by('sort_order')
            bookshelf = [item.book_id for item in bookshelf_items]

            CacheManager.delete(CacheManager.get_bookshelf_recommend_key(user_id))

            return JsonResponse({"code": 200, "msg": "添加成功", "data": bookshelf})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持GET和POST请求"}, status=405)


@csrf_exempt
def user_bookshelf_remove(request):
    """
    用户书架移除接口
    POST: 从书架中移除书籍
    URL: /api/user/bookshelf/remove/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            book_id = data.get('book_id')

            if not user_id or not book_id:
                return JsonResponse({"code": 400, "msg": "用户ID和书籍ID不能为空"}, status=400)

            user = User.objects.get(id=user_id)
            
            # 从新的书架表删除数据
            UserBookshelf.objects.filter(user=user, book_id=book_id).delete()

            # 重新获取书架数据
            bookshelf_items = UserBookshelf.objects.filter(user=user).order_by('sort_order')
            bookshelf = [item.book_id for item in bookshelf_items]

            CacheManager.delete(CacheManager.get_bookshelf_recommend_key(user_id))

            return JsonResponse({"code": 200, "msg": "移除成功", "data": bookshelf})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
def book_search(request):
    """
    书籍搜索接口
    GET: 根据关键词搜索书籍
    URL: /api/search/
    """
    if request.method == 'GET':
        try:
            keyword = request.GET.get('keyword', '')

            if not keyword:
                return JsonResponse({"code": 400, "msg": "搜索关键词不能为空"}, status=400)

            cache_key = CacheManager.get_search_key(keyword)
            cached_data = CacheManager.get(cache_key)
            if cached_data:
                return JsonResponse({"code": 200, "msg": "success", "data": cached_data})

            books = FalooBook.objects.filter(title__icontains=keyword)
            data = []
            for book in books:
                data.append({
                    "id": book.book_id,
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": book.cover_url,
                    "main_category": book.main_category,
                    "sub_category": book.sub_category,
                    "word_count": book.word_count,
                    "read_count": book.read_count,
                    "monthly_read": book.monthly_read,
                    "total_read": book.total_read,
                    "monthly_flowers": book.monthly_flowers,
                    "total_flowers": book.total_flowers,
                    "introduction": book.introduction,
                    "tags": book.tags,
                    "onboarding_time": book.onboarding_time,
                    "update_time": book.update_time
                })

            CacheManager.set(cache_key, data, 300)

            return JsonResponse({"code": 200, "msg": "success", "data": data})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


def book_recommend(request):
    """
    书籍推荐接口
    GET: 根据分类推荐书籍
    URL: /api/recommend/?main_category=xxx&sub_category=xxx
    """
    try:
        main_category = request.GET.get('main_category')
        sub_category = request.GET.get('sub_category')

        if not main_category or not sub_category:
            return JsonResponse({"code": 400, "msg": "主分类和子分类不能为空"}, status=400)

        cache_key = CacheManager.get_recommend_key(main_category, sub_category)
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data}, safe=False)

        books = FalooBook.objects.filter(
            main_category=main_category,
            sub_category=sub_category
        ).order_by('-read_count')[:10]

        data = []
        for i, book in enumerate(books):
            similarity = 1.0 - (i * 0.05)
            data.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "cover_url": book.cover_url,
                "similarity": similarity,
                "intro": book.introduction[:50] + "..." if book.introduction else "暂无简介"
            })

        CacheManager.set(cache_key, data, 600)

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def book_recommend_by_book(request):
    """
    基于书名的推荐接口
    GET: 根据书名推荐相似书籍
    URL: /api/recommend/book/?book_name=xxx
    """
    try:
        book_name = request.GET.get('book_name', '')

        if not book_name:
            return JsonResponse({"code": 400, "msg": "书名不能为空"}, status=400)

        books = FalooBook.objects.filter(title__icontains=book_name)
        if not books.exists():
            return JsonResponse({"code": 404, "msg": "未找到包含该书名的书籍"}, status=404)

        target_book = books.first()

        similar_books = FalooBook.objects.filter(
            main_category=target_book.main_category
        ).exclude(book_id=target_book.book_id).order_by('-read_count')[:10]

        data = []
        for i, book in enumerate(similar_books):
            similarity = 1.0 - (i * 0.05)
            data.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "cover_url": book.cover_url,
                "similarity": similarity,
                "intro": book.introduction[:50] + "..." if book.introduction else "暂无简介"
            })

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def book_recommend_by_category(request):
    """
    基于分类的推荐接口
    GET: 根据分类推荐优质书籍
    URL: /api/recommend/category/?categories=同人小说,玄幻奇幻
    """
    try:
        categories_str = request.GET.get('categories', '')
        if not categories_str:
            return JsonResponse({"code": 400, "msg": "分类不能为空"}, status=400)

        categories = categories_str.split(',')

        books = FalooBook.objects.filter(
            main_category__in=categories
        ).order_by('-read_count', '-word_count')[:10]

        data = []
        for i, book in enumerate(books):
            data.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "cover_url": book.cover_url,
                "read_count": book.read_count,
                "sub_category": book.sub_category,
                "intro": book.introduction[:50] + "..." if book.introduction else "暂无简介"
            })

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def book_recommend_by_bookshelf(request):
    """
    基于书架的推荐接口
    GET: 根据用户书架推荐相似书籍
    URL: /api/recommend/bookshelf/?user_id=1
    """
    try:
        user_id = request.GET.get('user_id', '')
        if not user_id:
            return JsonResponse({"code": 400, "msg": "用户ID不能为空"}, status=400)

        cache_key = CacheManager.get_bookshelf_recommend_key(user_id)
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data}, safe=False)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)

        # 从新的书架表获取数据
        bookshelf_items = UserBookshelf.objects.filter(user=user).order_by('sort_order')
        bookshelf_data = [item.book_id for item in bookshelf_items]
        
        if not bookshelf_data:
            return JsonResponse({"code": 400, "msg": "书架为空"}, status=400)

        import torch
        import pickle
        import os

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(base_dir, 'model_output')
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        vector_path = os.path.join(model_dir, 'vectors.pt')

        if not os.path.exists(metadata_path) or not os.path.exists(vector_path):
            shelf_books = FalooBook.objects.filter(book_id__in=bookshelf_data)
            if not shelf_books.exists():
                return JsonResponse({"code": 404, "msg": "书架中没有找到书籍"}, status=404)

            categories = set()
            for book in shelf_books:
                categories.add(book.main_category)

            if categories:
                recommended_books = FalooBook.objects.filter(
                    main_category__in=categories
                ).exclude(book_id__in=bookshelf_data).order_by('-read_count')[:10]
            else:
                recommended_books = FalooBook.objects.exclude(
                    book_id__in=bookshelf_data
                ).order_by('-read_count')[:10]

            data = []
            for i, book in enumerate(recommended_books):
                data.append({
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": book.cover_url,
                    "monthly_read": book.monthly_read,
                    "total_flowers": book.total_flowers,
                    "monthly_flowers": book.monthly_flowers,
                    "introduction": book.introduction
                })
        else:
            # 加载新模型
            with open(metadata_path, 'rb') as f:
                meta = pickle.load(f)
            vectors = torch.load(vector_path, map_location='cpu')
            
            titles = meta['titles']
            book_features = (vectors['sem'] + vectors['attr']) / 2

            shelf_books = FalooBook.objects.filter(book_id__in=bookshelf_data)
            book_titles = [book.title for book in shelf_books]

            # 寻找匹配的索引
            target_idxs = [i for i, t in enumerate(titles) if t in book_titles]
            
            if not target_idxs:
                categories = set()
                for book in shelf_books:
                    categories.add(book.main_category)

                if categories:
                    recommended_books = FalooBook.objects.filter(
                        main_category__in=categories
                    ).exclude(book_id__in=bookshelf_data).order_by('-read_count')[:20]
                else:
                    recommended_books = FalooBook.objects.exclude(
                        book_id__in=bookshelf_data
                    ).order_by('-read_count')[:20]

                data = []
                for i, book in enumerate(recommended_books):
                    data.append({
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "cover_url": book.cover_url,
                        "monthly_read": book.monthly_read,
                        "total_flowers": book.total_flowers,
                        "monthly_flowers": book.monthly_flowers,
                        "introduction": book.introduction
                    })
            else:
                # 计算输入书籍的平均特征向量
                query_vec = book_features[target_idxs].mean(dim=0, keepdim=True)
                
                # 计算余弦相似度
                scores = torch.cosine_similarity(query_vec, book_features)
                
                # 排除掉输入的书本身
                for idx in target_idxs:
                    scores[idx] = -1.0
                
                # 提取 Top K
                vals, idxs = torch.topk(scores, min(25, len(titles)))

                data = []
                count = 0
                found_titles = [titles[idx] for idx in target_idxs]
                
                for i, idx in enumerate(idxs):
                    target_title = titles[idx.item()]

                    if target_title in found_titles:
                        continue

                    book = FalooBook.objects.filter(title=target_title).first()
                    if not book:
                        continue

                    count += 1
                    data.append({
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "cover_url": book.cover_url,
                        "monthly_read": book.monthly_read,
                        "total_flowers": book.total_flowers,
                        "monthly_flowers": book.monthly_flowers,
                        "introduction": book.introduction
                    })

                    if count >= 20:
                        break

        CacheManager.set(cache_key, data, 600)

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def hot_books(request):
    """
    热门书籍接口
    GET: 返回按阅读量排序的热门书籍
    URL: /api/hot/
    """
    try:
        cache_key = CacheManager.get_hot_books_key()
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data}, safe=False)

        books = FalooBook.objects.order_by('-read_count')[:20]

        data = []
        for i, book in enumerate(books):
            data.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "cover_url": book.cover_url,
                "monthly_read": book.monthly_read,
                "total_flowers": book.total_flowers,
                "monthly_flowers": book.monthly_flowers,
                "introduction": book.introduction
            })

        CacheManager.set(cache_key, data, 300)

        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


@csrf_exempt
def admin_users(request):
    """
    管理员管理用户接口
    GET: 获取用户列表
    URL: /api/admin/users/
    """
    if request.method == 'GET':
        try:
            users = User.objects.all()
            data = []
            for user in users:
                # 从新的书架表获取数据
                bookshelf_items = UserBookshelf.objects.filter(user=user).order_by('sort_order')
                bookshelf = [item.book_id for item in bookshelf_items]
                
                data.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "avatar": user.avatar,
                    "bookshelf": bookshelf
                })
            return JsonResponse({"code": 200, "msg": "success", "data": data})

        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


@csrf_exempt
def admin_user_detail(request, user_id):
    """
    管理员管理用户详情接口
    PUT: 更新用户
    DELETE: 删除用户
    URL: /api/admin/users/<user_id>/
    """
    if request.method == 'PUT':
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'bookshelf' in data:
                # 从新的书架表更新数据
                UserBookshelf.objects.filter(user=user).delete()
                if isinstance(data['bookshelf'], str):
                    bookshelf_list = [item.strip() for item in data['bookshelf'].split(',') if item.strip()]
                elif isinstance(data['bookshelf'], list):
                    bookshelf_list = data['bookshelf']
                else:
                    bookshelf_list = []
                
                for i, book_id in enumerate(bookshelf_list):
                    UserBookshelf.objects.create(
                        user=user,
                        book_id=book_id,
                        sort_order=i
                    )

            user.save()
            return JsonResponse({"code": 200, "msg": "更新成功"})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'DELETE':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({"code": 200, "msg": "删除成功"})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持PUT和DELETE请求"}, status=405)


@csrf_exempt
def user_rating(request):
    """
    用户评分接口
    POST: 提交或更新评分
    GET: 获取用户的所有评分
    URL: /api/user/rating/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            book_id = data.get('book_id')
            score = data.get('score')

            if not user_id or not book_id or score is None:
                return JsonResponse({"code": 400, "msg": "用户ID、书籍ID和评分不能为空"}, status=400)

            if score < 0.5 or score > 10:
                return JsonResponse({"code": 400, "msg": "评分必须在0.5到10之间"}, status=400)

            user = User.objects.get(id=user_id)
            rating, created = Rating.objects.get_or_create(
                user=user,
                book_id=book_id,
                defaults={'score': score}
            )

            if not created:
                rating.score = score
                rating.save()

            CacheManager.delete(CacheManager.get_book_detail_key(book_id))

            return JsonResponse({"code": 200, "msg": "评分成功", "data": {"score": rating.score}})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            if not user_id:
                return JsonResponse({"code": 400, "msg": "用户ID不能为空"}, status=400)

            user = User.objects.get(id=user_id)
            ratings = Rating.objects.filter(user=user)

            data = []
            for rating in ratings:
                try:
                    book = FalooBook.objects.get(book_id=rating.book_id)
                    book_info = {
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "cover_url": book.cover_url
                    }
                except FalooBook.DoesNotExist:
                    book_info = {
                        "book_id": rating.book_id,
                        "title": "未知书籍",
                        "author": "",
                        "cover_url": ""
                    }

                data.append({
                    "id": rating.id,
                    "book": book_info,
                    "score": rating.score,
                    "created_at": rating.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": rating.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return JsonResponse({"code": 200, "msg": "success", "data": data})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持POST和GET请求"}, status=405)


@csrf_exempt
def user_rating_detail(request, rating_id):
    """
    用户评分详情接口
    GET: 获取单个评分
    PUT: 更新评分
    DELETE: 删除评分
    URL: /api/user/rating/<rating_id>/
    """
    if request.method == 'GET':
        try:
            rating = Rating.objects.get(id=rating_id)

            try:
                book = FalooBook.objects.get(book_id=rating.book_id)
                book_info = {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": book.cover_url
                }
            except FalooBook.DoesNotExist:
                book_info = {
                    "book_id": rating.book_id,
                    "title": "未知书籍",
                    "author": "",
                    "cover_url": ""
                }

            data = {
                "id": rating.id,
                "user_id": rating.user.id,
                "book": book_info,
                "score": rating.score,
                "created_at": rating.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": rating.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }

            return JsonResponse({"code": 200, "msg": "success", "data": data})

        except Rating.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "评分不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'PUT':
        try:
            rating = Rating.objects.get(id=rating_id)
            data = json.loads(request.body)
            score = data.get('score')

            if score is None:
                return JsonResponse({"code": 400, "msg": "评分不能为空"}, status=400)

            if score < 0.5 or score > 10:
                return JsonResponse({"code": 400, "msg": "评分必须在0.5到10之间"}, status=400)

            rating.score = score
            rating.save()

            CacheManager.delete(CacheManager.get_book_detail_key(rating.book_id))

            return JsonResponse({"code": 200, "msg": "更新成功", "data": {"score": rating.score}})

        except Rating.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "评分不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    elif request.method == 'DELETE':
        try:
            rating = Rating.objects.get(id=rating_id)
            book_id = rating.book_id
            rating.delete()

            CacheManager.delete(CacheManager.get_book_detail_key(book_id))

            return JsonResponse({"code": 200, "msg": "删除成功"})

        except Rating.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "评分不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)

    else:
        return JsonResponse({"code": 405, "msg": "只支持GET、PUT和DELETE请求"}, status=405)


def book_rating(request, book_id):
    """
    获取书籍的平均评分
    GET: 获取书籍的平均评分
    URL: /api/book/rating/<book_id>/
    """
    try:
        ratings = Rating.objects.filter(book_id=book_id)
        if not ratings.exists():
            return JsonResponse({"code": 200, "msg": "success", "data": {"average_score": 0, "count": 0}})

        total_score = sum([float(rating.score) for rating in ratings])
        average_score = total_score / len(ratings)

        return JsonResponse({"code": 200, "msg": "success", "data": {
            "average_score": round(average_score, 1),
            "count": len(ratings)
        }})

    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


def cache_warmup(request):
    """
    缓存预热接口
    GET: 预热常用缓存
    URL: /api/cache/warmup/
    """
    try:
        CacheManager.warm_up_cache()
        return JsonResponse({"code": 200, "msg": "缓存预热成功"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"缓存预热失败: {str(e)}"}, status=500)


def cache_clear(request):
    """
    缓存清除接口
    GET: 清除所有缓存
    URL: /api/cache/clear/
    """
    try:
        CacheManager.delete_pattern("*")
        return JsonResponse({"code": 200, "msg": "缓存清除成功"})
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"缓存清除失败: {str(e)}"}, status=500)


def book_recommend_you_may_like(request):
    """
    猜你喜欢推荐接口
    GET: 返回猜你喜欢的书籍列表
    URL: /api/recommend/you_may_like/
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        # 生成缓存键
        cache_key = "recommend:you_may_like"
        
        # 尝试从缓存获取数据
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            logger.info("猜你喜欢: 来自缓存")
            return JsonResponse({"code": 200, "msg": "success", "data": cached_data}, safe=False)
        
        # 缓存失效，生成推荐结果
        logger.info("猜你喜欢: 重新生成")
        
        # 这里可以根据实际情况实现推荐算法
        # 示例：返回阅读量较高的书籍
        books = FalooBook.objects.order_by('-read_count')[:20]
        
        data = []
        for i, book in enumerate(books):
            data.append({
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "cover_url": book.cover_url,
                "category": book.main_category,
                "sub_category": book.sub_category,
                "read_count": book.read_count,
                "monthly_read": book.monthly_read,
                "total_read": book.total_read,
                "monthly_flowers": book.monthly_flowers,
                "total_flowers": book.total_flowers,
                "word_count": book.word_count,
                "introduction": book.introduction[:60] + "..." if book.introduction else "暂无简介",
                "update_time": book.update_time,
                "tags": book.tags
            })
        
        # 将结果存入缓存，有效期2小时（7200秒）
        CacheManager.set(cache_key, data, 7200)
        
        return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)
        
    except Exception as e:
        return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)


@csrf_exempt
def user_profile(request, user_id):
    """
    用户个人信息更新接口
    PUT: 更新用户个人信息
    URL: /api/user/profile/<user_id>/
    """
    if request.method == 'PUT':
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']

            user.save()

            return JsonResponse({"code": 200, "msg": "更新成功", "data": {"username": user.username, "email": user.email, "avatar": user.avatar}})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持PUT请求"}, status=405)


@csrf_exempt
def user_password(request, user_id):
    """
    用户密码更新接口
    PUT: 更新用户密码
    URL: /api/user/password/<user_id>/
    """
    if request.method == 'PUT':
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if not old_password or not new_password:
                return JsonResponse({"code": 400, "msg": "旧密码和新密码不能为空"}, status=400)

            if not user.check_password(old_password):
                return JsonResponse({"code": 400, "msg": "旧密码错误"}, status=400)

            user.set_password(new_password)
            user.save()

            return JsonResponse({"code": 200, "msg": "密码更新成功"})

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持PUT请求"}, status=405)


@csrf_exempt
def user_avatar(request, user_id):
    """
    用户头像更新接口
    POST: 更新用户头像
    URL: /api/user/avatar/<user_id>/
    """
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            
            if request.FILES.get('avatar'):
                file = request.FILES['avatar']
                
                # 1. 物理保存文件到 media/avatars/
                # 生成文件名防止重复，例如: user_1_avatar.jpg
                ext = os.path.splitext(file.name)[1]
                file_name = f"user_{user_id}{ext}"
                file_path = os.path.join('avatars', file_name)
                
                # 如果文件已存在则先删除，确保更新
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                
                # 保存文件
                saved_path = default_storage.save(file_path, file)
                
                # 2. 更新数据库中的路径 (存入相对路径，例如 /media/avatars/user_1.jpg)
                user.avatar = f"{settings.MEDIA_URL}{saved_path}"
                user.save()

                return JsonResponse({
                    "code": 200,
                    "msg": "头像更新成功",
                    "data": {
                        # 确保这里返回的是可以被前端 img 标签直接识别的 URL
                        "avatar": user.avatar if isinstance(user.avatar, str) else user.avatar.url
                    }
                })
            else:
                return JsonResponse({"code": 400, "msg": "未检测到上传文件，请检查表单 Key 是否为 avatar"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    
    return JsonResponse({"code": 405, "msg": "请使用 POST 方法上传"}, status=405)


@csrf_exempt
@admin_required
def crawler_start(request):
    """
    启动爬虫脚本接口
    POST: 接收页码参数或book_id参数，启动爬虫脚本
    URL: /api/admin/crawler/start/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            start_page = data.get('start_page', 81)
            end_page = data.get('end_page', 101)
            
            # Generate task ID
            task_id = f"crawler_{int(time.time())}"
            
            # Check if script exists
            if not os.path.exists(CRAWLER_SCRIPT):
                return JsonResponse({"code": 404, "msg": f"爬虫脚本不存在: {CRAWLER_SCRIPT}"}, status=404)
            
            # Start subprocess based on parameters
            if book_id:
                # Run with --bookid parameter
                process = subprocess.Popen(
                    ['python', CRAWLER_SCRIPT, '--bookid', str(book_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False
                )
            else:
                # Run with --pages parameter
                process = subprocess.Popen(
                    ['python', CRAWLER_SCRIPT, '--pages', str(start_page), str(end_page)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False
                )
            
            # Store process information
            task_processes[task_id] = process
            task_status[task_id] = 'running'
            
            # Start thread to capture output
            threading.Thread(target=capture_process_output, args=(process, task_id), daemon=True).start()
            
            return JsonResponse({"code": 200, "msg": "爬虫脚本已启动", "data": {"task_id": task_id}})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
@admin_required
def crawler_import(request):
    """
    启动导入脚本接口
    POST: 启动导入到数据库脚本
    URL: /api/admin/crawler/import/
    """
    if request.method == 'POST':
        try:
            # Generate task ID
            task_id = f"import_{int(time.time())}"
            
            # Check if script exists
            if not os.path.exists(IMPORT_SCRIPT):
                return JsonResponse({"code": 404, "msg": f"导入脚本不存在: {IMPORT_SCRIPT}"}, status=404)
            
            # Start subprocess
            process = subprocess.Popen(
                ['python', IMPORT_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Store process information
            task_processes[task_id] = process
            task_status[task_id] = 'running'
            
            # Start thread to capture output
            threading.Thread(target=capture_process_output, args=(process, task_id), daemon=True).start()
            
            return JsonResponse({"code": 200, "msg": "导入脚本已启动", "data": {"task_id": task_id}})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@admin_required
def crawler_logs(request):
    """
    获取任务日志接口
    GET: 获取指定任务的日志
    URL: /api/admin/crawler/logs/?task_id=xxx
    """
    if request.method == 'GET':
        try:
            task_id = request.GET.get('task_id')
            if not task_id:
                return JsonResponse({"code": 400, "msg": "任务ID不能为空"}, status=400)
            
            logs = task_logs.get(task_id, [])
            status = task_status.get(task_id, 'not_found')
            
            return JsonResponse({"code": 200, "msg": "success", "data": {
                "logs": logs,
                "status": status
            }})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


@csrf_exempt
@admin_required
def crawler_stop(request):
    """
    停止爬虫任务接口
    POST: 停止指定的爬虫任务
    URL: /api/admin/crawler/stop/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            
            if not task_id:
                return JsonResponse({"code": 400, "msg": "任务ID不能为空"}, status=400)
            
            # Kill the process if it exists
            if task_id in task_processes:
                process = task_processes[task_id]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                task_processes.pop(task_id, None)
                task_status[task_id] = 'stopped'
                
                add_log = task_logs.get(task_id, [])
                add_log.append("任务已被用户停止")
                task_logs[task_id] = add_log
                
                return JsonResponse({"code": 200, "msg": "任务已停止"})
            else:
                return JsonResponse({"code": 404, "msg": "任务不存在或已结束"}, status=404)
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@admin_required
def check_status(request):
    """
    检查任务状态接口
    GET: 检查是否有正在运行的任务
    URL: /api/admin/check_status/
    """
    if request.method == 'GET':
        try:
            running_tasks = []
            
            for task_id, process in task_processes.items():
                task_type = 'crawler' if 'crawler' in task_id else 'import'
                running_tasks.append({
                    'task_id': task_id,
                    'type': task_type,
                    'status': task_status.get(task_id, 'running')
                })
            
            return JsonResponse({"code": 200, "msg": "success", "data": {
                "running_tasks": running_tasks
            }})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


@csrf_exempt
def user_action(request):
    """
    用户行为反馈接口
    POST: 记录用户的收藏和不感兴趣行为，并提供实时补偿推荐
    URL: /api/user/action/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            book_id = data.get('book_id')
            action_type = data.get('action_type')
            
            # 验证参数
            if not user_id or not book_id or not action_type:
                return JsonResponse({"code": 400, "msg": "用户ID、书籍ID和行为类型不能为空"}, status=400)
            
            # 验证行为类型
            if action_type not in ['like', 'dislike']:
                return JsonResponse({"code": 400, "msg": "行为类型必须是like或dislike"}, status=400)
            
            # 验证用户是否存在
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
            
            # 验证书籍是否存在
            try:
                book = FalooBook.objects.get(book_id=book_id)
            except FalooBook.DoesNotExist:
                return JsonResponse({"code": 404, "msg": "书籍不存在"}, status=404)
            
            # 检查是否已经存在相同的行为记录
            existing_action = UserActionLog.objects.filter(
                user=user,
                book_id=book_id,
                action_type=action_type
            ).first()
            
            if existing_action:
                return JsonResponse({"code": 200, "msg": "行为记录已存在"})
            
            # 创建新的行为记录
            UserActionLog.objects.create(
                user=user,
                book_id=book_id,
                action_type=action_type
            )
            
            # 实时补偿推荐
            compensation_recommendations = []
            
            if action_type == 'like':
                # 当用户收藏时，基于当前书籍的向量推荐相似书籍
                import torch
                import pickle
                import os
                
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                metadata_file = os.path.join(base_dir, 'model_metadata_advanced.pkl')
                vector_file = os.path.join(base_dir, 'book_vectors_advanced.pt')
                
                if os.path.exists(metadata_file) and os.path.exists(vector_file):
                    # 加载模型和向量
                    with open(metadata_file, 'rb') as f:
                        metadata = pickle.load(f)
                    df = metadata['df']
                    book_vectors = torch.load(vector_file)
                    
                    # 找到当前书籍在数据框中的索引
                    match = df[df['title'] == book.title]
                    if not match.empty:
                        # 获取当前书籍的向量
                        book_idx = match.index[0]
                        book_vector = book_vectors[book_idx].unsqueeze(0)
                        
                        # 计算余弦相似度
                        sims = torch.mm(book_vector, book_vectors.t()).squeeze(0)
                        scores, indices = torch.topk(sims, k=min(50, len(df)))
                        
                        # 收集用户已读/已收藏的书籍ID
                        user_books = set()
                        # 已收藏的书籍
                        liked_books = UserActionLog.objects.filter(user=user, action_type='like')
                        for liked_book in liked_books:
                            user_books.add(liked_book.book_id)
                        # 已加入书架的书籍
                        bookshelf_books = UserBookshelf.objects.filter(user=user)
                        for shelf_book in bookshelf_books:
                            user_books.add(shelf_book.book_id)
                        
                        # 生成推荐结果
                        count = 0
                        for i in range(len(indices)):
                            res_idx = indices[i].item()
                            target_title = df.iloc[res_idx]['title']
                            
                            recommended_book = FalooBook.objects.filter(title=target_title).first()
                            if not recommended_book:
                                continue
                            
                            # 确保推荐的书籍用户未读过
                            if recommended_book.book_id not in user_books and recommended_book.book_id != book_id:
                                compensation_recommendations.append({
                                    "book_id": recommended_book.book_id,
                                    "title": recommended_book.title,
                                    "author": recommended_book.author,
                                    "cover_url": recommended_book.cover_url,
                                    "category": recommended_book.main_category,
                                    "sub_category": recommended_book.sub_category,
                                    "read_count": recommended_book.read_count,
                                    "monthly_read": recommended_book.monthly_read,
                                    "total_read": recommended_book.total_read,
                                    "monthly_flowers": recommended_book.monthly_flowers,
                                    "total_flowers": recommended_book.total_flowers,
                                    "word_count": recommended_book.word_count,
                                    "introduction": recommended_book.introduction[:60] + "..." if recommended_book.introduction else "暂无简介",
                                    "update_time": recommended_book.update_time,
                                    "tags": recommended_book.tags,
                                    "recommendation_reason": "基于您的收藏推荐"
                                })
                                count += 1
                                if count >= 3:
                                    break
            elif action_type == 'dislike':
                # 当用户不喜欢时，从缓存中剔除同类型特征的小说
                # 这里可以实现缓存剔除逻辑
                # 例如，使用Redis缓存，删除同类型的推荐
                pass
            
            return JsonResponse({"code": 200, "msg": "行为记录成功", "compensation_recommendations": compensation_recommendations})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)


@csrf_exempt
def user_actions(request):
    """
    获取用户行为记录接口
    GET: 获取用户的收藏和不感兴趣书籍
    URL: /api/user/actions/
    """
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            action_type = request.GET.get('action_type')  # 可选参数：like或dislike
            
            # 验证参数
            if not user_id:
                return JsonResponse({"code": 400, "msg": "用户ID不能为空"}, status=400)
            
            # 验证用户是否存在
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
            
            # 构建查询
            query = UserActionLog.objects.filter(user=user)
            if action_type:
                if action_type not in ['like', 'dislike']:
                    return JsonResponse({"code": 400, "msg": "行为类型必须是like或dislike"}, status=400)
                query = query.filter(action_type=action_type)
            
            # 执行查询并获取结果
            actions = query.order_by('-created_at')
            
            # 构建响应数据
            result = []
            for action in actions:
                try:
                    book = FalooBook.objects.get(book_id=action.book_id)
                    result.append({
                        'id': action.id,
                        'book_id': book.book_id,
                        'title': book.title,
                        'author': book.author,
                        'cover_url': book.cover_url,
                        'created_at': action.created_at.isoformat()
                    })
                except FalooBook.DoesNotExist:
                    # 书籍不存在时跳过
                    pass
            
            return JsonResponse({"code": 200, "data": result})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


@csrf_exempt
def get_user_profile(request):
    """
    获取用户个人资料和阅读基因接口
    GET: 获取用户的历史阅读倾向和阅读基因
    URL: /api/user/profile/stats/
    """
    if request.method == 'GET':
        try:
            user_id = request.GET.get('user_id')
            
            # 验证参数
            if not user_id:
                return JsonResponse({"code": 400, "msg": "用户ID不能为空"}, status=400)
            
            # 验证用户是否存在
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"code": 404, "msg": "用户不存在"}, status=404)
            
            # 统计用户的历史阅读倾向
            # 1. 收集用户的阅读记录（收藏的书籍）
            liked_books = UserActionLog.objects.filter(user=user, action_type='like')
            bookshelf_books = UserBookshelf.objects.filter(user=user)
            
            # 收集所有书籍ID
            book_ids = set()
            for book in liked_books:
                book_ids.add(book.book_id)
            for book in bookshelf_books:
                book_ids.add(book.book_id)
            
            # 2. 统计各类别占比
            category_count = {}
            word_count_ranges = {
                'short': 0,  # < 50万
                'medium': 0,  # 50万-150万
                'long': 0,  # > 150万
            }
            total_books = 0
            
            for book_id in book_ids:
                try:
                    book = FalooBook.objects.get(book_id=book_id)
                    total_books += 1
                    
                    # 统计类别
                    category = book.main_category
                    if category not in category_count:
                        category_count[category] = 0
                    category_count[category] += 1
                    
                    # 统计字数区间
                    word_count = book.word_count or 0
                    if word_count < 500000:
                        word_count_ranges['short'] += 1
                    elif word_count < 1500000:
                        word_count_ranges['medium'] += 1
                    else:
                        word_count_ranges['long'] += 1
                except FalooBook.DoesNotExist:
                    pass
            
            # 3. 计算各类别占比
            category_percentage = {}
            for category, count in category_count.items():
                category_percentage[category] = round((count / total_books) * 100, 2) if total_books > 0 else 0
            
            # 4. 计算平均阅读频率（这里简化处理，使用收藏书籍的数量除以用户注册天数）
            import datetime
            days_since_creation = (datetime.datetime.now().date() - user.date_joined.date()).days
            days_since_creation = max(1, days_since_creation)  # 避免除零
            avg_reading_frequency = round(total_books / days_since_creation, 2)
            
            # 5. 生成阅读基因（这里使用模拟数据，实际项目中可以根据书籍内容分析）
            reading_gene = {
                '玄幻度': 0,
                '情感度': 0,
                '逻辑性': 0,
                '热血度': 0,
                '科技感': 0,
                '历史感': 0,
            }
            
            # 根据书籍类别设置阅读基因
            for category, percentage in category_percentage.items():
                if '玄幻' in category or '奇幻' in category:
                    reading_gene['玄幻度'] += percentage * 0.8
                if '言情' in category or '都市' in category:
                    reading_gene['情感度'] += percentage * 0.8
                if '推理' in category or '悬疑' in category:
                    reading_gene['逻辑性'] += percentage * 0.8
                if '武侠' in category or '仙侠' in category:
                    reading_gene['热血度'] += percentage * 0.8
                if '科幻' in category or '网游' in category:
                    reading_gene['科技感'] += percentage * 0.8
                if '历史' in category:
                    reading_gene['历史感'] += percentage * 0.8
            
            # 归一化阅读基因，确保每个维度在0-100之间
            for key in reading_gene:
                reading_gene[key] = min(100, max(0, reading_gene[key]))
            
            # 6. 构建响应数据
            data = {
                'user_info': {
                    'username': user.username,
                    'email': user.email,
                    'avatar': user.avatar,
                    'joined_date': user.date_joined.isoformat(),
                },
                'reading_stats': {
                    'total_books': total_books,
                    'category_percentage': category_percentage,
                    'word_count_ranges': word_count_ranges,
                    'avg_reading_frequency': avg_reading_frequency,
                },
                'reading_gene': reading_gene,
            }
            
            return JsonResponse({"code": 200, "data": data})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持GET请求"}, status=405)


@csrf_exempt
def user_action_delete(request, action_id):
    """
    删除用户行为记录接口
    DELETE: 删除用户的收藏或不感兴趣记录
    URL: /api/user/action/<action_id>/
    """
    if request.method == 'DELETE':
        try:
            # 验证行为记录是否存在
            try:
                action = UserActionLog.objects.get(id=action_id)
            except UserActionLog.DoesNotExist:
                return JsonResponse({"code": 404, "msg": "行为记录不存在"}, status=404)
            
            # 删除行为记录
            action.delete()
            
            return JsonResponse({"code": 200, "msg": "删除成功"})
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持DELETE请求"}, status=405)


@csrf_exempt
def post_interests(request):
    """
    兴趣标签提交接口
    POST: 接收用户选择的兴趣标签，返回推荐书籍
    URL: /api/interests/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tags = data.get('tags', [])
            user_id = data.get('user_id')
            
            # 验证标签数量
            if len(tags) < 3 or len(tags) > 5:
                return JsonResponse({"code": 400, "msg": "请选择3-5个标签"}, status=400)
            
            # 获取用户标记为不感兴趣的书籍ID列表
            disliked_book_ids = []
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    disliked_actions = UserActionLog.objects.filter(user=user, action_type='dislike')
                    disliked_book_ids = [action.book_id for action in disliked_actions]
                except User.DoesNotExist:
                    pass
            
            # 集成BERT模型计算标签组合的语义向量
            import torch
            import pickle
            import os
            
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(base_dir, 'model_output')
            metadata_path = os.path.join(model_dir, 'metadata.pkl')
            vector_path = os.path.join(model_dir, 'vectors.pt')
            
            if not os.path.exists(metadata_path) or not os.path.exists(vector_path):
                # 如果模型文件不存在，返回基于阅读量的推荐
                books = FalooBook.objects.exclude(book_id__in=disliked_book_ids).order_by('-read_count')[:16]
                
                data = []
                for i, book in enumerate(books):
                    data.append({
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "cover_url": book.cover_url,
                        "category": book.main_category,
                        "sub_category": book.sub_category,
                        "read_count": book.read_count,
                        "monthly_read": book.monthly_read,
                        "total_read": book.total_read,
                        "monthly_flowers": book.monthly_flowers,
                        "total_flowers": book.total_flowers,
                        "word_count": book.word_count,
                        "introduction": book.introduction[:60] + "..." if book.introduction else "暂无简介",
                        "update_time": book.update_time,
                        "tags": book.tags
                    })
            else:
                # 加载新模型
                with open(metadata_path, 'rb') as f:
                    meta = pickle.load(f)
                vectors = torch.load(vector_path, map_location='cpu')
                
                titles = meta['titles']
                book_features = (vectors['sem'] + vectors['attr']) / 2
                
                # 计算标签组合的语义向量
                # 这里使用一个简单的方法：找到包含这些标签的书籍，取它们的向量平均值
                # 实际项目中可以使用BERT模型对标签进行编码
                
                # 收集包含任何一个标签的书籍标题
                matching_titles = []
                for tag in tags:
                    # 查找标题中包含标签的书籍
                    tag_books = FalooBook.objects.filter(title__icontains=tag)[:10]
                    matching_titles.extend([book.title for book in tag_books])
                
                # 去重
                matching_titles = list(set(matching_titles))
                
                # 计算标签向量
                tag_vectors = []
                for title in matching_titles:
                    if title in titles:
                        idx = titles.index(title)
                        tag_vectors.append(book_features[idx])
                
                if tag_vectors:
                    # 计算标签向量的平均值
                    tag_vector = torch.stack(tag_vectors).mean(dim=0).unsqueeze(0)
                    
                    # 计算余弦相似度
                    scores = torch.cosine_similarity(tag_vector, book_features)
                    
                    # 提取 Top K（多取一些以过滤不感兴趣的书籍）
                    vals, idxs = torch.topk(scores, min(50, len(titles)))
                    
                    # 生成推荐结果
                    data = []
                    count = 0
                    for i, idx in enumerate(idxs):
                        target_title = titles[idx.item()]
                        
                        book = FalooBook.objects.filter(title=target_title).first()
                        if not book:
                            continue
                        
                        # 过滤掉用户标记为不感兴趣的书籍
                        if book.book_id in disliked_book_ids:
                            continue
                        
                        count += 1
                        data.append({
                            "book_id": book.book_id,
                            "title": book.title,
                            "author": book.author,
                            "cover_url": book.cover_url,
                            "category": book.main_category,
                            "sub_category": book.sub_category,
                            "read_count": book.read_count,
                            "monthly_read": book.monthly_read,
                            "total_read": book.total_read,
                            "monthly_flowers": book.monthly_flowers,
                            "total_flowers": book.total_flowers,
                            "word_count": book.word_count,
                            "introduction": book.introduction[:60] + "..." if book.introduction else "暂无简介",
                            "update_time": book.update_time,
                            "tags": book.tags
                        })
                        
                        if count >= 16:
                            break
                else:
                    # 如果没有找到匹配的标签，返回基于阅读量的推荐
                    books = FalooBook.objects.exclude(book_id__in=disliked_book_ids).order_by('-read_count')[:16]
                    
                    data = []
                    for i, book in enumerate(books):
                        data.append({
                            "book_id": book.book_id,
                            "title": book.title,
                            "author": book.author,
                            "cover_url": book.cover_url,
                            "category": book.main_category,
                            "sub_category": book.sub_category,
                            "read_count": book.read_count,
                            "monthly_read": book.monthly_read,
                            "total_read": book.total_read,
                            "monthly_flowers": book.monthly_flowers,
                            "total_flowers": book.total_flowers,
                            "word_count": book.word_count,
                            "introduction": book.introduction[:60] + "..." if book.introduction else "暂无简介",
                            "update_time": book.update_time,
                            "tags": book.tags
                        })
            
            return JsonResponse({"code": 200, "msg": "success", "data": data}, safe=False)
            
        except Exception as e:
            return JsonResponse({"code": 500, "msg": f"服务器错误: {str(e)}"}, status=500)
    else:
        return JsonResponse({"code": 405, "msg": "只支持POST请求"}, status=405)
