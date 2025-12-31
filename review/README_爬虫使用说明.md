# IEEE Xplore 文献检索爬虫 - 使用说明

## 📋 功能特点

✅ **安全防封**：60-120秒随机延迟，模拟真实用户行为  
✅ **断点续爬**：自动保存进度，支持中断后继续  
✅ **智能提取**：自动提取标题、作者、摘要、年份等信息  
✅ **结构化存储**：JSON格式保存，方便后续分析  
✅ **详细日志**：实时记录爬取状态和错误信息  

---

## 🔧 环境配置

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Chrome浏览器

确保系统已安装 **Google Chrome** 浏览器（最新版本）

### 3. 安装ChromeDriver

**方法一：自动安装（推荐）**

```python
# 修改 ieee_crawler.py，添加以下代码
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# 在 init_driver() 方法中修改为：
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=options)
```

**方法二：手动安装**

1. 查看Chrome版本：`chrome://version/`
2. 下载对应版本的ChromeDriver：https://chromedriver.chromium.org/
3. 将 `chromedriver.exe` 放到系统PATH目录

---

## 🚀 运行爬虫

### 基础运行

```bash
python ieee_crawler.py
```

### 从指定检索式开始

在 `main()` 函数中修改：

```python
crawler.run(start_from=10)  # 从第10个检索式开始
```

---

## 📊 输出文件

### 1. 检索结果 `ieee_results/`

每个检索式生成一个JSON文件：

```
ieee_results/
├── query_1_results.json
├── query_2_results.json
├── ...
└── query_80_results.json
```

**JSON文件结构：**

```json
{
  "query_id": "1",
  "query_text": "检索式内容",
  "crawl_time": "2024-11-19T10:30:00",
  "total_results": "1,234 results",
  "articles_count": 25,
  "articles": [
    {
      "title": "文章标题",
      "link": "https://ieeexplore.ieee.org/document/...",
      "authors": "作者名",
      "publisher_info": "期刊/会议名",
      "year": "2024",
      "abstract": "摘要内容"
    }
  ]
}
```

### 2. 进度文件 `crawl_progress.json`

```json
{
  "completed": ["1", "2", "3"],
  "failed": [],
  "last_query_time": "2024-11-19T10:30:00"
}
```

### 3. 日志文件 `ieee_crawler.log`

记录详细的运行日志，包括：
- 每个检索式的执行状态
- 提取的文献数量
- 错误和警告信息

---

## ⚙️ 配置参数

在 `ieee_crawler.py` 的 `__init__` 方法中可调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `min_delay` | 60秒 | 查询间最小延迟 |
| `max_delay` | 120秒 | 查询间最大延迟 |
| `small_delay_min` | 3秒 | 页面操作最小延迟 |
| `small_delay_max` | 8秒 | 页面操作最大延迟 |

### 调整频率示例

```python
# 更保守（3倍延迟，不容易被封）
self.min_delay = 90  
self.max_delay = 180

# 更快速（有风险）
self.min_delay = 30  
self.max_delay = 60
```

---

## ⚠️ 注意事项

### 1. 遵守IEEE使用条款

- ✅ 仅用于学术研究
- ❌ 禁止商业用途
- ❌ 禁止批量下载PDF全文

### 2. 网络要求

- 需要有权访问IEEE Xplore（校园网或VPN）
- 如果需要下载全文，需要机构订阅权限

### 3. 时间估算

- 80个检索式 × 平均90秒/个 = **约2小时**
- 建议在网络稳定时运行
- 可以随时中断，下次自动继续

### 4. 如何避免被封

✅ **已实现的保护措施：**
- 随机延迟（60-120秒）
- 模拟真实浏览器
- 设置User-Agent
- 禁用自动化检测特征

✅ **额外建议：**
- 不要在短时间内重复爬取相同内容
- 如果出现验证码或403错误，立即停止
- 可以使用校园网的不同IP轮换

---

## 🛠️ 常见问题

### Q1: 提示"ChromeDriver版本不匹配"

**解决方法：**
```bash
pip install webdriver-manager
```

然后使用自动安装模式（见上文配置部分）

### Q2: 无法提取到文献信息

可能原因：
1. IEEE页面结构更新 → 需要更新元素选择器
2. 网络延迟 → 增加等待时间
3. 需要登录 → 添加登录逻辑

### Q3: 爬取速度太慢

**谨慎调整延迟：**
```python
self.min_delay = 45  # 不建议低于45秒
self.max_delay = 90
```

### Q4: 如何只爬取前N页

修改 `extract_articles()` 方法，添加翻页逻辑：

```python
for page in range(max_pages):
    articles.extend(self.extract_current_page())
    self.click_next_page()
    self.safe_delay('small')
```

---

## 📈 数据分析

爬取完成后，可以使用以下脚本合并结果：

```python
import json
import glob

all_articles = []
for file in glob.glob('ieee_results/*.json'):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_articles.extend(data['articles'])

print(f"总共爬取了 {len(all_articles)} 篇文献")

# 导出为CSV
import pandas as pd
df = pd.DataFrame(all_articles)
df.to_csv('all_articles.csv', index=False, encoding='utf-8-sig')
```

---

## 📞 技术支持

如遇到问题：

1. 查看 `ieee_crawler.log` 日志文件
2. 检查 `crawl_progress.json` 确认进度
3. 查看IEEE Xplore是否更新了页面结构

---

## 📝 更新日志

**v1.0 (2024-11-19)**
- ✨ 初始版本
- ✅ 支持80个检索式批量爬取
- ✅ 安全防封机制
- ✅ 断点续爬功能

---

## ⏱️ 预计完成时间

| 检索式数量 | 延迟设置 | 预计时间 |
|-----------|---------|----------|
| 80个 | 60-120秒 | 约2小时 |
| 80个 | 90-180秒 | 约3小时 |
| 80个 | 30-60秒 | 约1小时（有风险）|

**建议：** 在晚上或周末运行，让程序自动完成。

---

## 🎯 下一步

1. ✅ 运行爬虫
2. ⏳ 等待完成（约2小时）
3. 📊 分析结果数据
4. 📄 导出为Excel/CSV
5. 📚 进行文献综述

祝科研顺利！🎓


