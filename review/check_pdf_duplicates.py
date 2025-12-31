"""检查PDF文件是否有重复统计"""
import json
import glob
import os
from collections import Counter

actual_pdfs = set(os.path.basename(f) for f in glob.glob('ieee_pdfs/*.pdf'))
result_files = glob.glob('ieee_results/query_*_results.json')

all_pdf_paths = []
pdf_to_articles = {}

for file in result_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for article in data.get('articles', []):
        if article.get('pdf_downloaded', False):
            pdf_path = article.get('pdf_path', '')
            if pdf_path:
                pdf_filename = os.path.basename(pdf_path)
                all_pdf_paths.append(pdf_filename)
                if pdf_filename not in pdf_to_articles:
                    pdf_to_articles[pdf_filename] = []
                pdf_to_articles[pdf_filename].append({
                    'query_id': data['query_id'],
                    'title': article.get('title', '')[:50]
                })

# 统计重复
counter = Counter(all_pdf_paths)
duplicates = {k: v for k, v in counter.items() if v > 1}

print(f"实际PDF文件数: {len(actual_pdfs)} 个")
print(f"JSON中标记的PDF路径数: {len(all_pdf_paths)} 个")
print(f"去重后的PDF路径数: {len(set(all_pdf_paths))} 个")

if duplicates:
    print(f"\n⚠️  发现 {len(duplicates)} 个PDF被重复统计:")
    for pdf_name, count in duplicates.items():
        print(f"\n  {pdf_name} (被统计 {count} 次):")
        for article in pdf_to_articles[pdf_name]:
            print(f"    - 检索式 #{article['query_id']}: {article['title']}...")
else:
    print("\n✓ 没有发现重复统计")

# 检查哪些PDF在JSON中但不在实际文件中
json_pdfs = set(all_pdf_paths)
missing = json_pdfs - actual_pdfs
if missing:
    print(f"\n⚠️  有 {len(missing)} 个PDF在JSON中标记但实际文件不存在:")
    for pdf in missing:
        print(f"  - {pdf}")
        for article in pdf_to_articles[pdf]:
            print(f"    来自: 检索式 #{article['query_id']}")




