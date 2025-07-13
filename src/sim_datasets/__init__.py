"""
This software package aims to build a unified platform solution for symbolic regression, 
providing comprehensive support for Scientific-Intelligent-Modeling toolkits. 

With its thoughtfully designed user-friendly interface, the package seamlessly integrates 
with leading open-source platforms like ModelScope and Hugging Face, enabling researchers 
and developers to efficiently access symbolic regression datasets and substantially improve 
their scientific modeling workflow.
"""

__version__ = "0.1.0"
__author__ = "Ziwen Zhang, Kai Li"
__email__ = "244824379@qq.com"

from .utils import (
    get_datasets_list,
    download_single_dataset,
    download_dataset,
    download_dataset_parallel
)

__all__ = [
    "get_datasets_list",
    "download_single_dataset", 
    "download_dataset",
    "download_dataset_parallel"
] 