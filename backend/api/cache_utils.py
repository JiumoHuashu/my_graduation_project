import json
import hashlib
from django.core.cache import cache
from django.conf import settings


class CacheManager:
    @staticmethod
    def get_book_rank_key(category=None):
        if category:
            return f"book_rank:{category}"
        return "book_rank:all"

    @staticmethod
    def get_book_detail_key(book_id):
        return f"book_detail:{book_id}"

    @staticmethod
    def get_hot_books_key():
        return "hot_books"

    @staticmethod
    def get_recommend_key(main_category, sub_category):
        return f"recommend:{main_category}:{sub_category}"

    @staticmethod
    def get_search_key(keyword):
        keyword_hash = hashlib.md5(keyword.encode()).hexdigest()
        return f"search:{keyword_hash}"

    @staticmethod
    def get_bookshelf_recommend_key(user_id):
        return f"bookshelf_recommend:{user_id}"

    @staticmethod
    def get(cache_key, default=None):
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return default
        except Exception:
            return default

    @staticmethod
    def set(cache_key, data, timeout=None):
        try:
            if timeout is None:
                timeout = 300
            cache.set(cache_key, json.dumps(data), timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def delete(cache_key):
        try:
            cache.delete(cache_key)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_pattern(pattern):
        try:
            keys = cache.keys(f"*{pattern}*")
            for key in keys:
                cache.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def invalidate_book_cache(book_id=None):
        if book_id:
            CacheManager.delete(CacheManager.get_book_detail_key(book_id))
        CacheManager.delete(CacheManager.get_book_rank_key())
        CacheManager.delete(CacheManager.get_hot_books_key())
        CacheManager.delete_pattern("recommend")
        CacheManager.delete_pattern("search")

    @staticmethod
    def warm_up_cache():
        from api.models import FalooBook

        try:
            books = FalooBook.objects.order_by('-read_count')[:30]
            data = []
            for b in books:
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
            CacheManager.set(CacheManager.get_book_rank_key(), data, 300)

            hot_books = FalooBook.objects.order_by('-read_count')[:20]
            hot_data = []
            for i, book in enumerate(hot_books):
                hot_data.append({
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "cover_url": book.cover_url,
                    "monthly_read": book.monthly_read,
                    "total_flowers": book.total_flowers,
                    "monthly_flowers": book.monthly_flowers,
                    "introduction": book.introduction
                })
            CacheManager.set(CacheManager.get_hot_books_key(), hot_data, 300)

            return True
        except Exception:
            return False
