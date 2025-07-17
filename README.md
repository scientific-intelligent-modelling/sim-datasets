# SIM-Datasets

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-green.svg)](https://opensource.org/licenses/GPL-3.0)
[![PyPI version](https://badge.fury.io/py/sim-datasets.svg)](https://badge.fury.io/py/sim-datasets)

A unified platform solution for symbolic regression, providing comprehensive support for Scientific-Intelligent-Modeling toolkits. Seamlessly integrates with ModelScope and Hugging Face for efficient dataset access.

## 🌟 Key Features

- 🔄 **Multi-Source Support**: Simultaneously supports HuggingFace and ModelScope platforms
- ⚡ **Smart Source Selection**: Automatically selects the fastest download source
- 🚀 **Concurrent Downloads**: Supports asynchronous concurrent downloads with up to 20 concurrent tasks
- 📊 **Real-time Progress**: Displays detailed download progress and status
- 📁 **Smart Caching**: Automatically caches download results to avoid repeated downloads
- 🛠️ **Command Line Tools**: Provides convenient command-line interface
- 🔧 **Proxy Support**: Complete proxy configuration support
- 📋 **Dataset Management**: Unified dataset list and configuration management

## 📦 Installation

### Install from Source

```bash
# Clone repository
git clone https://github.com/scientific-intelligent-modelling/scientific-intelligent-modelling.git
cd scientific-intelligent-modelling

# Install dependencies
pip install -e .
```

### Install from PyPI

```bash
pip install sim-datasets
```

## 🚀 Quick Start

### Basic Usage

```python
from sim_datasets import get_datasets_list, download_dataset

# Get dataset list
datasets = get_datasets_list('llm-srbench')
print(f"Found {len(datasets)} datasets")

# Download single dataset
result = download_single_dataset('llm-srbench/bio_pop_growth/BPG0')
print(f"Dataset downloaded: {result['cache_path']}")

# Download entire dataset collection
result = download_dataset('llm-srbench')
print(f"Downloaded {len(result['downloaded'])} datasets")
```

### Advanced Usage

```python
from sim_datasets import download_dataset_parallel

# Concurrent download (recommended for large datasets)
result = download_dataset_parallel(
    'llm-srbench',
    source='huggingface',  # or 'modelscope' or None for auto-detected
    max_workers=10,        # number of concurrent workers
    proxy='http://proxy:8080'  # optional proxy
)

print(f"Successfully downloaded: {len(result['downloaded'])}")
print(f"Failed: {len(result['failed'])}")
```

## 📋 Supported Datasets

### LLM-SRBench Datasets
- **Biological Population Growth** (`bio_pop_growth`): Biological population dynamics modeling data
- **Chemical Reactions** (`chem_react`): Chemical reaction kinetics data
- **LSR Transform** (`lsrtransform`): Linear symbolic regression transform data
- **Materials Science** (`matsci`): Materials science related data
- **Physical Oscillations** (`phys_osc`): Physical oscillation system data

### SRBench 1.0 Datasets
- **Feynman Equations** (`feynman`): Feynman physics equation data
- **Strogatz Systems** (`strogatz`): Strogatz nonlinear system data
- **Black Box Functions** (`blackbox`): Black box function data

### SRSD Datasets
- **Feynman Easy** (`srsd-feynman_easy`): Simple Feynman equations
- **Feynman Medium** (`srsd-feynman_medium`): Medium difficulty Feynman equations
- **Feynman Hard** (`srsd-feynman_hard`): Hard Feynman equations

## 📄 License

This project is licensed under the [GPL-3.0](https://opensource.org/licenses/GPL-3.0) License.

## 👥 Authors

- **Ziwen Zhang** - *Lead Developer* - [244824379@qq.com](mailto:244824379@qq.com)
- **Kai Li** - *Contributor* - [kai.li@ia.ac.cn](mailto:kai.li@ia.ac.cn)

## 🙏 Acknowledgments

Thanks to the following open source projects:

- [Hugging Face](https://huggingface.co/) - Providing dataset hosting services
- [ModelScope](https://modelscope.cn/) - Providing model and dataset platform
- [datasets](https://github.com/huggingface/datasets) - Dataset processing library

## 📞 Contact Us

- Email: [244824379@qq.com](mailto:244824379@qq.com)
- Project Homepage: [https://github.com/scientific-intelligent-modelling/scientific-intelligent-modelling](https://github.com/scientific-intelligent-modelling/scientific-intelligent-modelling)
- Issue Reports: [GitHub Issues](https://github.com/scientific-intelligent-modelling/scientific-intelligent-modelling/issues)

---

⭐ If this project helps you, please give us a star! 