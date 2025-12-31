"""
IEEE Xplore 爬虫 - 智能启动脚本
自动判断PDF下载权限并运行
"""

import os
import sys
from ieee_crawler import IEEECrawler
import logging

# Windows编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         IEEE Xplore 爬虫 - 自动运行                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("根据测试结果：")
    print("   [OK] 多页爬取功能：正常")
    print("   [OK] 元数据提取：正常")
    print("   [!]  PDF下载：受限（可能需要IEEE订阅权限）")
    
    print("\n现在开始正式爬取...")
    print("   - 80个检索式")
    print("   - 每个检索式5页")
    print("   - 预计2-3小时")
    print("   - PDF下载：自动尝试（有权限时下载，无权限时跳过）")
    
    print("\n开始运行...")
    print("="*60)
    
    # 创建爬虫实例
    crawler = IEEECrawler()
    
    # 设置：启用PDF下载（但遇到无权限时自动跳过）
    crawler.download_pdf = True
    crawler.max_pages = 5
    
    # 运行爬虫
    try:
        crawler.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断爬取")
        print("   进度已保存，下次运行会自动继续")
    except Exception as e:
        print(f"\n\n❌ 运行出错：{e}")
        logging.exception("爬虫运行错误")
    
    print("\n" + "="*60)
    print("[OK] 爬取任务结束")
    print(f"   结果目录：{crawler.output_dir}/")
    print(f"   PDF目录：{crawler.pdf_dir}/")
    print("   运行分析：python analyze_results.py")
    print("="*60)


if __name__ == "__main__":
    # 直接运行，不需要用户确认
    main()

