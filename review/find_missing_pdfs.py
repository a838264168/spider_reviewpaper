"""找出JSON标记已下载但实际文件不存在的记录"""
import json
import glob
import os

actual_pdfs = set(os.path.basename(f) for f in glob.glob('ieee_pdfs/*.pdf'))
result_files = glob.glob('ieee_results/query_*_results.json')

missing = []

for file in result_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for article in data.get('articles', []):
        if article.get('pdf_downloaded', False):
            pdf_path = article.get('pdf_path', '')
            if pdf_path:
                pdf_filename = os.path.basename(pdf_path)
                if pdf_filename not in actual_pdfs:
                    missing.append({
                        'query_id': data['query_id'],
                        'title': article.get('title', ''),
                        'pdf_path': pdf_path
                    })
            else:
                missing.append({
                    'query_id': data['query_id'],
                    'title': article.get('title', ''),
                    'pdf_path': '(无路径)'
                })

print(f"实际PDF文件数: {len(actual_pdfs)} 个")
print(f"JSON标记已下载: {sum(1 for f in result_files for a in json.load(open(f, encoding='utf-8')).get('articles', []) if a.get('pdf_downloaded', False))} 个")
print(f"\n找到 {len(missing)} 个标记已下载但文件缺失的记录:\n")

for i, item in enumerate(missing, 1):
    print(f"{i}. 检索式 #{item['query_id']}")
    print(f"   标题: {item['title'][:70]}...")
    print(f"   路径: {item['pdf_path']}")
    print()




