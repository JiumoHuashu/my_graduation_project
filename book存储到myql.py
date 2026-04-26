# # 建表命令
# CREATE TABLE `faloo_books` (
#   `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
#   `book_id` varchar(20) NOT NULL COMMENT '书籍原始ID',
#   `title` varchar(255) NOT NULL COMMENT '书名',
#   `author` varchar(100) DEFAULT NULL COMMENT '作者',
#   `cover_url` varchar(500) DEFAULT NULL COMMENT '封面链接',
#   `onboarding_time` date DEFAULT NULL COMMENT '入站时间',
#   `update_time` varchar(50) DEFAULT NULL COMMENT '更新时间文本',
#   `main_category` varchar(50) DEFAULT NULL COMMENT '主分类',
#   `sub_category` varchar(50) DEFAULT NULL COMMENT '子分类',
#   `read_count` bigint(20) DEFAULT '0' COMMENT '总阅读数',
#   `word_count` bigint(20) DEFAULT '0' COMMENT '总字数',
#   `monthly_read` int(11) DEFAULT '0' COMMENT '月阅读数',
#   `monthly_flowers` int(11) DEFAULT '0' COMMENT '月鲜花数',
#   `total_read` bigint(20) DEFAULT '0' COMMENT '总统计阅读数',
#   `total_flowers` int(11) DEFAULT '0' COMMENT '总鲜花数',
#   `tags` varchar(500) DEFAULT NULL COMMENT '标签',
#   `introduction` text COMMENT '简介内容',
#   `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据抓取时间',
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `idx_book_id` (`book_id`) -- 唯一索引，防止重复导入同一本书
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

import os
import json
import pymysql

# --- 1. 数据库配置 (请根据你的实际情况修改) ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # 你的数据库用户名
    'password': '123456',   # 你的数据库密码
    'database': 'faloo_db', # 你的数据库名
    'charset': 'utf8mb4'
}

# 存放 JSON 的文件夹路径
JSON_DIR = "book"

def import_json_to_mysql():
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 统计数据
    success_count = 0
    fail_count = 0

    # 检查文件夹是否存在
    if not os.path.exists(JSON_DIR):
        print(f"错误：找不到文件夹 '{JSON_DIR}'")
        return

    print(f"开始从 {JSON_DIR} 文件夹导入数据...")

    # 遍历文件夹下所有 .json 文件
    for filename in os.listdir(JSON_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(JSON_DIR, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # SQL 插入语句 (对应你要求的表字段)
                sql = """
                INSERT INTO faloo_books (
                    book_id, title, author, cover_url, onboarding_time, 
                    update_time, main_category, sub_category, read_count, 
                    word_count, monthly_read, monthly_flowers, total_read, 
                    total_flowers, tags, introduction
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    title=VALUES(title),
                    update_time=VALUES(update_time),
                    read_count=VALUES(read_count),
                    total_read=VALUES(total_read);
                """
                
                # 数据清洗与转换
                # 注意：MySQL 的数字字段需要传入 int 或 float，防止字符串导致报错
                values = (
                    str(data.get('book_id')),
                    data.get('title'),
                    data.get('author'),
                    data.get('cover_url'),
                    data.get('onboarding_time', '2025-10-01'),
                    data.get('update_time'),
                    data.get('category', {}).get('main_category'),
                    data.get('category', {}).get('sub_category'),
                    int(data.get('read_count', 0)),
                    int(data.get('word_count', 0)),
                    int(data.get('monthly_stats', {}).get('monthly_read', 0)),
                    int(data.get('monthly_stats', {}).get('monthly_flowers', 0)),
                    int(data.get('total_stats', {}).get('total_read', 0)),
                    int(data.get('total_stats', {}).get('total_flowers', 0)),
                    data.get('tags'),
                    data.get('introduction')
                )
                
                cursor.execute(sql, values)
                success_count += 1
                
            except Exception as e:
                print(f"文件 {filename} 导入失败: {e}")
                fail_count += 1

    # 提交更改并关闭
    conn.commit()
    cursor.close()
    conn.close()
    
    print("-" * 30)
    print(f"导入完成！")
    print(f"成功导入: {success_count} 条")
    print(f"失败条数: {fail_count} 条")

if __name__ == "__main__":
    import_json_to_mysql()