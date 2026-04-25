import torch
import pickle
import pandas as pd
import sys
import os

def load_resources():
    print("正在加载【高级版】推荐引擎资源...")
    metadata_file = 'model_metadata_advanced.pkl'
    vector_file = 'book_vectors_advanced.pt'
    
    if not os.path.exists(metadata_file) or not os.path.exists(vector_file):
        print("错误：未找到模型文件！请先确保运行了 1.py 训练脚本。")
        sys.exit()

    with open(metadata_file, 'rb') as f:
        metadata = pickle.load(f)
    return metadata['df'], metadata['encoders'], torch.load(vector_file)

def interactive_test():
    df, encoders, book_vectors = load_resources()
    main_categories = list(encoders['main_cat'].classes_)

    print("\n" + "★"*30)
    print("  飞卢小说深度语义推荐系统 (V2.0)  ")
    print("  已配置：简介+章节融合 / Top 10 推荐 ")
    print("★"*30)

    while True:
        print("\n[模式选择] 1.输入书名(找相似)  2.选择大类(找优质)  3.退出")
        choice = input("请选择操作编号: ").strip()
        
        if choice == '1':
            book_name = input("请输入您喜欢的书名: ").strip()
            match = df[df['title'].str.contains(book_name, na=False)]
            if match.empty:
                print(f"× 未找到包含《{book_name}》的书籍。")
                continue
            
            # 如果匹配到多本，默认选第一本
            idx = match.index[0]
            current_title = df.iloc[idx]['title']
            
            # 计算相似度
            target_vec = book_vectors[idx].unsqueeze(0)
            sims = torch.mm(target_vec, book_vectors.t()).squeeze(0)
            
            # 修改点：取 Top 11 (排除自己后剩下 10 本)
            scores, indices = torch.topk(sims, k=11)
            
            print(f"\n✅ 匹配成功！基于剧情与文风，为您推荐与《{current_title}》最像的10本书：")
            print("-" * 60)
            for i in range(1, len(indices)):
                res_idx = indices[i].item()
                print(f"   [{i:02d}] 《{df.iloc[res_idx]['title']:<20}》 (相似度: {scores[i].item():.4f})")

        elif choice == '2':
            print("\n当前系统支持的大分类：")
            for i in range(0, len(main_categories), 4):
                print(" | ".join(f"{cat:10}" for cat in main_categories[i:i+4]))
            
            print("\n💡 输入一个或多个大类名（空格隔开），系统将为您筛选最优质的10部作品：")
            selected_input = input("您的选择: ").strip().split()
            
            selected_codes = []
            valid_names = []
            for name in selected_input:
                if name in main_categories:
                    code = encoders['main_cat'].transform([name])[0]
                    selected_codes.append(code)
                    valid_names.append(name)
            
            if not selected_codes:
                print("× 未识别到有效的分类，请输入上方列表中的名称。")
                continue
            
            # 筛选并排序
            mask = df['main_cat'].isin(selected_codes)
            filtered = df[mask].copy()
            
            if filtered.empty:
                print("！该分类下暂时没有数据。")
            else:
                # 按照阅读权重降序排列，取前 10 名
                recommendations = filtered.sort_values(by=['read_count', 'word_count'], ascending=False).head(10)
                
                print(f"\n✅ 已为您在【{' / '.join(valid_names)}】中精选出 Top 10 优质作品：")
                print("-" * 60)
                for i, (idx, row) in enumerate(recommendations.iterrows()):
                    # 反向解析子分类名称
                    sub_cat_name = encoders['sub_cat'].inverse_transform([int(row['sub_cat'])])[0]
                    print(f"   [{i+1:02d}] 《{row['title']:<20}》 | 类别：{sub_cat_name:<10} | 评分：{row['read_count']:.4f}")

        elif choice.lower() in ['3', 'quit', 'exit']:
            print("感谢使用，系统已关闭。")
            break
        else:
            print("输入指令无效，请重新输入。")

if __name__ == "__main__":
    interactive_test()