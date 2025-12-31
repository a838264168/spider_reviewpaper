"""
IEEE Xplore 爬取结果分析脚本
用于合并、统计和导出爬取的文献数据
"""

import json
import glob
import os
from datetime import datetime
import csv

class ResultAnalyzer:
    def __init__(self, results_dir='ieee_results'):
        self.results_dir = results_dir
        self.all_articles = []
        self.query_stats = []
        
    def load_all_results(self):
        """加载所有结果文件"""
        result_files = glob.glob(f"{self.results_dir}/query_*_results.json")
        result_files.sort(key=lambda x: int(x.split('_')[1]))  # 按编号排序
        
        print(f"找到 {len(result_files)} 个结果文件")
        
        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 统计信息
                    query_stat = {
                        'query_id': data['query_id'],
                        'query_text': data['query_text'][:100] + '...' if len(data['query_text']) > 100 else data['query_text'],
                        'total_results': data.get('total_results', 'N/A'),
                        'articles_count': data.get('articles_count', 0),
                        'crawl_time': data.get('crawl_time', 'N/A')
                    }
                    self.query_stats.append(query_stat)
                    
                    # 收集所有文章（添加来源检索式信息）
                    for article in data.get('articles', []):
                        article['source_query_id'] = data['query_id']
                        article['source_query_text'] = data['query_text']
                        self.all_articles.append(article)
                        
                print(f"✓ 已加载：{file_path} - {data.get('articles_count', 0)} 篇文章")
                
            except Exception as e:
                print(f"✗ 加载失败：{file_path} - {e}")
        
        print(f"\n总共加载了 {len(self.all_articles)} 篇文献")
        
    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "="*80)
        print("📊 爬取结果统计")
        print("="*80)
        
        print(f"\n检索式数量：{len(self.query_stats)}")
        print(f"文献总数：{len(self.all_articles)}")
        
        # 按检索式统计
        print(f"\n{'检索式ID':<8} {'文献数':<8} {'总结果数':<15} {'爬取时间'}")
        print("-"*80)
        
        total_articles = 0
        for stat in self.query_stats:
            print(f"{stat['query_id']:<8} {stat['articles_count']:<8} {str(stat['total_results']):<15} {stat['crawl_time'][:19]}")
            total_articles += stat['articles_count']
        
        print("-"*80)
        print(f"{'合计':<8} {total_articles:<8}")
        
        # 年份分布
        years = [a.get('year', 'N/A') for a in self.all_articles]
        year_counts = {}
        for year in years:
            if year != 'N/A':
                year_counts[year] = year_counts.get(year, 0) + 1
        
        if year_counts:
            print(f"\n📅 年份分布（Top 10）：")
            sorted_years = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for year, count in sorted_years:
                print(f"  {year}: {count} 篇")
        
        # 去重统计
        unique_titles = set(a.get('title', '') for a in self.all_articles)
        print(f"\n🔄 去重后文献数：{len(unique_titles)} 篇")
        print(f"   重复文献数：{len(self.all_articles) - len(unique_titles)} 篇")
        
    def remove_duplicates(self):
        """去除重复文献（基于标题）"""
        seen_titles = set()
        unique_articles = []
        
        for article in self.all_articles:
            title = article.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        print(f"\n去重前：{len(self.all_articles)} 篇")
        print(f"去重后：{len(unique_articles)} 篇")
        
        return unique_articles
    
    def export_to_csv(self, output_file='all_articles.csv', remove_duplicates=True):
        """导出为CSV文件"""
        if not self.all_articles:
            print("没有数据可导出")
            return
        
        articles = self.remove_duplicates() if remove_duplicates else self.all_articles
        
        print(f"\n📝 正在导出到 {output_file}...")
        
        # 定义CSV字段
        fieldnames = [
            'title', 'authors', 'year', 'publisher_info', 
            'abstract', 'link', 'source_query_id', 'source_query_text'
        ]
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                row = {field: article.get(field, 'N/A') for field in fieldnames}
                writer.writerow(row)
        
        print(f"✓ 导出完成：{len(articles)} 篇文献")
        print(f"  文件位置：{os.path.abspath(output_file)}")
    
    def export_to_excel(self, output_file='all_articles.xlsx', remove_duplicates=True):
        """导出为Excel文件（需要pandas和openpyxl）"""
        try:
            import pandas as pd
            
            if not self.all_articles:
                print("没有数据可导出")
                return
            
            articles = self.remove_duplicates() if remove_duplicates else self.all_articles
            
            print(f"\n📊 正在导出到 {output_file}...")
            
            df = pd.DataFrame(articles)
            
            # 重新排列列顺序
            column_order = [
                'title', 'authors', 'year', 'publisher_info', 
                'abstract', 'link', 'source_query_id', 'source_query_text'
            ]
            
            # 只保留存在的列
            column_order = [col for col in column_order if col in df.columns]
            df = df[column_order]
            
            # 导出
            df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"✓ 导出完成：{len(articles)} 篇文献")
            print(f"  文件位置：{os.path.abspath(output_file)}")
            
        except ImportError:
            print("✗ 需要安装 pandas 和 openpyxl：")
            print("  pip install pandas openpyxl")
    
    def export_query_stats(self, output_file='query_statistics.csv'):
        """导出检索式统计信息"""
        print(f"\n📋 正在导出统计信息到 {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['query_id', 'query_text', 'total_results', 'articles_count', 'crawl_time']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.query_stats)
        
        print(f"✓ 导出完成")
        print(f"  文件位置：{os.path.abspath(output_file)}")
    
    def search_by_keyword(self, keyword):
        """按关键词搜索文献"""
        results = []
        keyword_lower = keyword.lower()
        
        for article in self.all_articles:
            title = article.get('title', '').lower()
            abstract = article.get('abstract', '').lower()
            
            if keyword_lower in title or keyword_lower in abstract:
                results.append(article)
        
        print(f"\n🔍 搜索关键词 '{keyword}'：找到 {len(results)} 篇相关文献")
        
        for idx, article in enumerate(results[:10], 1):  # 只显示前10个
            print(f"\n{idx}. {article.get('title', 'N/A')}")
            print(f"   作者：{article.get('authors', 'N/A')}")
            print(f"   年份：{article.get('year', 'N/A')}")
        
        if len(results) > 10:
            print(f"\n... 还有 {len(results) - 10} 篇")
        
        return results


def main():
    """主函数"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         IEEE Xplore 结果分析工具 v1.0                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    analyzer = ResultAnalyzer()
    
    # 加载所有结果
    print("📂 正在加载结果文件...\n")
    analyzer.load_all_results()
    
    if not analyzer.all_articles:
        print("\n⚠️  没有找到任何结果文件！")
        print("   请先运行 ieee_crawler.py 进行爬取")
        return
    
    # 显示统计信息
    analyzer.print_statistics()
    
    # 导出选项
    print("\n" + "="*80)
    print("📤 导出选项")
    print("="*80)
    
    while True:
        print("\n请选择操作：")
        print("  1. 导出为CSV（推荐，去重）")
        print("  2. 导出为CSV（保留重复）")
        print("  3. 导出为Excel（需要安装pandas）")
        print("  4. 导出检索式统计信息")
        print("  5. 按关键词搜索")
        print("  6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            analyzer.export_to_csv('all_articles_unique.csv', remove_duplicates=True)
        elif choice == '2':
            analyzer.export_to_csv('all_articles_all.csv', remove_duplicates=False)
        elif choice == '3':
            analyzer.export_to_excel('all_articles.xlsx', remove_duplicates=True)
        elif choice == '4':
            analyzer.export_query_stats()
        elif choice == '5':
            keyword = input("请输入关键词: ").strip()
            if keyword:
                analyzer.search_by_keyword(keyword)
        elif choice == '6':
            print("\n👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()


