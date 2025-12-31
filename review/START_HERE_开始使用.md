# 🚀 IEEE Xplore 爬虫 - 立即开始

## ✅ 测试已通过！

爬虫功能已验证正常，可以开始使用了！

---

## 📝 快速开始（3步）

### **第1步：运行正式爬取**

```bash
python ieee_crawler.py
```

这将爬取所有80个检索式，每个检索式爬取**5页**（最多125篇文献）。

⏱️ **预计耗时：约2-3小时**（80个检索式 × 平均90秒）

### **第2步：查看进度**

爬取过程中，您可以：
- 查看终端输出（实时显示进度）
- 查看日志文件：`ieee_crawler.log`
- 查看进度文件：`crawl_progress.json`

### **第3步：分析结果**

爬取完成后：

```bash
python analyze_results.py
```

可以：
- 📊 查看统计信息
- 💾 导出为CSV/Excel
- 🔄 自动去重
- 🔍 按关键词搜索

---

## 🎯 当前配置

| 设置项 | 值 | 说明 |
|--------|---|------|
| 检索式数量 | 80个 | 来自CSV文件 |
| 每个检索式页数 | 5页 | 可在代码中修改 `max_pages` |
| 每页文献数 | 约25篇 | IEEE默认 |
| 查询间延迟 | 60-120秒 | 随机延迟，2倍安全系数 |
| 预计总文献数 | 约10,000篇 | 80 × 5 × 25（实际可能更少） |

---

## ⚙️ 调整配置（可选）

### 修改爬取页数

编辑 `ieee_crawler.py`，找到第44-45行：

```python
# 多页爬取设置
self.max_pages = 5  # 改为你想要的页数，如10
self.results_per_page = 25
```

### 修改延迟时间

编辑 `ieee_crawler.py`，找到第35-37行：

```python
# 频率控制
self.min_delay = 60   # 改为更大的值更安全
self.max_delay = 120  # 改为更大的值更安全
```

### 从指定检索式开始

如果需要跳过前面的检索式，编辑 `ieee_crawler.py` 的最后部分：

```python
# 运行爬虫
crawler.run(start_from=10)  # 从第10个检索式开始
```

---

## 📁 输出文件

爬取完成后，您将获得：

```
ieee_results/
├── query_1_results.json    ← 第1个检索式的结果
├── query_2_results.json    ← 第2个检索式的结果
├── ...
└── query_80_results.json   ← 第80个检索式的结果

crawl_progress.json          ← 爬取进度（可断点续爬）
ieee_crawler.log             ← 详细日志
```

每个JSON文件包含：
- 检索式信息
- 文献总数
- 文献列表（标题、作者、年份、摘要、链接等）

---

## 🔄 断点续爬

如果爬取过程中断（按Ctrl+C或网络问题），**不用担心**！

再次运行 `python ieee_crawler.py`，会自动：
- ✅ 跳过已完成的检索式
- ✅ 从中断处继续
- ✅ 保留之前的结果

---

## 📊 查看测试结果

测试已经成功爬取了第1个检索式：

```bash
cat ieee_results/query_1_results.json
```

或在Windows中：

```cmd
type ieee_results\query_1_results.json
```

---

## ⚠️ 重要提示

### 安全使用

✅ **已实施的保护措施：**
- 60-120秒随机延迟（2倍安全系数）
- 模拟真实浏览器行为
- 自动滚动加载（避免遗漏）
- 多种元素选择器（适应页面变化）

✅ **使用建议：**
- 在网络稳定时运行
- 建议晚上或周末运行
- 可随时中断，自动保存进度
- 遵守IEEE使用条款

### 如果遇到问题

1. **速度太慢**：已经是2倍安全延迟，建议保持
2. **某些检索式失败**：查看日志，可能该检索式无结果
3. **被要求验证**：停止爬取，等待一段时间后继续
4. **ChromeDriver问题**：已使用自动管理，应该不会出现

---

## 🎯 下一步

### 选项A：立即开始正式爬取

```bash
python ieee_crawler.py
```

### 选项B：先分析测试结果

```bash
python analyze_results.py
```

### 选项C：再次测试（验证稳定性）

```bash
python test_crawler.py
```

---

## 📈 预期结果

基于当前配置，完成后您将获得：

- ✅ **80个JSON文件**（每个检索式一个）
- ✅ **约5,000-10,000篇文献**（去重后）
- ✅ **完整的元数据**（标题、作者、年份、摘要、链接）
- ✅ **可导出为CSV/Excel**（便于分析）

---

## 💡 使用技巧

### 后台运行（Windows PowerShell）

```powershell
Start-Process python -ArgumentList "ieee_crawler.py" -NoNewWindow -RedirectStandardOutput "output.log"
```

### 查看实时日志

```bash
# 另开一个终端
tail -f ieee_crawler.log  # Linux/Mac
Get-Content ieee_crawler.log -Wait  # Windows PowerShell
```

### 查看当前进度

```bash
python -c "import json; p=json.load(open('crawl_progress.json')); print(f'已完成：{len(p[\"completed\"])} 个')"
```

---

## 🎉 准备好了吗？

**测试已通过**，多页爬取功能正常！

现在运行：

```bash
python ieee_crawler.py
```

让爬虫为您收集所有文献数据！☕ 喝杯咖啡，等待2-3小时后回来查看结果。

---

## 📞 需要帮助？

查看详细文档：
- **README_爬虫使用说明.md** - 完整使用文档
- **快速开始.txt** - 命令速查
- **ieee_crawler.log** - 运行日志

祝科研顺利！🎓


