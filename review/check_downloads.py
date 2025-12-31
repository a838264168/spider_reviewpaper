"""检查每个检索式的文献和PDF下载情况"""
import json
import os
import glob

results_dir = 'ieee_results'
result_files = sorted(glob.glob(f"{results_dir}/query_*_results.json"), 
                     key=lambda x: int(os.path.basename(x).split('_')[1]))

print("\n" + "="*80)
print("检索式文献和PDF下载详细统计")
print("="*80)

total_articles = 0
total_pdfs = 0
queries_with_results = 0

for file in result_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    query_id = data['query_id']
    articles_count = data.get('articles_count', 0)
    articles = data.get('articles', [])
    
    if articles_count > 0:
        queries_with_results += 1
        pdfs_downloaded = sum(1 for a in articles if a.get('pdf_downloaded', False))
        
        print(f"\n检索式 #{query_id:>2}: 找到 {articles_count:>2} 篇文献, 下载 {pdfs_downloaded:>2} 个PDF", end="")
        
        if pdfs_downloaded < articles_count:
            print(f" ({pdfs_downloaded/articles_count*100:.0f}%)")
        else:
            print(" (100%)")
        
        # 显示前3篇的标题
        if articles_count <= 3:
            for i, article in enumerate(articles, 1):
                pdf_status = "✓" if article.get('pdf_downloaded') else "✗"
                print(f"  {i}. [{pdf_status}] {article['title'][:60]}...")
        
        total_articles += articles_count
        total_pdfs += pdfs_downloaded

print("\n" + "="*80)
print(f"总计:")
print(f"  有结果的检索式: {queries_with_results} 个")
print(f"  提取文献总数: {total_articles} 篇")
print(f"  下载PDF总数: {total_pdfs} 个")
print(f"  下载成功率: {total_pdfs/total_articles*100:.1f}%" if total_articles > 0 else "  下载成功率: N/A")
print("="*80 + "\n")

