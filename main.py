#!/usr/bin/env python3
"""
Marketing Automation Agent - 主入口
通用的多平台营销内容自动化生成与发布系统
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src import MarketingAgent


def main():
    parser = argparse.ArgumentParser(
        description="营销内容自动化生成与发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础用法 - 处理文档并发布
  python main.py --document project.pdf --platforms reddit,x

  # 包含图片
  python main.py --document project.pdf --images img1.jpg,img2.png --platforms reddit,x,tiktok

  # 定时发布
  python main.py --document project.pdf --platforms reddit,x --schedule "2025-12-27 18:00"

  # 只生成内容不发布
  python main.py --document project.pdf --platforms reddit,x --dry-run

支持的平台:
  reddit     - Reddit (自动发布)
  x/twitter  - X/Twitter (自动发布)
  tiktok     - TikTok (需要企业认证)
  bilibili   - B站 (需要认证)
  xiaohongshu - 小红书 (半自动)
  douyin     - 抖音 (半自动)
        """
    )

    parser.add_argument(
        "-d", "--document",
        required=True,
        help="项目文档路径 (PDF, Word, Markdown, TXT)"
    )

    parser.add_argument(
        "-i", "--images",
        help="图片路径，多个图片用逗号分隔"
    )

    parser.add_argument(
        "-p", "--platforms",
        default="reddit,x",
        help="目标平台，多个平台用逗号分隔 (默认: reddit,x)"
    )

    parser.add_argument(
        "-s", "--schedule",
        help="定时发布时间，格式: YYYY-MM-DD HH:MM 或 ISO格式 (可带时区)"
    )

    parser.add_argument(
        "--timezone",
        help="时区 (例如: 'Asia/Shanghai', 'UTC')，默认使用系统时区"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只生成内容不发布"
    )

    parser.add_argument(
        "--config",
        help="配置文件路径"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    # 验证文档存在
    if not Path(args.document).exists():
        print(f"错误: 文档不存在: {args.document}")
        sys.exit(1)

    # 处理图片列表
    images = None
    if args.images:
        images = [img.strip() for img in args.images.split(",")]
        # 验证图片存在
        for img in images:
            if not Path(img).exists():
                print(f"警告: 图片不存在: {img}")

    # 解析平台列表
    platforms = [p.strip() for p in args.platforms.split(",")]

    # 解析定时发布时间 (时区感知)
    schedule = None
    if args.schedule:
        import pytz

        # 辅助函数：将naive datetime转为timezone-aware
        def make_aware(dt, tz):
            """兼容 pytz 和 zoneinfo 的时区转换"""
            if hasattr(tz, 'localize'):
                # pytz 时区
                return tz.localize(dt)
            else:
                # zoneinfo 时区 (Python 3.9+ / tzlocal)
                return dt.replace(tzinfo=tz)

        # 确定时区
        tz = None
        if args.timezone:
            try:
                tz = pytz.timezone(args.timezone)
            except pytz.UnknownTimeZoneError:
                print(f"错误: 未知时区: {args.timezone}")
                sys.exit(1)
        else:
            try:
                from tzlocal import get_localzone
                tz = get_localzone()
            except ImportError:
                tz = pytz.UTC
                print("警告: 未安装tzlocal，使用UTC时区")

        # 尝试解析时间
        try:
            # 先尝试ISO格式 (可能包含时区)
            schedule = datetime.fromisoformat(args.schedule)
            if schedule.tzinfo is None:
                schedule = make_aware(schedule, tz)
        except ValueError:
            try:
                # 回退到简单格式
                schedule = datetime.strptime(args.schedule, "%Y-%m-%d %H:%M")
                schedule = make_aware(schedule, tz)
            except ValueError:
                print(f"错误: 时间格式不正确，应为 'YYYY-MM-DD HH:MM' 或 ISO格式")
                sys.exit(1)

    # 加载配置（如果有）
    config = {}
    if args.config:
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)

    # 显示处理信息
    print("=" * 60)
    print("营销自动化Agent")
    print("=" * 60)
    print(f"文档: {args.document}")
    print(f"图片: {len(images) if images else 0} 张")
    print(f"平台: {', '.join(platforms)}")
    if schedule:
        tz_name = schedule.tzinfo.zone if hasattr(schedule.tzinfo, 'zone') else str(schedule.tzinfo)
        print(f"定时发布: {schedule.strftime('%Y-%m-%d %H:%M')} ({tz_name})")
    if args.dry_run:
        print("模式: 只生成不发布 (Dry Run)")
    print("=" * 60)
    print()

    # 初始化Agent
    try:
        agent = MarketingAgent(config=config)
    except Exception as e:
        print(f"错误: Agent初始化失败: {e}")
        sys.exit(1)

    # 处理并发布
    try:
        result = agent.process_and_publish(
            document=args.document,
            images=images,
            platforms=platforms,
            schedule=schedule
        )

        # 显示结果
        print("处理结果:")
        print("-" * 60)

        # 显示生成的平台内容
        print("\n生成的内容:")
        for platform, content in result.get("contents", {}).items():
            text_preview = content["text"][:100] + "..." if len(content["text"]) > 100 else content["text"]
            print(f"\n[{platform.upper()}]")
            print(f"  {text_preview}")

        # 显示发布结果
        if not args.dry_run:
            print("\n\n发布结果:")
            published = result.get("results", {}).get("published", {})
            for platform, publish_result in published.items():
                status = "✓ 成功" if publish_result.get("success") else "✗ 失败"
                print(f"\n[{platform.upper()}] {status}")
                if publish_result.get("url"):
                    print(f"  链接: {publish_result['url']}")
                if publish_result.get("error"):
                    print(f"  错误: {publish_result['error']}")

        print("\n" + "=" * 60)
        print("完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
