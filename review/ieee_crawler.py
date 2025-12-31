"""
IEEE Xplore 文献检索爬虫
安全爬取，避免封IP
"""

import csv
import time
import random
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ieee_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class IEEECrawler:
    def __init__(self, csv_file='IEEE_Xplore_检索式汇总_修正版.csv'):
        """初始化爬虫"""
        self.csv_file = csv_file
        self.base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
        
        # 频率控制：60-120秒随机间隔（安全2倍）
        self.min_delay = 60  
        self.max_delay = 120
        
        # 页面内小延迟
        self.small_delay_min = 3
        self.small_delay_max = 8
        
        # 多页爬取设置
        self.max_pages = 5  # 每个检索式最多爬取5页
        self.results_per_page = 25  # IEEE默认每页25条
        
        # PDF下载设置
        self.download_pdf = True  # 是否下载PDF
        self.pdf_dir = 'ieee_pdfs'  # PDF保存目录
        os.makedirs(self.pdf_dir, exist_ok=True)
        
        # 结果保存目录
        self.output_dir = 'ieee_results'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 进度文件
        self.progress_file = 'crawl_progress.json'
        self.load_progress()
        
        # 初始化浏览器（延迟到实际使用时）
        self.driver = None
        
    def load_progress(self):
        """加载爬取进度"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
            logging.info(f"加载进度：已完成 {len(self.progress.get('completed', []))} 个检索式")
        else:
            self.progress = {'completed': [], 'failed': [], 'last_query_time': None}
    
    def save_progress(self):
        """保存爬取进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def init_driver(self):
        """初始化Selenium WebDriver"""
        if self.driver is not None:
            return
        
        options = webdriver.ChromeOptions()
        
        # 反爬虫设置
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 设置User-Agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 可选：无头模式（不显示浏览器窗口）
        # options.add_argument('--headless')
        
        # 设置下载目录和行为
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2  # 禁用图片
            },
            'download.default_directory': os.path.abspath(self.pdf_dir),  # 下载目录
            'download.prompt_for_download': False,  # 不询问下载位置
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True  # 不在浏览器中打开PDF
        }
        options.add_experimental_option('prefs', prefs)
        
        try:
            # 使用 webdriver-manager 自动管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            logging.info("浏览器初始化成功")
        except Exception as e:
            logging.error(f"浏览器初始化失败：{e}")
            logging.info("提示：请确保已安装Chrome浏览器")
            raise
    
    def load_queries(self):
        """从CSV加载检索式"""
        queries = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                query_id = row['编号']
                query_text = row['检索式'].strip('"')  # 移除CSV的引号
                queries.append({
                    'id': query_id,
                    'text': query_text
                })
        logging.info(f"加载了 {len(queries)} 个检索式")
        return queries
    
    def safe_delay(self, delay_type='large'):
        """安全延迟"""
        if delay_type == 'large':
            # 查询间隔：60-120秒
            delay = random.uniform(self.min_delay, self.max_delay)
            logging.info(f"等待 {delay:.1f} 秒...")
        else:
            # 页面操作间隔：3-8秒
            delay = random.uniform(self.small_delay_min, self.small_delay_max)
        
        time.sleep(delay)
    
    def search_query(self, query_text):
        """执行单个检索（支持多页）"""
        try:
            # 构建搜索URL
            search_url = f"{self.base_url}?queryText={query_text}&newsearch=true"
            
            logging.info(f"正在访问：{search_url[:100]}...")
            self.driver.get(search_url)
            
            # 等待页面加载
            self.safe_delay('small')
            
            # 等待结果加载
            wait = WebDriverWait(self.driver, 20)
            
            # 尝试获取结果数量
            try:
                result_stats = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Dashboard-statistics"))
                )
                total_results = result_stats.text
                logging.info(f"找到结果：{total_results}")
            except TimeoutException:
                logging.warning("未能获取结果统计信息")
                total_results = "未知"
            
            # 提取多页文献列表
            all_articles = []
            
            for page_num in range(1, self.max_pages + 1):
                logging.info(f"正在提取第 {page_num} 页...")
                
                # 提取当前页的文献
                page_articles = self.extract_articles()
                
                if not page_articles:
                    logging.warning(f"第 {page_num} 页没有找到文献，停止翻页")
                    break
                
                all_articles.extend(page_articles)
                logging.info(f"第 {page_num} 页提取了 {len(page_articles)} 篇文献（累计：{len(all_articles)} 篇）")
                
                # 如果不是最后一页，尝试翻页
                if page_num < self.max_pages:
                    if not self.go_to_next_page():
                        logging.info("没有下一页了，停止翻页")
                        break
                    
                    # 翻页后等待
                    self.safe_delay('small')
            
            logging.info(f"✓ 共提取了 {len(all_articles)} 篇文献（{len(set(a['title'] for a in all_articles))} 篇去重）")
            
            # 下载PDF（如果启用）
            downloaded_count = 0
            if self.download_pdf and all_articles:
                logging.info(f"\n开始下载 {len(all_articles)} 篇文献的PDF...")
                
                for idx, article in enumerate(all_articles, 1):
                    success = self.download_article_pdf(article, idx, len(all_articles))
                    if success:
                        downloaded_count += 1
                    
                    # 每篇文章下载后等待
                    if idx < len(all_articles):
                        self.safe_delay('small')
                
                logging.info(f"✓ PDF下载完成：成功 {downloaded_count}/{len(all_articles)} 篇")
            
            return {
                'success': True,
                'total_results': total_results,
                'articles_count': len(all_articles),
                'articles': all_articles,
                'pdfs_downloaded': downloaded_count
            }
            
        except TimeoutException:
            logging.error("页面加载超时")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            logging.error(f"搜索出错：{e}")
            return {'success': False, 'error': str(e)}
    
    def extract_articles(self):
        """提取当前页面的文献信息"""
        articles = []
        
        try:
            # 等待文献列表加载
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "List-results-items")))
            
            # 滚动页面以加载所有结果（IEEE使用懒加载）
            logging.info("正在滚动页面加载所有结果...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # 最多滚动3次
                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待加载
                
                # 计算新的滚动高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break  # 没有新内容了
                last_height = new_height
            
            # 滚回顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 获取所有文献项
            article_elements = self.driver.find_elements(By.CLASS_NAME, "result-item")
            logging.info(f"在页面中找到 {len(article_elements)} 个文献项")
            
            for idx, element in enumerate(article_elements, 1):
                try:
                    # 提取标题（优先使用h3 a）
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h3 a")
                        title = title_elem.text.strip()
                        link = title_elem.get_attribute('href')
                    except NoSuchElementException:
                        # 备用方案
                        title_elem = element.find_element(By.CLASS_NAME, "result-item-title")
                        title = title_elem.text.strip()
                        link = title_elem.find_element(By.TAG_NAME, "a").get_attribute('href')
                    
                    # 提取作者
                    try:
                        authors = element.find_element(By.CLASS_NAME, "author").text.strip()
                    except NoSuchElementException:
                        authors = "N/A"
                    
                    # 提取发表信息
                    try:
                        publisher_info = element.find_element(By.CLASS_NAME, "publisher-info-container").text.strip()
                    except NoSuchElementException:
                        publisher_info = "N/A"
                    
                    # 提取年份
                    try:
                        year = element.find_element(By.CLASS_NAME, "detail-info-year").text.strip()
                    except NoSuchElementException:
                        year = "N/A"
                    
                    # 提取摘要（如果有）
                    try:
                        abstract = element.find_element(By.CLASS_NAME, "description").text.strip()
                    except NoSuchElementException:
                        abstract = "N/A"
                    
                    # 提取文档ID（用于命名PDF）
                    doc_id = link.split('/')[-2] if '/' in link else f"doc_{idx}"
                    
                    article = {
                        'title': title,
                        'link': link,
                        'authors': authors,
                        'publisher_info': publisher_info,
                        'year': year,
                        'abstract': abstract,
                        'doc_id': doc_id,
                        'pdf_downloaded': False,
                        'pdf_path': None
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logging.warning(f"提取第 {idx} 篇文献时出错：{e}")
                    continue
            
            logging.info(f"成功提取 {len(articles)} 篇文献信息")
            
        except Exception as e:
            logging.error(f"提取文献列表失败：{e}")
        
        return articles
    
    def go_to_next_page(self):
        """翻到下一页"""
        try:
            # 方法1：查找并点击"下一页"按钮
            next_buttons = self.driver.find_elements(By.XPATH, "//button[@aria-label='Next page']")
            
            if not next_buttons:
                # 方法2：查找分页器中的下一页链接
                next_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'next-page')]")
            
            if not next_buttons:
                # 方法3：查找包含">"或"Next"文本的按钮
                next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
            
            if not next_buttons:
                # 方法4：通过CSS选择器查找
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".pagination .next, .pagination li:last-child a")
            
            for button in next_buttons:
                try:
                    # 检查按钮是否可用（没有disabled属性）
                    if button.is_enabled() and button.is_displayed():
                        # 滚动到按钮位置
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(1)
                        
                        # 点击
                        button.click()
                        logging.info("✓ 成功翻页")
                        return True
                except Exception as e:
                    logging.debug(f"尝试点击按钮失败：{e}")
                    continue
            
            logging.warning("未找到可用的下一页按钮")
            return False
            
        except Exception as e:
            logging.error(f"翻页失败：{e}")
            return False
    
    def download_article_pdf(self, article, current_idx, total_count):
        """下载单篇文章的PDF（两步流程：打开查看器 -> 下载）"""
        doc_id = article.get('doc_id', 'unknown')
        title = article.get('title', 'Untitled')[:50]  # 限制标题长度
        link = article.get('link', '')
        
        # 生成安全的文件名（移除特殊字符）
        safe_filename = "".join(c for c in f"{doc_id}_{title}" if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_filename = safe_filename[:100]  # 限制文件名长度
        pdf_path = os.path.join(self.pdf_dir, f"{safe_filename}.pdf")
        
        # 检查是否已下载
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:  # 至少1KB
            logging.info(f"[{current_idx}/{total_count}] PDF已存在：{safe_filename}.pdf")
            article['pdf_downloaded'] = True
            article['pdf_path'] = pdf_path
            return True
        
        try:
            logging.info(f"[{current_idx}/{total_count}] 正在下载：{title[:40]}...")
            
            # 第一步：访问文章页面，找到PDF查看器链接
            self.driver.get(link)
            time.sleep(3)
            
            # 查找PDF查看器链接（stamp.jsp）
            pdf_viewer_link = None
            try:
                # 方法1：查找包含stamp.jsp的链接
                pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'stamp.jsp')]")
                if pdf_links:
                    pdf_viewer_link = pdf_links[0].get_attribute('href')
                    logging.info(f"  ✓ 找到PDF查看器链接")
            except:
                pass
            
            if not pdf_viewer_link:
                # 方法2：查找PDF按钮
                try:
                    pdf_button = self.driver.find_element(By.CSS_SELECTOR, "[class*='pdf']")
                    pdf_viewer_link = pdf_button.get_attribute('href')
                except:
                    pass
            
            if not pdf_viewer_link:
                logging.warning(f"  ✗ 未找到PDF查看器链接：{title[:40]}")
                return False
            
            # 第二步：打开PDF查看器页面并提取iframe中的PDF URL
            logging.info(f"  → 打开PDF查看器...")
            self.driver.get(pdf_viewer_link)
            time.sleep(3)  # 等待页面加载
            
            # 第三步：查找iframe中的getPDF.jsp链接
            pdf_download_url = None
            try:
                # 方法1：查找iframe的src属性
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute('src')
                    if src and 'getPDF.jsp' in src:
                        pdf_download_url = src
                        logging.info(f"  ✓ 找到PDF下载URL（iframe）")
                        break
                
                # 方法2：从页面源码中提取
                if not pdf_download_url:
                    page_source = self.driver.page_source
                    import re
                    match = re.search(r'https://[^"\']*?getPDF\.jsp[^"\']*', page_source)
                    if match:
                        pdf_download_url = match.group(0).replace('&amp;', '&')
                        logging.info(f"  ✓ 找到PDF下载URL（源码）")
                        
            except Exception as e:
                logging.debug(f"  查找PDF URL失败：{e}")
            
            if not pdf_download_url:
                logging.warning(f"  ✗ 未找到PDF下载URL：{title[:40]}")
                return False
            
            # 第四步：使用requests直接下载PDF
            logging.info(f"  → 开始下载PDF...")
            try:
                import requests
                # 复制浏览器的cookies以保持会话
                cookies = {}
                for cookie in self.driver.get_cookies():
                    cookies[cookie['name']] = cookie['value']
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': pdf_viewer_link
                }
                
                response = requests.get(pdf_download_url, headers=headers, cookies=cookies, timeout=30)
                
                if response.status_code == 200 and len(response.content) > 1000:
                    # 检查是否真的是PDF文件
                    if response.content[:4] == b'%PDF':
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        article['pdf_downloaded'] = True
                        article['pdf_path'] = pdf_path
                        file_size = len(response.content) / 1024
                        logging.info(f"  ✓ 下载成功：{safe_filename}.pdf ({file_size:.1f} KB)")
                        return True
                    else:
                        logging.warning(f"  ✗ 响应不是PDF文件（可能需要订阅）")
                        return False
                else:
                    logging.warning(f"  ✗ 下载失败：HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                logging.error(f"  ✗ 下载出错：{str(e)[:100]}")
                return False
            
        except Exception as e:
            logging.error(f"  ✗ 下载失败：{str(e)[:100]}")
            return False
    
    def wait_for_download(self, expected_path, filename, timeout=30):
        """等待文件下载完成"""
        import glob
        
        # 等待下载开始和完成
        for i in range(timeout):
            time.sleep(1)
            
            # 检查目标文件是否存在
            if os.path.exists(expected_path) and os.path.getsize(expected_path) > 1000:
                logging.debug(f"  文件已下载：{os.path.getsize(expected_path)} bytes")
                return True
            
            # 检查是否有.crdownload临时文件（Chrome下载中）
            temp_files = glob.glob(os.path.join(self.pdf_dir, "*.crdownload"))
            if not temp_files and i > 5:  # 5秒后还没有临时文件，可能下载失败
                # 检查目录中是否有新下载的PDF
                recent_pdfs = glob.glob(os.path.join(self.pdf_dir, "*.pdf"))
                for pdf in recent_pdfs:
                    if os.path.getmtime(pdf) > time.time() - 30:  # 30秒内的文件
                        # 可能是刚下载的，重命名为期望的文件名
                        if not os.path.exists(expected_path):
                            try:
                                os.rename(pdf, expected_path)
                                logging.debug(f"  重命名文件：{os.path.basename(pdf)} -> {os.path.basename(expected_path)}")
                                return True
                            except:
                                pass
        
        logging.warning(f"  下载超时：{filename}")
        return False
    
    def save_results(self, query_id, query_text, result_data):
        """保存单个检索式的结果"""
        filename = f"{self.output_dir}/query_{query_id}_results.json"
        
        output_data = {
            'query_id': query_id,
            'query_text': query_text,
            'crawl_time': datetime.now().isoformat(),
            'total_results': result_data.get('total_results', 'N/A'),
            'articles_count': result_data.get('articles_count', 0),
            'articles': result_data.get('articles', [])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"结果已保存到：{filename}")
    
    def run(self, start_from=1):
        """运行爬虫"""
        try:
            # 初始化浏览器
            self.init_driver()
            
            # 加载检索式
            queries = self.load_queries()
            
            # 过滤已完成的
            remaining_queries = [q for q in queries if q['id'] not in self.progress['completed']]
            
            if start_from > 1:
                remaining_queries = [q for q in remaining_queries if int(q['id']) >= start_from]
            
            logging.info(f"待爬取：{len(remaining_queries)} 个检索式")
            
            for idx, query in enumerate(remaining_queries, 1):
                query_id = query['id']
                query_text = query['text']
                
                logging.info(f"\n{'='*60}")
                logging.info(f"进度：{idx}/{len(remaining_queries)} | 检索式 #{query_id}")
                logging.info(f"检索式：{query_text[:100]}...")
                logging.info(f"{'='*60}\n")
                
                # 执行搜索
                result = self.search_query(query_text)
                
                if result['success']:
                    # 保存结果
                    self.save_results(query_id, query_text, result)
                    
                    # 标记为完成
                    self.progress['completed'].append(query_id)
                    self.progress['last_query_time'] = datetime.now().isoformat()
                    self.save_progress()
                    
                    logging.info(f"✓ 检索式 #{query_id} 完成")
                else:
                    # 标记为失败
                    self.progress['failed'].append({
                        'query_id': query_id,
                        'error': result.get('error', 'unknown'),
                        'time': datetime.now().isoformat()
                    })
                    self.save_progress()
                    
                    logging.error(f"✗ 检索式 #{query_id} 失败")
                
                # 如果不是最后一个，则等待
                if idx < len(remaining_queries):
                    self.safe_delay('large')
            
            logging.info("\n" + "="*60)
            logging.info("✅ 所有检索式爬取完成！")
            logging.info(f"成功：{len(self.progress['completed'])} 个")
            logging.info(f"失败：{len(self.progress['failed'])} 个")
            logging.info("="*60)
            
        except KeyboardInterrupt:
            logging.info("\n用户中断爬取")
        except Exception as e:
            logging.error(f"爬虫运行出错：{e}")
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("浏览器已关闭")


def main():
    """主函数"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           IEEE Xplore 文献检索爬虫 v1.0                  ║
    ║                                                           ║
    ║  ⚠️  安全设置：                                           ║
    ║     - 查询间隔：60-120秒随机延迟                         ║
    ║     - 模拟真实浏览器行为                                 ║
    ║     - 自动保存进度，支持断点续爬                         ║
    ║                                                           ║
    ║  📁 输出目录：ieee_results/                              ║
    ║  📋 日志文件：ieee_crawler.log                           ║
    ║  💾 进度文件：crawl_progress.json                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 创建爬虫实例
    crawler = IEEECrawler()
    
    # 检查是否有未完成的任务
    if crawler.progress['completed']:
        print(f"\n📊 检测到之前的爬取进度：")
        print(f"   已完成：{len(crawler.progress['completed'])} 个检索式")
        print(f"   失败：{len(crawler.progress['failed'])} 个检索式")
        
        choice = input("\n是否继续之前的进度？(y/n): ").strip().lower()
        if choice != 'y':
            choice = input("是否从头开始？这将清除之前的进度 (y/n): ").strip().lower()
            if choice == 'y':
                crawler.progress = {'completed': [], 'failed': [], 'last_query_time': None}
                crawler.save_progress()
                print("✓ 进度已重置")
    
    print("\n🚀 开始爬取...\n")
    
    # 运行爬虫
    crawler.run()


if __name__ == "__main__":
    main()

