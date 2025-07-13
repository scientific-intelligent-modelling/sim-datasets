#!/usr/bin/env python3
"""
基本功能测试脚本
用于验证 sim-datasets 包的安装和基本功能
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from sim_datasets import get_datasets_list, download_single_dataset
    print("✅ 成功导入 sim_datasets 包")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_get_datasets_list():
    """测试获取数据集列表功能"""
    print("\n🔍 测试获取数据集列表...")
    
    try:
        # 测试获取 llm-srbench 数据集列表
        datasets = get_datasets_list('llm-srbench')
        print(f"✅ 成功获取 llm-srbench 数据集列表，共 {len(datasets)} 个数据集")
        
        # 显示前5个数据集
        for i, dataset in enumerate(datasets[:5], 1):
            print(f"  {i}. {dataset}")
        
        if len(datasets) > 5:
            print(f"  ... 还有 {len(datasets) - 5} 个数据集")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取数据集列表失败: {e}")
        return False

def test_download_single_dataset():
    """测试下载单个数据集功能"""
    print("\n📥 测试下载单个数据集...")
    
    try:
        # 测试下载一个小的数据集
        result = download_single_dataset(
            'llm-srbench/bio_pop_growth/BPG0',
            source='huggingface'
        )
        
        print(f"✅ 成功下载数据集: {result['dataset_name']}")
        print(f"   缓存路径: {result['cache_path']}")
        print(f"   文件数量: {len(result['files'])}")
        print(f"   总大小: {result['total_size']} 字节")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载数据集失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试 sim-datasets 包...")
    
    # 测试1: 获取数据集列表
    test1_passed = test_get_datasets_list()
    
    # 测试2: 下载单个数据集
    test2_passed = test_download_single_dataset()
    
    # 总结
    print(f"\n📊 测试结果:")
    print(f"  获取数据集列表: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"  下载单个数据集: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！sim-datasets 包安装成功。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查安装和配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 