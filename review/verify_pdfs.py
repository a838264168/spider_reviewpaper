"""验证PDF文件"""
import os

pdf_dir = 'ieee_pdfs'
files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

print(f"\n{'='*60}")
print(f"PDF文件验证报告")
print(f"{'='*60}\n")
print(f"文件数量：{len(files)} 个\n")

total_size = 0
valid_count = 0

for i, filename in enumerate(files, 1):
    filepath = os.path.join(pdf_dir, filename)
    size = os.path.getsize(filepath)
    total_size += size
    
    # 验证PDF文件头
    with open(filepath, 'rb') as f:
        header = f.read(4)
        is_valid = header == b'%PDF'
    
    status = "✓ 有效PDF" if is_valid else "✗ 无效文件"
    if is_valid:
        valid_count += 1
    
    print(f"{i}. {filename[:50]}...")
    print(f"   大小：{size/1024:.1f} KB | {status}")

print(f"\n{'='*60}")
print(f"总计：{len(files)} 个文件，{total_size/1024/1024:.2f} MB")
print(f"有效PDF：{valid_count}/{len(files)} 个")
print(f"{'='*60}\n")




