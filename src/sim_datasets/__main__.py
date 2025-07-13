#!/usr/bin/env python3
"""
sim-datasets 命令行接口

使用方法:
    python -m sim_datasets <config_name> [options]
    
示例:
    python -m sim_datasets llm-srbench
    python -m sim_datasets srbench1.0 --source huggingface
    python -m sim_datasets srsd --parallel --max-workers 10
"""

import argparse
import sys
from pathlib import Path

from .utils import (
    get_datasets_list,
    download_dataset,
    download_dataset_parallel
)


def main():
    """主函数，处理命令行参数并执行相应的操作"""
    parser = argparse.ArgumentParser(
        description="下载和管理符号回归数据集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s llm-srbench                    # 下载 llm-srbench 数据集
  %(prog)s srbench1.0 --source huggingface  # 从 Hugging Face 下载
  %(prog)s srsd --parallel --max-workers 10  # 并行下载，最大10个进程
  %(prog)s bio_pop_growth --proxy http://proxy:8080  # 使用代理
        """
    )
    
    parser.add_argument(
        "config_name",
        help="数据集配置名称 (例如: llm-srbench, srbench1.0, srsd, bio_pop_growth)"
    )
    
    parser.add_argument(
        "--source",
        choices=["modelscope", "huggingface"],
        default="modelscope",
        help="数据源 (默认: modelscope)"
    )
    
    parser.add_argument(
        "--proxy",
        default="",
        help="代理地址 (例如: http://proxy:8080)"
    )
    
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="缓存目录 (默认: 当前目录下的 .sim_datasets)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="使用并行下载"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="并行下载时的最大进程数 (默认: 5)"
    )
    
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="仅列出数据集，不下载"
    )
    
    args = parser.parse_args()
    
    try:
        # 获取数据集列表
        print(f"正在获取数据集列表: {args.config_name}")
        datasets_list = get_datasets_list(args.config_name)
        
        print(f"找到 {len(datasets_list)} 个数据集:")
        for i, dataset in enumerate(datasets_list, 1):
            print(f"  {i:2d}. {dataset}")
        
        if args.list_only:
            return 0
        
        print(f"\n开始下载数据集...")
        print(f"数据源: {args.source}")
        if args.proxy:
            print(f"代理: {args.proxy}")
        if args.parallel:
            print(f"并行下载，最大进程数: {args.max_workers}")
        
        # 执行下载
        if args.parallel:
            result = download_dataset_parallel(
                config_name=args.config_name,
                source=args.source,
                proxy=args.proxy,
                cache_dir=args.cache_dir,
                max_workers=args.max_workers
            )
        else:
            result = download_dataset(
                config_name=args.config_name,
                source=args.source,
                proxy=args.proxy,
                cache_dir=args.cache_dir
            )
        
        # 显示结果
        print(f"\n下载完成!")
        print(f"缓存目录: {result['cache_dir']}")
        print(f"总数据集数: {result['total_datasets']}")
        print(f"成功: {result['success_count']}")
        print(f"失败: {result['failed_count']}")
        
        if result.get('failed'):
            print(f"\n失败的数据集:")
            for dataset in result['failed']:
                print(f"  - {dataset}")
        
        return 0 if result['failed_count'] == 0 else 1
        
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        print(f"请检查数据集名称 '{args.config_name}' 是否正确", file=sys.stderr)
        return 1
        
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
        
    except KeyboardInterrupt:
        print(f"\n用户中断下载", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 