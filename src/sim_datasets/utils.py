def check_ip_location(proxy: str = "") -> bool:
    """
    检查当前IP是否在中国大陆
    
    Args:
        proxy: 代理地址，空字符串表示不使用代理
        
    Returns:
        True表示在大陆，False表示非大陆
    """
    import requests
    
    # 设置代理
    proxies = {}
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        print(f"使用代理检测IP位置: {proxy}")
    
    try:
        # 使用多个服务来确保准确性
        services = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/',
        ]
        
        for service in services:
            try:
                response = requests.get(service, proxies=proxies, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查不同服务的返回格式
                    country = None
                    if 'country' in data:
                        country = data['country']
                    elif 'country_name' in data:
                        country = data['country_name']
                    
                    if country:
                        print(f"检测到IP所在国家: {country}")
                        return country.lower() in ['china', 'cn', '中国']
                        
            except Exception as e:
                print(f"服务 {service} 检测失败: {e}")
                continue
                
        # 如果所有服务都失败，默认假设在大陆
        print("IP位置检测失败，默认使用ModelScope")
        return True
        
    except Exception as e:
        print(f"IP检测过程中发生错误: {e}")
        return True


def auto_select_source(proxy: str = "") -> str:
    """
    根据IP位置自动选择下载源
    
    Args:
        proxy: 代理地址，空字符串表示不使用代理
        
    Returns:
        "modelscope" 或 "huggingface"
    """
    is_china = check_ip_location(proxy=proxy)
    if is_china:
        print("检测到中国IP，使用ModelScope下载源")
        return "modelscope"
    else:
        print("检测到海外IP，使用HuggingFace下载源")
        return "huggingface"


def get_datasets_list(config_name: str) -> list:
    """
    根据数据集名称读取对应的配置文件，返回数据集列表。
    
    Args:
        config_name: 数据集名称，支持以下格式：
            - 简单名称：'llm-srbench', 'srbench1.0', 'srsd'
            - 子数据集：'bio_pop_growth', 'chem_react', 'lsrtransform', 'matsci', 'phys_osc'
            - 完整路径：'llm-srbench/bio_pop_growth', 'srbench1.0/feynman', 'srsd/srsd-feynman_easy'
    
    Returns:
        数据集列表，每个元素是一个字符串
        
    Raises:
        ValueError: 当数据集名称无效时
        FileNotFoundError: 当配置文件不存在时
    """
    import os
    from pathlib import Path
    
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    configs_dir = current_dir / "configs"
    
    # 将路径中的"/"转换为"."来匹配文件名
    config_filename = config_name.replace("/", ".") + ".txt"
    config_file_path = configs_dir / config_filename
    
    # 检查文件是否存在
    if not config_file_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file_path}")
    
    # 读取配置文件
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            # 读取所有行，去除空白字符，过滤掉空行
            datasets = [line.strip() for line in f.readlines() if line.strip()]
        
        return datasets
        
    except Exception as e:
        raise ValueError(f"读取配置文件失败 {config_file_path}: {e}")
    

