"""验证PDF文件与JSON标记的一致性"""
import json
import glob
import os

results_dir = 'ieee_results'
pdf_dir = 'ieee_pdfs'

# 获取所有实际PDF文件
actual_pdfs = set(os.path.basename(f) for f in glob.glob(f"{pdf_dir}/*.pdf"))
print(f"实际PDF文件数: {len(actual_pdfs)} 个\n")

# 检查JSON中标记的下载状态
result_files = sorted(glob.glob(f"{results_dir}/query_*_results.json"), 
                     key=lambda x: int(os.path.basename(x).split('_')[1]))

json_marked = 0
json_files = []
missing_files = []

for file in result_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', [])
    for article in articles:
        if article.get('pdf_downloaded', False):
            json_marked += 1
            pdf_path = article.get('pdf_path', '')
            if pdf_path:
                pdf_filename = os.path.basename(pdf_path)
                json_files.append(pdf_filename)
                if pdf_filename not in actual_pdfs:
                    missing_files.append({
                        'filename': pdf_filename,
                        'query_id': data['query_id'],
                        'title': article.get('title', '')[:60]
                    })
                    print(f"⚠️  JSON标记已下载但文件不存在: {pdf_filename}")
                    print(f"   来源: 检索式 #{data['query_id']}, 文献: {article.get('title', '')[:60]}...")
            else:
                # 没有pdf_path但标记为已下载
                missing_files.append({
                    'filename': '(无路径)',
                    'query_id': data['query_id'],
                    'title': article.get('title', '')[:60]
                })
                print(f"⚠️  JSON标记已下载但无pdf_path: 检索式 #{data['query_id']}, 文献: {article.get('title', '')[:60]}...")

print(f"\nJSON中标记已下载: {json_marked} 个")
print(f"实际PDF文件数: {len(actual_pdfs)} 个")
print(f"差异: {json_marked - len(actual_pdfs)} 个")

# 检查是否有实际文件但JSON未标记
json_file_set = set(json_files)
missing_in_json = actual_pdfs - json_file_set
if missing_in_json:
    print(f"\n⚠️  有 {len(missing_in_json)} 个PDF文件在JSON中未找到对应记录")

if missing_files:
    print(f"\n📋 缺失文件详情:")
    for i, item in enumerate(missing_files, 1):
        print(f"  {i}. {item['filename']}")
        print(f"     检索式 #{item['query_id']}: {item['title']}...")

