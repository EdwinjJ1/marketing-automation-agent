"""
平台发布模块
支持多平台内容发布
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()


class PlatformPublisher:
    """平台发布器基类"""

    def __init__(self, platform: str, config: Optional[Dict[str, Any]] = None):
        self.platform = platform
        self.config = config or {}
        self._init_client()

    def _init_client(self):
        """初始化平台客户端"""
        raise NotImplementedError("子类需要实现此方法")

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        发布内容

        Args:
            content: 包含以下键的字典:
                - text: 文案内容
                - images: 图片列表（可选）
                - video: 视频路径（可选）
                - metadata: 额外元数据（可选）

        Returns:
            发布结果，包含:
                - success: 是否成功
                - post_id: 帖子ID
                - url: 帖子链接
                - error: 错误信息（如果失败）
        """
        raise NotImplementedError("子类需要实现此方法")

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """验证内容是否符合平台要求"""
        return True


class RedditPublisher(PlatformPublisher):
    """Reddit发布器"""

    def _init_client(self):
        import praw

        self.client = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "MarketingAgent/1.0"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )

        # 测试连接
        try:
            self.client.user.me()
        except Exception as e:
            raise ConnectionError(f"Reddit连接失败: {e}")

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """发布到Reddit"""
        try:
            subreddit_name = self.config.get("subreddit", "marketing")
            post_type = self.config.get("post_type", "text")  # text, link, image

            subreddit = self.client.subreddit(subreddit_name)
            text = content["text"]
            title = content.get("title", self._generate_title(text))

            if post_type == "link" and content.get("url"):
                submission = subreddit.submit(
                    title=title,
                    url=content["url"]
                )
            elif post_type == "image" and content.get("images"):
                # Reddit图片发布需要特殊处理
                submission = subreddit.submit_image(
                    title=title,
                    image_path=content["images"][0]
                )
            else:
                # 文本帖子
                submission = subreddit.submit(
                    title=title,
                    selftext=text
                )

            return {
                "success": True,
                "post_id": submission.id,
                "url": f"https://reddit.com{submission.permalink}",
                "platform": "reddit"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "reddit"
            }

    def _generate_title(self, text: str, max_length: int = 300) -> str:
        """生成标题"""
        # 取第一句话或前N个字符
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit("。", 1)[0] + "..."

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """验证Reddit内容"""
        # Reddit标题限制：300字符
        title = content.get("title", "")
        if len(title) > 300:
            return False

        # Reddit文本限制：40000字符
        text = content.get("text", "")
        if len(text) > 40000:
            return False

        return True


class XTwitterPublisher(PlatformPublisher):
    """X/Twitter发布器"""

    def _init_client(self):
        import tweepy

        # 使用API v2
        self.client = tweepy.Client(
            bearer_token=os.getenv("X_BEARER_TOKEN"),
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_SECRET"),
        )

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """发布到X/Twitter"""
        try:
            text = content["text"]

            # 检查是否需要发布图片
            if content.get("images"):
                # 需要使用API v1.1上传图片
                import tweepy

                auth = tweepy.OAuth1UserHandler(
                    os.getenv("X_API_KEY"),
                    os.getenv("X_API_SECRET"),
                    os.getenv("X_ACCESS_TOKEN"),
                    os.getenv("X_ACCESS_SECRET")
                )
                api = tweepy.API(auth)

                # 上传第一张图片
                media = api.media_upload(filename=content["images"][0])

                # 发布推文
                tweet = self.client.create_tweet(
                    text=text,
                    media_ids=[media.media_id]
                )
            else:
                # 纯文本推文
                tweet = self.client.create_tweet(text=text)

            tweet_url = f"https://x.com/i/status/{tweet.data['id']}"

            return {
                "success": True,
                "post_id": tweet.data['id'],
                "url": tweet_url,
                "platform": "x"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "x"
            }

    def validate_content(self, content: Dict[str, Any]) -> bool:
        """验证X/Twitter内容"""
        # X文本限制：280字符（免费账号）
        text = content.get("text", "")
        max_length = self.config.get("character_limit", 280)

        if len(text) > max_length:
            return False

        return True


