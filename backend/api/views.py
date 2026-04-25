from django.http import JsonResponse
from .models import FalooBook, Admin, User, Rating, UserBookshelf
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .cache_utils import CacheManager
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage

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
        metadata_file = os.path.join(base_dir, 'model_metadata_advanced.pkl')
        vector_file = os.path.join(base_dir, 'book_vectors_advanced.pt')

        if not os.path.exists(metadata_file) or not os.path.exists(vector_file):
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
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            df = metadata['df']
            encoders = metadata['encoders']
            book_vectors = torch.load(vector_file)

            shelf_books = FalooBook.objects.filter(book_id__in=bookshelf_data)
            book_titles = [book.title for book in shelf_books]

            selected_vecs = []
            found_titles = []

            for title in book_titles:
                match = df[df['title'].str.contains(title, na=False)]
                if not match.empty:
                    idx = match.index[0]
                    selected_vecs.append(book_vectors[idx])
                    found_titles.append(df.iloc[idx]['title'])

            if not selected_vecs:
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
                combined_vec = torch.stack(selected_vecs).mean(dim=0).unsqueeze(0)
                sims = torch.mm(combined_vec, book_vectors.t()).squeeze(0)
                scores, indices = torch.topk(sims, k=min(25, len(df)))

                data = []
                count = 0
                for i in range(len(indices)):
                    res_idx = indices[i].item()
                    target_title = df.iloc[res_idx]['title']

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
