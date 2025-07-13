#!/usr/bin/env python3
"""
sim-datasets 安装脚本

使用方法:
    python install.py [--dev] [--test]
    
选项:
    --dev    安装开发依赖
    --test   安装后运行测试
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败:")
        print(f"   命令: {cmd}")
        print(f"   错误: {e.stderr}")
        return False


def install_package(dev=False):
    """安装包"""
    if dev:
        cmd = "pip install -e .[dev]"
        description = "安装 sim-datasets 包（包含开发依赖）"
    else:
        cmd = "pip install -e ."
        description = "安装 sim-datasets 包"
    
    return run_command(cmd, description)


def run_tests():
    """运行测试"""
    return run_command("python test_basic.py", "运行基本功能测试")


def main():
    """主函数"""
    print("🚀 sim-datasets 安装脚本")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not Path("pyproject.toml").exists():
        print("❌ 错误: 请在包含 pyproject.toml 的目录中运行此脚本")
        sys.exit(1)
    
    # 解析命令行参数
    dev_mode = "--dev" in sys.argv
    test_mode = "--test" in sys.argv
    
    print(f"📦 安装模式: {'开发模式' if dev_mode else '标准模式'}")
    print(f"🧪 测试模式: {'启用' if test_mode else '禁用'}")
    print()
    
    # 安装包
    if not install_package(dev_mode):
        print("\n❌ 安装失败，请检查错误信息")
        sys.exit(1)
    
    # 运行测试（如果启用）
    if test_mode:
        print("\n" + "=" * 50)
        if not run_tests():
            print("\n⚠️  测试失败，但包已安装")
        else:
            print("\n🎉 安装和测试都成功完成！")
    
    print("\n📋 安装完成！")
    print("\n📖 使用示例:")
    print("  # 导入包")
    print("  from sim_datasets import get_datasets_list, download_dataset")
    print()
    print("  # 获取数据集列表")
    print("  datasets = get_datasets_list('llm-srbench')")
    print()
    print("  # 下载数据集")
    print("  result = download_dataset('llm-srbench')")
    print()
    print("  # 命令行使用")
    print("  python -m sim_datasets llm-srbench")
    print()
    print("📚 更多信息请查看 README.md")


if __name__ == "__main__":
    main() 