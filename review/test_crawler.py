"""
测试脚本：验证爬虫基本功能
仅测试第1个检索式，测试PDF下载，不保存进度
"""

import sys
import time
from ieee_crawler import IEEECrawler
import logging
import os

def test_single_query():
    """测试单个检索式"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║              IEEE Xplore 爬虫测试程序                     ║
    ║                                                           ║
    ║  🧪 测试第1个检索式（含多页+PDF下载）                    ║
    ║  ⏱️  预计耗时：2-3分钟                                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("\n正在初始化...")
    
    # 创建爬虫实例
    crawler = IEEECrawler()
    
    # 设置更短的延迟（仅用于测试）
    crawler.min_delay = 5
    crawler.max_delay = 10
    
    # 设置测试页数（测试3页）
    crawler.max_pages = 3
    
    try:
        # 初始化浏览器
        print("✓ 正在启动浏览器...")
        crawler.init_driver()
        print("✓ 浏览器启动成功")
        
        # 加载检索式
        queries = crawler.load_queries()
        
        if not queries:
            print("❌ 未找到检索式！请检查CSV文件")
            return False
        
        # 测试第一个检索式
        test_query = queries[0]
        
        print(f"\n{'='*60}")
        print(f"🧪 测试检索式 #{test_query['id']}")
        print(f"内容：{test_query['text'][:100]}...")
        print(f"{'='*60}\n")
        
        # 执行搜索
        result = crawler.search_query(test_query['text'])
        
        if result['success']:
            print(f"\n✅ 测试成功！")
            print(f"   找到结果：{result.get('total_results', 'N/A')}")
            print(f"   提取文章：{result.get('articles_count', 0)} 篇（已测试多页爬取）")
            print(f"   下载PDF：{result.get('pdfs_downloaded', 0)} 篇")
            
            # 显示前5篇文章
            articles = result.get('articles', [])
            if articles:
                print(f"\n📄 前5篇文章预览：")
                for idx, article in enumerate(articles[:5], 1):
                    pdf_status = "✓ PDF已下载" if article.get('pdf_downloaded') else "✗ PDF未下载"
                    print(f"\n{idx}. {article.get('title', 'N/A')[:80]}...")
                    print(f"   作者：{article.get('authors', 'N/A')[:60]}...")
                    print(f"   年份：{article.get('year', 'N/A')} | {pdf_status}")
                
                if len(articles) > 5:
                    print(f"\n... 还有 {len(articles) - 5} 篇文章")
            
            # 检查PDF文件
            pdf_dir = 'ieee_pdfs'
            if os.path.exists(pdf_dir):
                pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
                print(f"\n📁 PDF文件夹：{pdf_dir}")
                print(f"   文件数量：{len(pdf_files)} 个")
                
                if pdf_files:
                    print(f"   文件列表：")
                    for pdf in pdf_files[:3]:
                        pdf_path = os.path.join(pdf_dir, pdf)
                        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
                        print(f"     - {pdf} ({size_mb:.2f} MB)")
                    if len(pdf_files) > 3:
                        print(f"     ... 还有 {len(pdf_files) - 3} 个文件")
            
            # 保存测试结果
            crawler.save_results(test_query['id'], test_query['text'], result)
            print(f"\n✓ 测试结果已保存到：ieee_results/query_{test_query['id']}_results.json")
            
            print(f"\n{'='*60}")
            print("🎉 多页爬取+PDF下载功能测试完成！")
            print(f"   当前设置：每个检索式爬取 {crawler.max_pages} 页")
            print(f"   预计每个检索式获取：{crawler.max_pages * crawler.results_per_page} 篇文献")
            print(f"   PDF下载：{'启用' if crawler.download_pdf else '禁用'}")
            
            # 判断是否可以开始正式爬取
            pdfs_downloaded = result.get('pdfs_downloaded', 0)
            if pdfs_downloaded > 0:
                print(f"\n✅ PDF下载功能正常！可以开始正式爬取")
                print("   运行命令：python ieee_crawler.py")
            else:
                print(f"\n⚠️  PDF下载功能可能受限（无权限或未找到下载按钮）")
                print("   建议：")
                print("     1. 如果需要PDF，请确保有IEEE订阅权限（校园网/VPN）")
                print("     2. 可以只爬取元数据（在ieee_crawler.py中设置download_pdf=False）")
                print("   运行命令：python ieee_crawler.py")
            
            print(f"{'='*60}")
            
            return True
        else:
            print(f"\n❌ 测试失败：{result.get('error', 'unknown')}")
            print("\n可能的原因：")
            print("  1. 网络连接问题")
            print("  2. 需要登录IEEE Xplore")
            print("  3. 页面结构已更新")
            print("  4. IP被限制（很少见于单次测试）")
            print("\n请查看 ieee_crawler.log 获取详细错误信息")
            return False
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错：{e}")
        print("\n常见问题：")
        print("  1. 未安装Chrome浏览器")
        print("  2. ChromeDriver版本不匹配")
        print("  3. 依赖包未安装：pip install -r requirements.txt")
        logging.exception("测试失败")
        return False
    finally:
        if crawler.driver:
            print("\n正在关闭浏览器...")
            crawler.driver.quit()
            print("✓ 已关闭")


def check_environment():
    """检查运行环境"""
    print("\n🔍 检查运行环境...\n")
    
    issues = []
    
    # 检查Python版本
    import sys
    python_version = sys.version_info
    print(f"✓ Python版本：{python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        issues.append("Python版本过低，建议3.7+")
    
    # 检查依赖包
    try:
        import selenium
        print(f"✓ Selenium：已安装 (版本 {selenium.__version__})")
    except ImportError:
        issues.append("未安装Selenium：pip install selenium")
    
    # 检查CSV文件
    import os
    csv_file = 'IEEE_Xplore_检索式汇总_修正版.csv'
    if os.path.exists(csv_file):
        print(f"✓ 检索式文件：已找到")
    else:
        issues.append(f"未找到检索式文件：{csv_file}")
    
    # 检查Chrome
    try:
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print(f"✓ Chrome浏览器：正常")
    except Exception as e:
        issues.append(f"Chrome/ChromeDriver问题：{str(e)[:50]}")
    
    if issues:
        print(f"\n⚠️  发现 {len(issues)} 个问题：")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("\n✅ 环境检查通过！")
        return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  步骤 1/2：环境检查")
    print("="*60)
    
    env_ok = check_environment()
    
    if not env_ok:
        print("\n❌ 环境检查未通过，请先解决上述问题")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("  步骤 2/2：功能测试")
    print("="*60)
    
    print("\n🚀 自动开始测试（包含PDF下载）...")
    time.sleep(2)
    
    success = test_single_query()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

