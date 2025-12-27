"""
Celery配置模块
使用环境变量配置，支持生产级部署
"""

import os
from celery import Celery

# 从环境变量获取配置，提供合理的默认值
BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
TIMEZONE = os.getenv('CELERY_TIMEZONE', 'UTC')

# 创建Celery应用
app = Celery('marketing_agent')

app.conf.update(
    # Broker配置
    broker_url=BROKER_URL,
    result_backend=RESULT_BACKEND,

    # 序列化配置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # 时区配置
    timezone=TIMEZONE,
    enable_utc=True,

    # 可靠性配置
    task_track_started=True,      # 跟踪任务开始状态
    task_acks_late=True,          # 任务完成后再确认
    task_reject_on_worker_lost=True,  # Worker丢失时拒绝任务

    # 结果配置
    result_expires=86400,         # 结果保留24小时

    # 重试配置
    task_default_retry_delay=60,  # 默认重试延迟60秒
    task_max_retries=3,           # 最大重试次数
)

# 自动发现任务
app.autodiscover_tasks(['src'])
