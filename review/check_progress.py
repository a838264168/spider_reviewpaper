"""
查看爬取进度
"""

import json
import os
import glob
from datetime import datetime

def check_progress():
    print("\n" + "="*60)
    print("IEEE Xplore 爬虫进度查看")
    print("="*60)
    
    # 读取进度文件
    progress_file = 'crawl_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        completed = len(progress.get('completed', []))
        failed = len(progress.get('failed', []))
        total = 80
        
        print(f"\n状态统计：")
        print(f"  已完成：{completed}/{total} 个检索式 ({completed/total*100:.1f}%)")
        print(f"  失败：{failed} 个")
        print(f"  剩余：{total - completed} 个")
        
        last_time = progress.get('last_query_time')
        if last_time:
            print(f"  最后更新：{last_time[:19]}")
    else:
        print("\n未找到进度文件，爬虫可能还未启动")
    
    # 检查结果文件
    result_dir = 'ieee_results'
    if os.path.exists(result_dir):
        result_files = glob.glob(f"{result_dir}/query_*_results.json")
        print(f"\n结果文件：{len(result_files)} 个")
        
        total_articles = 0
        for file in result_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_articles += data.get('articles_count', 0)
            except:
                pass
        
        print(f"  已提取文献：{total_articles} 篇")
    
    # 检查PDF文件
    pdf_dir = 'ieee_pdfs'
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        print(f"\nPDF文件：{len(pdf_files)} 个")
        
        if pdf_files:
            total_size = sum(os.path.getsize(os.path.join(pdf_dir, f)) for f in pdf_files)
            print(f"  总大小：{total_size / (1024*1024):.2f} MB")
    
    # 检查日志最后几行
    log_file = 'ieee_crawler.log'
    if os.path.exists(log_file):
        print(f"\n最近日志：")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"  {line.strip()}")
    
    print("\n" + "="*60)
    print("提示：")
    print("  - 查看完整日志：type ieee_crawler.log")
    print("  - 查看进度文件：type crawl_progress.json")
    print("  - 停止爬虫：按 Ctrl+C")
    print("="*60 + "\n")


if __name__ == "__main__":
    check_progress()