def download_single_dataset(dataset_name: str, source: str = None, proxy="", cache_dir=None):
    """
    下载单个数据集的 package.tar.gz 文件，解压后删除压缩包。
    
    Args:
        dataset_name: 数据集名称，格式如 "llm-srbench/bio_pop_growth/BPG0"
        source: 数据源，支持 "modelscope" 或 "huggingface"，如果为None则自动根据IP位置选择
        proxy: 代理地址，空字符串表示不使用代理
        cache_dir: 缓存目录，如果为None则使用默认目录
        
    Returns:
        下载的数据集内容字典
    """
    import requests
    from pathlib import Path
    import tarfile
    import shutil
    
    # 如果未指定数据源，自动选择
    if source is None:
        source = auto_select_source(proxy=proxy)
    
    source = source.lower()

    # 设置代理
    proxies = {}
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
    
    # 构建 package.tar.gz 的 URL
    if source == 'huggingface':
        base_url = f"https://huggingface.co/datasets/scientific-intelligent-modelling/sim-datasets/resolve/main/{dataset_name}"
    else:  # ModelScope
        base_url = f"https://modelscope.cn/datasets/scientific-intelligent-modelling/sim-datasets/resolve/master/{dataset_name}"
    
    tar_filename = 'package.tar.gz'
    download_url = f"{base_url}/{tar_filename}"

    print(f"从 {source} 下载 {dataset_name} 的 {tar_filename} ...")

    dataset_data = {
        'dataset_name': dataset_name,
        'source': source,
        'files': {},
        'total_size': 0,
        'cache_path': None
    }

    # 创建数据集目录，保持原始目录结构
    if cache_dir:
        dataset_dir = cache_dir / Path(dataset_name)
    else:
        dataset_dir = Path.cwd() / ".sim_datasets"  / Path(dataset_name)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    dataset_data['cache_path'] = str(dataset_dir)

    tar_path = dataset_dir / tar_filename

    # 下载 package.tar.gz
    if not tar_path.exists():
        try:
            print(f"  下载 {tar_filename} ...")
            response = requests.get(download_url, proxies=proxies, timeout=60, stream=True)
            if response.status_code == 200:
                with open(tar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                file_size = tar_path.stat().st_size
                
                # 验证下载的文件是否为有效的tar.gz文件
                try:
                    with tarfile.open(tar_path, 'r:gz') as test_tar:
                        # 尝试读取文件列表来验证格式
                        test_tar.getnames()
                    print(f"  ✅ {tar_filename} 已保存到 {tar_path} (已验证格式)")
                except tarfile.ReadError:
                    # 如果不是有效的tar.gz文件，可能是HTML错误页面，删除并报错
                    tar_path.unlink()
                    error_msg = f"下载的文件不是有效的tar.gz格式，可能是404错误页面"
                    print(f"  ❌ {error_msg}")
                    dataset_data['files'][tar_filename] = {
                        'path': None,
                        'size': 0,
                        'url': download_url,
                        'error': error_msg
                    }
                    return dataset_data
                
                dataset_data['files'][tar_filename] = {
                    'path': str(tar_path),
                    'size': file_size,
                    'url': download_url
                }
                dataset_data['total_size'] += file_size
                print(f"  ✅ {tar_filename} 已保存到 {tar_path}")
            else:
                print(f"  下载 {tar_filename} 失败: HTTP {response.status_code}")
                dataset_data['files'][tar_filename] = {
                    'path': None,
                    'size': 0,
                    'url': download_url,
                    'error': f"HTTP {response.status_code}"
                }
                return dataset_data
        except Exception as e:
            print(f"  下载 {tar_filename} 失败: {e}")
            dataset_data['files'][tar_filename] = {
                'path': None,
                'size': 0,
                'url': download_url,
                'error': str(e)
            }
            return dataset_data
    else:
        print(f"{tar_filename} 已缓存")

    # 解压 package.tar.gz
    try:
        print(f"  解压 {tar_path} ...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path=dataset_dir)
        print(f"  ✅ 解压完成")
        # 删除压缩包
        tar_path.unlink()
        print(f"  已删除 {tar_path}")
    except Exception as e:
        print(f"  解压或删除 {tar_path} 失败: {e}")
        dataset_data['files']['extract_error'] = str(e)

    return dataset_data



def download_dataset(config_name: str, source: str = None, proxy="", cache_dir=None):
    """
    下载指定的数据集。
    
    Args:
        config_name: 数据集名称
        source: 数据源，支持 "modelscope" 或 "huggingface"，如果为None则自动根据IP位置选择
        proxy: 代理地址，空字符串表示不使用代理
        cache_dir: 缓存目录，如果为None则使用默认目录
    Returns:
        下载结果
    """
    import os
    from pathlib import Path
    
    # 如果未指定数据源，自动选择
    if source is None:
        source = auto_select_source(proxy=proxy)
    
    # 获取数据集列表
    datasets_list = get_datasets_list(config_name)
    
    # 设置缓存目录为当前工作目录
    cache_dir = Path.cwd() / ".sim_datasets" 
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置代理环境变量
    if proxy:
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
    
    downloaded_datasets = []
    failed_datasets = []
    
    for dataset_name in datasets_list:
        dataset_dir = cache_dir / Path(dataset_name)
        
        # 检查是否已经缓存（检查目录是否存在且包含文件）
        if dataset_dir.exists() and any(dataset_dir.iterdir()):
            print(f"数据集 {dataset_name} 已缓存，跳过下载")
            downloaded_datasets.append(dataset_name)
            continue
        
        try:
            # 下载单个数据集，使用已测试的源
            result = download_single_dataset(dataset_name, source=source, proxy=proxy, cache_dir=cache_dir)
            
            downloaded_datasets.append(dataset_name)
            print(f"数据集 {dataset_name} 下载完成并保存到 {result['cache_path']}")
            
        except Exception as e:
            print(f"数据集 {dataset_name} 下载失败: {e}")
            failed_datasets.append(dataset_name)
    
    # 清理代理环境变量
    if proxy:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
    
    return {
        "config_name": config_name,
        "cache_dir": str(cache_dir),
        "total_datasets": len(datasets_list),
        "downloaded": downloaded_datasets,
        "failed": failed_datasets,
        "success_count": len(downloaded_datasets),
        "failed_count": len(failed_datasets),
    }



def download_dataset_parallel(config_name: str, source: str = None, proxy="", cache_dir=None, max_workers: int = 5):
    """
    使用多进程并发下载指定的数据集。
    
    Args:
        config_name: 数据集名称
        source: 数据源，支持 "modelscope" 或 "huggingface"，如果为None则自动根据IP位置选择
        proxy: 代理地址，空字符串表示不使用代理
        cache_dir: 缓存目录，如果为None则使用默认目录
        max_workers: 最大并发进程数，默认为5
        
    Returns:
        下载结果
    """
    import os
    import multiprocessing as mp
    from pathlib import Path
    from functools import partial
    
    # 如果未指定数据源，自动选择
    if source is None:
        source = auto_select_source(proxy=proxy)
    
    # 获取数据集列表
    datasets_list = get_datasets_list(config_name)
    
    # 设置缓存目录
    if cache_dir is None:
        cache_dir = Path.cwd() / ".sim_datasets"
    else:
        cache_dir = Path(cache_dir)
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置代理环境变量
    if proxy:
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
    
    # 创建下载单个数据集的包装函数
    def download_single_wrapper(dataset_name):
        """包装函数，用于多进程调用"""
        try:
            dataset_dir = cache_dir / Path(dataset_name)
            
            # 检查是否已经缓存
            if dataset_dir.exists() and any(dataset_dir.iterdir()):
                print(f"数据集 {dataset_name} 已缓存，跳过下载")
                return {"dataset_name": dataset_name, "status": "cached", "error": None}
            
            # 下载数据集
            result = download_single_dataset(dataset_name, source=source, proxy=proxy, cache_dir=cache_dir)
            print(f"数据集 {dataset_name} 下载完成")
            return {"dataset_name": dataset_name, "status": "success", "result": result, "error": None}
            
        except Exception as e:
            print(f"数据集 {dataset_name} 下载失败: {e}")
            return {"dataset_name": dataset_name, "status": "failed", "error": str(e)}
    
    # 使用进程池进行并发下载
    print(f"开始并发下载 {len(datasets_list)} 个数据集，最大并发数: {max_workers}")
    
    downloaded_datasets = []
    failed_datasets = []
    cached_datasets = []
    
    # 限制并发数不超过数据集数量
    actual_workers = min(max_workers, len(datasets_list))
    
    with mp.Pool(processes=actual_workers) as pool:
        # 使用map进行并发处理
        results = pool.map(download_single_wrapper, datasets_list)
    
    # 处理结果
    for result in results:
        dataset_name = result["dataset_name"]
        status = result["status"]
        
        if status == "success":
            downloaded_datasets.append(dataset_name)
        elif status == "failed":
            failed_datasets.append(dataset_name)
        elif status == "cached":
            cached_datasets.append(dataset_name)
    
    # 清理代理环境变量
    if proxy:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
    
    print(f"\n下载完成统计:")
    print(f"  总数据集数: {len(datasets_list)}")
    print(f"  成功下载: {len(downloaded_datasets)}")
    print(f"  已缓存: {len(cached_datasets)}")
    print(f"  失败: {len(failed_datasets)}")
    
    return {
        "config_name": config_name,
        "cache_dir": str(cache_dir),
        "total_datasets": len(datasets_list),
        "downloaded": downloaded_datasets,
        "cached": cached_datasets,
        "failed": failed_datasets,
        "success_count": len(downloaded_datasets) + len(cached_datasets),
        "failed_count": len(failed_datasets),
        "max_workers": actual_workers,
    }


