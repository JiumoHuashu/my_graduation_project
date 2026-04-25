import torch
import pickle
import pandas as pd
import sys
import os

def load_resources():
    print("正在加载深度语义推荐引擎 (简介+章节融合版)...")
    metadata_file = 'model_metadata_advanced.pkl'
    vector_file = 'book_vectors_advanced.pt'
    
    if not os.path.exists(metadata_file) or not os.path.exists(vector_file):
        print("错误：未找到模型文件！请确保已经运行了最新的训练脚本并生成了 .pt 和 .pkl 文件。")
        sys.exit()

    with open(metadata_file, 'rb') as f:
        metadata = pickle.load(f)
    return metadata['df'], metadata['encoders'], torch.load(vector_file)

def interactive_test():
    df, encoders, book_vectors = load_resources()

    print("\n" + "★"*40)
    print("      飞卢小说【多维度语义融合】推荐测试      ")
    print("      输入多本书名 -> 自动合成口味 -> 推荐20本      ")
    print("★"*40)

    while True:
        print("\n💡 请输入您喜欢的书籍名称（多本书请用“空格”隔开，输入 quit 退出）：")
        user_input = input(">> ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        book_inputs = user_input.split()
        if not book_inputs:
            continue
            
        selected_vecs = []
        found_titles = []
        
        # 在库中寻找匹配的书籍
        for name in book_inputs:
            # 使用模糊匹配增强容错性
            match = df[df['title'].str.contains(name, na=False)]
            if not match.empty:
                # 如果匹配到多个，取第一个最相关的
                idx = match.index[0]
                selected_vecs.append(book_vectors[idx])
                found_titles.append(df.iloc[idx]['title'])
            else:
                print(f"⚠️ 库中未找到书名包含《{name}》的书籍，已跳过。")
        
        if not selected_vecs:
            print("❌ 抱歉，未能匹配到任何有效书籍，请重新输入。")
            continue
        
        print(f"\n✅ 已锁定参考样本：{ ' + '.join([f'《{t}》' for t in found_titles]) }")
        print("正在进行多向量空间融合计算...")

        # --- 核心推荐算法：多中心融合 ---
        # 1. 将选中的多本书向量合成一个平均向量（用户的“灵魂指纹”）
        combined_vec = torch.stack(selected_vecs).mean(dim=0).unsqueeze(0)
        
        # 2. 计算余弦相似度（全库搜索）
        sims = torch.mm(combined_vec, book_vectors.t()).squeeze(0)
        
        # 3. 提取 Top 25 (多取几个用于过滤原书)
        scores, indices = torch.topk(sims, k=min(25, len(df)))
        
        print(f"\n🚀 基于您的综合兴趣，为您精准匹配以下 20 本作品：")
        print("-" * 75)
        
        count = 0
        for i in range(len(indices)):
            res_idx = indices[i].item()
            target_title = df.iloc[res_idx]['title']
            
            # 过滤：如果这本书是用户刚刚输入的那几本之一，就不显示
            if target_title in found_titles:
                continue
                
            count += 1
            # 反向解析分类标签用于显示
            main_name = encoders['main_cat'].inverse_transform([int(df.iloc[res_idx]['main_cat'])])[0]
            sub_name = encoders['sub_cat'].inverse_transform([int(df.iloc[res_idx]['sub_cat'])])[0]
            
            print(f"   [{count:02d}] 《{target_title:<25}》 | 分类：{main_name}-{sub_name:<10} | 匹配度：{scores[i].item():.4f}")
            
            if count >= 20: # 严格限制推荐 20 本
                break
        print("-" * 75)

if __name__ == "__main__":
    interactive_test()