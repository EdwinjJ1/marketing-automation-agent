"""
Celery任务定义
用于异步和定时发布任务
"""

from src.celery_config import app


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_scheduled_task(
    self,
    task_id: str,
    content_id: str,
    platforms: list,
    configs: dict = None
):
    """
    执行定时发布任务（带幂等保护）

    Args:
        task_id: 任务ID (用于状态跟踪和幂等)
        content_id: 内容ID (从SQLite加载实际内容)
        platforms: 平台列表
        configs: 平台配置

    Returns:
        发布结果字典
    """
    from src.db import (
        get_content, get_task, update_task_status,
        check_published, mark_published
    )
    from src.publishers import create_publisher

    # 检查任务是否已被取消
    task = get_task(task_id)
    if task and task["status"] == "cancelled":
        return {
            "status": "cancelled",
            "task_id": task_id,
            "message": "Task was cancelled before execution"
        }

    # 从SQLite加载内容 (避免消息体过大)
    contents = get_content(content_id)
    if not contents:
        update_task_status(task_id, "failed", error="Content not found in database")
        return {
            "success": False,
            "error": "Content not found",
            "task_id": task_id
        }

    try:
        # 更新状态为运行中
        update_task_status(task_id, "running")

        configs = configs or {}
        results = {}

        # 逐平台发布，带幂等检查
        for platform in platforms:
            # 幂等检查：已发布则跳过
            existing = check_published(task_id, platform)
            if existing:
                results[platform] = {
                    "success": True,
                    "skipped": True,
                    "post_id": existing.get("post_id"),
                    "url": existing.get("post_url"),
                    "platform": platform,
                    "message": "Already published (idempotent skip)"
                }
                continue

            # 获取该平台内容
            platform_content = contents.get(platform)
            if not platform_content:
                results[platform] = {
                    "success": False,
                    "error": f"No content for {platform}",
                    "platform": platform
                }
                continue

            try:
                publisher = create_publisher(platform, configs.get(platform))

                # 校验内容
                if not publisher.validate_content(platform_content):
                    results[platform] = {
                        "success": False,
                        "error": "Content validation failed",
                        "platform": platform
                    }
                    continue

                # 执行发布
                result = publisher.publish(platform_content)
                results[platform] = result

                # 发布成功则标记幂等
                if result.get("success"):
                    mark_published(
                        task_id,
                        platform,
                        result.get("post_id"),
                        result.get("url")
                    )

            except Exception as e:
                results[platform] = {
                    "success": False,
                    "error": str(e),
                    "platform": platform
                }

        # 判断整体成功状态
        all_success = all(r.get("success", False) for r in results.values())
        any_success = any(r.get("success", False) for r in results.values())

        if all_success:
            status = "completed"
        elif any_success:
            status = "partial_failure"
        else:
            status = "failed"

        # 更新任务状态
        update_task_status(
            task_id,
            status,
            result=str(results)
        )

        return {
            "success": all_success,
            "task_id": task_id,
            "status": status,
            "results": results
        }

    except Exception as e:
        error_msg = str(e)
        update_task_status(task_id, "failed", error=error_msg)

        # 尝试重试
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "success": False,
                "error": f"Max retries exceeded: {error_msg}",
                "task_id": task_id
            }


@app.task
def cleanup_old_tasks(days: int = 30):
    """
    安全清理旧任务数据

    只删除已完成/失败/取消的任务，保留未来计划任务

    Args:
        days: 保留最近N天的已完成任务数据
    """
    from src.db import cleanup_old_content
    result = cleanup_old_content(days)
    return {
        "deleted_contents": result["contents"],
        "deleted_tasks": result["tasks"],
        "deleted_published_records": result["published"]
    }
