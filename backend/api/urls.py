from django.urls import path
from api.views import book_rank_api, book_detail_api, admin_login, admin_books, admin_book_detail, user_register, user_login, user_bookshelf, user_bookshelf_remove, book_search, book_recommend, book_recommend_by_book, book_recommend_by_category, book_recommend_by_bookshelf, hot_books, admin_users, admin_user_detail, user_rating, user_rating_detail, book_rating, cache_warmup, cache_clear, user_profile, user_password, user_avatar

urlpatterns = [
    # 排行榜接口
    path('rank/', book_rank_api),
    # 书籍详情接口
    path('book/<str:book_id>/', book_detail_api),
    # 搜索接口
    path('search/', book_search),
    # 推荐接口
    path('recommend/', book_recommend),
    # 基于书名的推荐接口
    path('recommend/book/', book_recommend_by_book),
    # 基于分类的推荐接口
    path('recommend/category/', book_recommend_by_category),
    # 基于书架的推荐接口
    path('recommend/bookshelf/', book_recommend_by_bookshelf),
    # 热门书籍接口
    path('hot/', hot_books),
    # 管理员相关路由
    path('admin/login/', admin_login),
    path('admin/books/', admin_books),
    path('admin/books/<str:book_id>/', admin_book_detail),
    path('admin/users/', admin_users),
    path('admin/users/<int:user_id>/', admin_user_detail),
    # 用户相关路由
    path('user/register/', user_register),
    path('user/login/', user_login),
    path('user/bookshelf/', user_bookshelf),
    path('user/bookshelf/remove/', user_bookshelf_remove),
    # 评分相关路由
    path('user/rating/', user_rating),
    path('user/rating/<int:rating_id>/', user_rating_detail),
    path('book/rating/<str:book_id>/', book_rating),
    # 缓存相关路由
    path('cache/warmup/', cache_warmup),
    path('cache/clear/', cache_clear),
    # 用户个人信息相关路由
    path('user/profile/<int:user_id>/', user_profile),
    path('user/password/<int:user_id>/', user_password),
    path('user/avatar/<int:user_id>/', user_avatar),
]