class TikTokPublisher(PlatformPublisher):
    """TikTok发布器"""

    def _init_client(self):
        # TikTok API需要企业认证
        # 这里使用官方SDK或自定义HTTP客户端
        pass

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """发布到TikTok"""
        # 需要视频文件
        if not content.get("video"):
            return {
                "success": False,
                "error": "TikTok需要视频内容",
                "platform": "tiktok"
            }

        # 实际实现需要调用TikTok Content Posting API
        # 这里返回模拟结果
        return {
            "success": True,
            "post_id": "mock_tiktok_id",
            "url": "https://tiktok.com/@user/video/mock",
            "platform": "tiktok",
            "note": "需要企业认证和官方API"
        }


class BilibiliPublisher(PlatformPublisher):
    """B站发布器"""

    def _init_client(self):
        # B站API需要认证
        pass

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """发布到B站"""
        # B站视频投稿API
        # 这里返回模拟结果
        return {
            "success": True,
            "post_id": "mock_bvid",
            "url": "https://bilibili.com/video/mock_bvid",
            "platform": "bilibili",
            "note": "需要B站认证"
        }


# 半自动发布器（生成内容，手动发布）
class XiaohongshuPublisher(PlatformPublisher):
    """小红书半自动发布器"""

    def _init_client(self):
        pass  # 小红书官方API受限

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成小红书发布内容
        返回格式化的内容供用户手动发布
        """
        formatted_content = {
            "title": content.get("title", ""),
            "content": content["text"],
            "images": content.get("images", []),
            "tags": content.get("tags", []),
            "platform": "xiaohongshu",
            "manual_publish": True,
            "instructions": "请复制以下内容到小红书APP手动发布"
        }

        return {
            "success": True,
            "data": formatted_content,
            "platform": "xiaohongshu",
            "note": "需要手动发布"
        }


class DouyinPublisher(PlatformPublisher):
    """抖音半自动发布器"""

    def _init_client(self):
        pass  # 抖音API需要企业认证

    def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """生成抖音发布内容"""
        return {
            "success": True,
            "data": content,
            "platform": "douyin",
            "manual_publish": True,
            "note": "需要手动发布或企业认证"
        }


# 工厂函数
def create_publisher(platform: str, config: Optional[Dict[str, Any]] = None) -> PlatformPublisher:
    """
    创建平台发布器

    Args:
        platform: 平台名称 (reddit, x, tiktok, bilibili, xiaohongshu, douyin)
        config: 平台配置

    Returns:
        对应平台的发布器实例
    """
    publishers = {
        "reddit": RedditPublisher,
        "x": XTwitterPublisher,
        "twitter": XTwitterPublisher,
        "tiktok": TikTokPublisher,
        "bilibili": BilibiliPublisher,
        "xiaohongshu": XiaohongshuPublisher,
        "douyin": DouyinPublisher,
    }

    publisher_class = publishers.get(platform.lower())
    if not publisher_class:
        raise ValueError(f"不支持的平台: {platform}")

    return publisher_class(platform, config)


# 批量发布
def publish_to_platforms(
    contents_by_platform: Dict[str, Dict[str, Any]],
    platforms: List[str],
    configs: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    发布到多个平台

    Args:
        contents_by_platform: 各平台的内容字典，格式: {platform: content_dict}
        platforms: 平台列表
        configs: 各平台配置

    Returns:
        各平台的发布结果
    """
    results = {}
    configs = configs or {}

    for platform in platforms:
        try:
            publisher = create_publisher(platform, configs.get(platform))

            # 提取该平台的内容
            platform_content = contents_by_platform.get(platform)
            if not platform_content:
                results[platform] = {
                    "success": False,
                    "error": f"No content provided for {platform}",
                    "platform": platform
                }
                continue

            # 发布前校验内容
            if not publisher.validate_content(platform_content):
                results[platform] = {
                    "success": False,
                    "error": "Content validation failed",
                    "platform": platform,
                    "validation_failed": True
                }
                continue

            result = publisher.publish(platform_content)
            results[platform] = result
        except Exception as e:
            results[platform] = {
                "success": False,
                "error": str(e),
                "platform": platform
            }

    return results
