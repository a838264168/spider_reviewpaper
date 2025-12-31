"""
调试PDF下载功能
查看页面元素和下载流程
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def debug_pdf_download():
    """调试PDF下载流程"""
    
    print("🔍 IEEE Xplore PDF下载调试工具\n")
    
    # 测试文章链接（从之前的结果获取）
    test_url = "https://ieeexplore.ieee.org/document/10763288/"
    
    # 设置下载目录
    pdf_dir = os.path.abspath('ieee_pdfs_test')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    # 设置下载
    prefs = {
        'download.default_directory': pdf_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True
    }
    options.add_experimental_option('prefs', prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"正在访问：{test_url}\n")
        driver.get(test_url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 截图1：初始页面
        driver.save_screenshot("debug_step1_initial.png")
        print("✓ 截图1已保存：debug_step1_initial.png\n")
        
        # 查找所有可能的下载相关元素
        print("="*60)
        print("🔍 查找PDF下载相关元素...")
        print("="*60)
        
        download_elements = []
        
        # 方法1：查找所有链接
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            text = link.text.strip().lower()
            href = link.get_attribute('href') or ''
            aria = link.get_attribute('aria-label') or ''
            classes = link.get_attribute('class') or ''
            
            if any(keyword in text.lower() for keyword in ['pdf', 'download', '下载']):
                download_elements.append({
                    'type': 'link',
                    'text': link.text[:50],
                    'href': href[:100],
                    'aria-label': aria[:50],
                    'class': classes[:50],
                    'element': link
                })
            elif 'pdf' in href.lower() or 'pdf' in aria.lower() or 'pdf' in classes.lower():
                download_elements.append({
                    'type': 'link',
                    'text': link.text[:50],
                    'href': href[:100],
                    'aria-label': aria[:50],
                    'class': classes[:50],
                    'element': link
                })
        
        # 方法2：查找所有按钮
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in all_buttons:
            text = button.text.strip().lower()
            aria = button.get_attribute('aria-label') or ''
            classes = button.get_attribute('class') or ''
            
            if any(keyword in text.lower() for keyword in ['pdf', 'download', '下载']):
                download_elements.append({
                    'type': 'button',
                    'text': button.text[:50],
                    'aria-label': aria[:50],
                    'class': classes[:50],
                    'element': button
                })
            elif 'pdf' in aria.lower() or 'pdf' in classes.lower():
                download_elements.append({
                    'type': 'button',
                    'text': button.text[:50],
                    'aria-label': aria[:50],
                    'class': classes[:50],
                    'element': button
                })
        
        # 显示找到的元素
        print(f"\n✅ 找到 {len(download_elements)} 个PDF相关元素：\n")
        for idx, elem in enumerate(download_elements, 1):
            print(f"{idx}. 类型：{elem['type']}")
            print(f"   文本：{elem['text']}")
            if 'href' in elem:
                print(f"   链接：{elem['href']}")
            print(f"   ARIA标签：{elem['aria-label']}")
            print(f"   CSS类：{elem['class']}")
            print()
        
        # 尝试点击第一个PDF相关元素
        if download_elements:
            print("="*60)
            print("🖱️  尝试点击第一个PDF相关元素...")
            print("="*60)
            
            target = download_elements[0]
            element = target['element']
            
            # 滚动到元素
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            
            # 截图2：点击前
            driver.save_screenshot("debug_step2_before_click.png")
            print("✓ 截图2已保存：debug_step2_before_click.png")
            
            # 高亮显示要点击的元素
            driver.execute_script("arguments[0].style.border='3px solid red'", element)
            time.sleep(0.5)
            driver.save_screenshot("debug_step3_highlight.png")
            print("✓ 截图3已保存：debug_step3_highlight.png（红框为目标元素）")
            
            # 点击
            print(f"\n正在点击元素...")
            print(f"  类型：{target['type']}")
            print(f"  文本：{target['text']}")
            
            element.click()
            print("✓ 已点击\n")
            
            # 截图3：点击后
            time.sleep(2)
            driver.save_screenshot("debug_step4_after_click.png")
            print("✓ 截图4已保存：debug_step4_after_click.png")
            
            # 等待下载
            print("\n等待30秒，观察下载情况...")
            print("请查看浏览器窗口，观察是否有：")
            print("  1. 弹出登录对话框")
            print("  2. 显示需要订阅/权限")
            print("  3. PDF开始下载")
            print("  4. 其他提示信息\n")
            
            for i in range(30, 0, -5):
                print(f"剩余 {i} 秒...")
                time.sleep(5)
                
                # 检查下载目录
                if os.path.exists(pdf_dir):
                    files = os.listdir(pdf_dir)
                    if files:
                        print(f"\n✅ 发现文件：{files}")
                        break
            
            # 最终截图
            driver.save_screenshot("debug_step5_final.png")
            print("\n✓ 截图5已保存：debug_step5_final.png")
            
            # 检查下载结果
            print("\n" + "="*60)
            print("📁 检查下载结果")
            print("="*60)
            
            if os.path.exists(pdf_dir):
                files = os.listdir(pdf_dir)
                if files:
                    print(f"\n✅ 下载成功！找到 {len(files)} 个文件：")
                    for f in files:
                        fpath = os.path.join(pdf_dir, f)
                        size = os.path.getsize(fpath) / 1024
                        print(f"  - {f} ({size:.2f} KB)")
                else:
                    print("\n⚠️  下载目录为空")
            
            # 检查是否有弹窗或提示
            print("\n" + "="*60)
            print("🔍 检查页面提示信息")
            print("="*60)
            
            # 查找可能的错误/提示信息
            alert_selectors = [
                "div[role='alert']",
                "div.error",
                "div.warning",
                "div.message",
                "[class*='modal']",
                "[class*='dialog']",
                "[class*='popup']"
            ]
            
            for selector in alert_selectors:
                try:
                    alerts = driver.find_elements(By.CSS_SELECTOR, selector)
                    if alerts:
                        print(f"\n找到提示信息（{selector}）：")
                        for alert in alerts:
                            if alert.is_displayed():
                                print(f"  - {alert.text[:200]}")
                except:
                    pass
            
        else:
            print("❌ 未找到PDF相关元素")
        
        # 保存页面源码
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n✓ 页面源码已保存：debug_page_source.html")
        
        print("\n" + "="*60)
        print("✅ 调试完成！")
        print("="*60)
        print("\n请查看以下文件：")
        print("  1. debug_step1_initial.png - 初始页面")
        print("  2. debug_step2_before_click.png - 点击前")
        print("  3. debug_step3_highlight.png - 目标元素（红框）")
        print("  4. debug_step4_after_click.png - 点击后")
        print("  5. debug_step5_final.png - 最终状态")
        print("  6. debug_page_source.html - 页面源码")
        print(f"  7. {pdf_dir}/ - 下载目录")
        
        print("\n浏览器将保持打开30秒，您可以手动查看...")
        time.sleep(30)
        
    finally:
        driver.quit()
        print("\n✓ 浏览器已关闭")


if __name__ == "__main__":
    debug_pdf_download()





