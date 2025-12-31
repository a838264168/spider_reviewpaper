"""
IEEE Xplore 爬虫调试工具
用于查看页面结构和元素选择器
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_ieee_page():
    """调试IEEE页面，查看实际结构"""
    
    print("🔍 IEEE Xplore 页面结构调试工具\n")
    
    # 测试检索式
    test_query = '(("self-esteem" OR "self concept") AND ("psychological assessment" OR "psychometrics") AND ("machine learning" OR "deep learning"))'
    
    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 访问搜索页面
        url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={test_query}&newsearch=true"
        print(f"正在访问：{url[:100]}...\n")
        
        driver.get(url)
        print("✓ 页面已加载\n")
        
        # 等待页面加载
        time.sleep(5)
        
        # 截图
        screenshot_path = "ieee_page_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"✓ 截图已保存：{screenshot_path}\n")
        
        # 查找可能的元素
        print("="*60)
        print("🔍 查找页面元素...")
        print("="*60)
        
        # 尝试不同的选择器
        selectors_to_try = [
            ("CLASS_NAME", "result-item"),
            ("CLASS_NAME", "List-results-items"),
            ("CLASS_NAME", "document-container"),
            ("CLASS_NAME", "search-result"),
            ("TAG_NAME", "article"),
            ("XPATH", "//div[contains(@class, 'result')]"),
            ("XPATH", "//xpl-document-result"),
            ("CSS_SELECTOR", "[class*='result']"),
            ("CSS_SELECTOR", "xpl-document-result"),
        ]
        
        for method, selector in selectors_to_try:
            try:
                if method == "CLASS_NAME":
                    elements = driver.find_elements(By.CLASS_NAME, selector)
                elif method == "TAG_NAME":
                    elements = driver.find_elements(By.TAG_NAME, selector)
                elif method == "XPATH":
                    elements = driver.find_elements(By.XPATH, selector)
                elif method == "CSS_SELECTOR":
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"\n✅ 找到 {len(elements)} 个元素：{method} = '{selector}'")
                    
                    # 显示第一个元素的详细信息
                    if len(elements) > 0:
                        elem = elements[0]
                        print(f"   - 标签名：{elem.tag_name}")
                        print(f"   - 类名：{elem.get_attribute('class')}")
                        print(f"   - ID：{elem.get_attribute('id')}")
                        print(f"   - 文本预览：{elem.text[:100]}...")
                else:
                    print(f"   ❌ 未找到：{method} = '{selector}'")
                    
            except Exception as e:
                print(f"   ⚠️  {method} = '{selector}' 出错：{str(e)[:50]}")
        
        # 保存页面源代码
        with open("ieee_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"\n✓ 页面源代码已保存：ieee_page_source.html")
        
        # 查找标题元素
        print("\n" + "="*60)
        print("🔍 查找标题元素...")
        print("="*60)
        
        title_selectors = [
            ("CLASS_NAME", "result-item-title"),
            ("CLASS_NAME", "document-title"),
            ("XPATH", "//h2//a"),
            ("XPATH", "//h3//a"),
            ("CSS_SELECTOR", "h2 a"),
            ("CSS_SELECTOR", "h3 a"),
            ("CSS_SELECTOR", "[class*='title'] a"),
        ]
        
        for method, selector in title_selectors:
            try:
                if method == "CLASS_NAME":
                    elements = driver.find_elements(By.CLASS_NAME, selector)
                elif method == "XPATH":
                    elements = driver.find_elements(By.XPATH, selector)
                elif method == "CSS_SELECTOR":
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"\n✅ 找到 {len(elements)} 个标题：{method} = '{selector}'")
                    for idx, elem in enumerate(elements[:3], 1):
                        print(f"   {idx}. {elem.text[:80]}")
                        
            except Exception as e:
                pass
        
        # 交互模式：保持浏览器打开
        print("\n" + "="*60)
        print("✅ 调试完成！")
        print("="*60)
        print("\n请查看：")
        print("  1. ieee_page_screenshot.png - 页面截图")
        print("  2. ieee_page_source.html - 页面源代码")
        print("\n浏览器窗口将保持打开30秒，您可以手动查看...")
        
        time.sleep(30)
        
    finally:
        driver.quit()
        print("\n✓ 浏览器已关闭")


if __name__ == "__main__":
    debug_ieee_page()


