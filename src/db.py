"""
SQLite数据库模块
用于持久化任务元数据和内容存储
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

# 数据库路径
DB_PATH = Path(__file__).parent.parent / "data" / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化数据库表"""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                task_id TEXT PRIMARY KEY,
                celery_task_id TEXT,
                content_id TEXT NOT NULL,
                platforms TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                error TEXT,
                result TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_contents (
                content_id TEXT PRIMARY KEY,
                contents_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # 幂等表：防止重复发布
        conn.execute("""
            CREATE TABLE IF NOT EXISTS published_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                post_id TEXT,
                post_url TEXT,
                published_at TEXT NOT NULL,
                UNIQUE(task_id, platform)
            )
        """)
        # 创建索引
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON scheduled_tasks(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_scheduled_time
            ON scheduled_tasks(scheduled_time)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_published_task_platform
            ON published_posts(task_id, platform)
        """)
        conn.commit()
    finally:
        conn.close()


def store_content(content_id: str, contents: Dict[str, Any]) -> None:
    """
    存储内容到数据库
    避免通过Celery消息传递大量内容
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO task_contents (content_id, contents_json, created_at) VALUES (?, ?, ?)",
            (content_id, json.dumps(contents, ensure_ascii=False), datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def get_content(content_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取存储的内容"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT contents_json FROM task_contents WHERE content_id = ?",
            (content_id,)
        ).fetchone()
        return json.loads(row["contents_json"]) if row else None
    finally:
        conn.close()


def create_task(
    task_id: str,
    celery_task_id: str,
    content_id: str,
    platforms: List[str],
    scheduled_time: datetime
) -> None:
    """创建新的调度任务记录"""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO scheduled_tasks
            (task_id, celery_task_id, content_id, platforms, scheduled_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            celery_task_id,
            content_id,
            json.dumps(platforms),
            scheduled_time.isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取任务信息"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM scheduled_tasks WHERE task_id = ?",
            (task_id,)
        ).fetchone()
        if row:
            result = dict(row)
            result["platforms"] = json.loads(result["platforms"])
            return result
        return None
    finally:
        conn.close()


def update_task_status(
    task_id: str,
    status: str,
    error: str = None,
    result: str = None
) -> None:
    """
    更新任务状态

    状态流转: scheduled -> running -> completed/failed/partial_failure
    """
    conn = get_connection()
    try:
        now = datetime.now().isoformat()

        if status == "running":
            # 任务开始执行
            conn.execute("""
                UPDATE scheduled_tasks
                SET status = ?, started_at = ?
                WHERE task_id = ?
            """, (status, now, task_id))
        elif status in ("completed", "failed", "partial_failure"):
            # 任务完成
            conn.execute("""
                UPDATE scheduled_tasks
                SET status = ?, error = ?, result = ?, finished_at = ?
                WHERE task_id = ?
            """, (status, error, result, now, task_id))
        else:
            # 其他状态 (cancelled 等)
            conn.execute("""
                UPDATE scheduled_tasks
                SET status = ?, error = ?
                WHERE task_id = ?
            """, (status, error, task_id))

        conn.commit()
    finally:
        conn.close()


def check_published(task_id: str, platform: str) -> Optional[Dict[str, Any]]:
    """
    检查是否已发布（幂等检查）

    Returns:
        已发布记录 或 None
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM published_posts WHERE task_id = ? AND platform = ?",
            (task_id, platform)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def mark_published(
    task_id: str,
    platform: str,
    post_id: str = None,
    post_url: str = None
) -> None:
    """
    标记为已发布（幂等写入）

    如果已存在则忽略（不抛异常）
    """
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO published_posts
            (task_id, platform, post_id, post_url, published_at)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, platform, post_id, post_url, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()


def cancel_task(task_id: str) -> str:
    """
    取消任务

    Returns:
        'cancelled' - 成功取消
        'already_executed' - 任务已执行，无法取消
        'not_found' - 任务不存在
    """
    task = get_task(task_id)
    if not task:
        return "not_found"
    if task["status"] in ("completed", "failed", "partial_failure"):
        return "already_executed"
    if task["status"] == "running":
        return "already_executed"  # 运行中的任务无法可靠取消

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE scheduled_tasks SET status = 'cancelled' WHERE task_id = ?",
            (task_id,)
        )
        conn.commit()
    finally:
        conn.close()
    return "cancelled"


def list_tasks(
    status: str = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """列出任务"""
    conn = get_connection()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM scheduled_tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM scheduled_tasks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

        results = []
        for row in rows:
            result = dict(row)
            result["platforms"] = json.loads(result["platforms"])
            results.append(result)
        return results
    finally:
        conn.close()


def cleanup_old_content(days: int = 7) -> Dict[str, int]:
    """
    安全清理旧的内容记录

    只删除已完成/失败/取消的任务内容，保留未来计划任务的内容

    Args:
        days: 保留最近N天的已完成任务内容

    Returns:
        删除统计 {"contents": n, "tasks": m, "published": p}
    """
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    conn = get_connection()
    try:
        # 找出可以安全删除的 content_id
        # 条件：关联任务状态为 completed/failed/cancelled/partial_failure
        # 且任务创建时间早于阈值
        safe_content_ids = conn.execute("""
            SELECT DISTINCT tc.content_id
            FROM task_contents tc
            JOIN scheduled_tasks st ON tc.content_id = st.content_id
            WHERE st.status IN ('completed', 'failed', 'cancelled', 'partial_failure')
            AND st.created_at < ?
        """, (cutoff,)).fetchall()

        content_ids = [row[0] for row in safe_content_ids]

        if not content_ids:
            return {"contents": 0, "tasks": 0, "published": 0}

        # 删除内容
        placeholders = ','.join('?' * len(content_ids))
        cursor1 = conn.execute(
            f"DELETE FROM task_contents WHERE content_id IN ({placeholders})",
            content_ids
        )
        deleted_contents = cursor1.rowcount

        # 删除关联的任务记录
        cursor2 = conn.execute(
            f"DELETE FROM scheduled_tasks WHERE content_id IN ({placeholders})",
            content_ids
        )
        deleted_tasks = cursor2.rowcount

        # 删除关联的发布记录
        task_ids = conn.execute(
            f"SELECT task_id FROM scheduled_tasks WHERE content_id IN ({placeholders})",
            content_ids
        ).fetchall()
        task_id_list = [row[0] for row in task_ids]

        deleted_published = 0
        if task_id_list:
            task_placeholders = ','.join('?' * len(task_id_list))
            cursor3 = conn.execute(
                f"DELETE FROM published_posts WHERE task_id IN ({task_placeholders})",
                task_id_list
            )
            deleted_published = cursor3.rowcount

        conn.commit()
        return {
            "contents": deleted_contents,
            "tasks": deleted_tasks,
            "published": deleted_published
        }
    finally:
        conn.close()
