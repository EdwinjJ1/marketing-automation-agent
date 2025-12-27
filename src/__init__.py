"""
Marketing Automation Agent
通用的多平台营销内容自动化生成与发布系统
"""

__version__ = "0.1.0"
__author__ = "Evan Lin"

from src.agents import MarketingAgent
from src.parsers import DocumentParser
from src.publishers import PlatformPublisher

__all__ = [
    "MarketingAgent",
    "DocumentParser",
    "PlatformPublisher",
]
