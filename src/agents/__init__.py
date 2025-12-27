"""
AI Agent模块
使用CrewAI实现多Agent协作的内容生成与发布
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# CrewAI imports
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("警告: CrewAI未安装，将使用简化模式")


class MarketingAgent:
    """
    营销自动化Agent
    协调内容生成和平台发布
    """

    def __init__(
        self,
        llm_provider: str = "anthropic",
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.llm_provider = llm_provider
        self._init_llm()

    def _init_llm(self):
        """初始化LLM"""
        if self.llm_provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                self.llm = None
                print("警告: langchain-anthropic未安装")
        elif self.llm_provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            except ImportError:
                self.llm = None
                print("警告: langchain-openai未安装")

    def process_and_publish(
        self,
        document: str,
        images: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        schedule: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理文档并发布到各平台

        Args:
            document: 文档路径
            images: 图片路径列表
            platforms: 目标平台列表
            schedule: 定时发布时间（可选）

        Returns:
            处理结果
        """
        # 1. 解析文档
        from src.parsers import DocumentParser
        parser = DocumentParser()
        parsed_doc = parser.parse(document)
        key_info = parser.extract_key_info(parsed_doc)

        # 2. 生成各平台内容
        platforms = platforms or ["reddit", "x"]
        platform_contents = self._generate_platform_contents(
            key_info,
            parsed_doc,
            images,
            platforms
        )

        # 3. 发布内容
        from src.publishers import publish_to_platforms

        results = {}
        if schedule:
            # 定时发布
            results["scheduled"] = self._schedule_publishing(
                platform_contents, platforms, schedule
            )
        else:
            # 立即发布
            results["published"] = publish_to_platforms(
                platform_contents, platforms, self.config.get("platform_configs")
            )

        return {
            "success": True,
            "document_info": key_info,
            "contents": platform_contents,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_platform_contents(
        self,
        key_info: Dict[str, Any],
        parsed_doc: Dict[str, Any],
        images: Optional[List[str]],
        platforms: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """为各平台生成适配的内容"""
        contents = {}

        for platform in platforms:
            contents[platform] = self._generate_content_for_platform(
                platform, key_info, parsed_doc, images
            )

        return contents

    def _generate_content_for_platform(
        self,
        platform: str,
        key_info: Dict[str, Any],
        parsed_doc: Dict[str, Any],
        images: Optional[List[str]]
    ) -> Dict[str, Any]:
        """为特定平台生成内容"""

        # 平台特性配置
        platform_specs = {
            "reddit": {
                "max_length": 40000,
                "tone": "informative",
                "format": "markdown",
                "hashtags": False
            },
            "x": {
                "max_length": 280,
                "tone": "concise",
                "format": "plain",
                "hashtags": True
            },
            "tiktok": {
                "max_length": 150,
                "tone": "energetic",
                "format": "plain",
                "hashtags": True
            },
            "xiaohongshu": {
                "max_length": 1000,
                "tone": "lifestyle",
                "format": "emoji",
                "hashtags": True
            },
            "douyin": {
                "max_length": 80,
                "tone": "catchy",
                "format": "plain",
                "hashtags": True
            },
            "bilibili": {
                "max_length": 2000,
                "tone": "detailed",
                "format": "markdown",
                "hashtags": True
            }
        }

        spec = platform_specs.get(platform, platform_specs["x"])

        # 使用LLM生成内容（简化版）
        if self.llm and CREWAI_AVAILABLE:
            content = self._generate_with_llm(platform, key_info, spec)
        else:
            # 降级到模板生成
            content = self._generate_with_template(platform, key_info, spec)

        return {
            "text": content,
            "images": images or [],
            "title": key_info.get("title", ""),
            "metadata": {
                "platform": platform,
                "generated_at": datetime.now().isoformat()
            }
        }

    def _generate_with_llm(
        self,
        platform: str,
        key_info: Dict[str, Any],
        spec: Dict[str, Any],
        max_retries: int = 1
    ) -> str:
        """使用LLM生成内容，失败时回退到模板"""
        import logging
        import time

        if not self.llm:
            return self._generate_with_template(platform, key_info, spec)

        prompt = self._build_prompt(platform, key_info, spec)

        for attempt in range(max_retries + 1):
            try:
                response = self.llm.invoke(prompt)
                text = response.content if hasattr(response, 'content') else str(response)

                # 强制执行最大长度限制
                max_len = spec.get('max_length', 1000)
                if len(text) > max_len:
                    text = text[:max_len]

                return text
            except Exception as e:
                logging.warning(f"LLM生成尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # 指数退避

        # 回退到模板生成
        logging.info(f"LLM生成失败，回退到模板生成 (平台: {platform})")
        return self._generate_with_template(platform, key_info, spec)

    def _build_prompt(
        self,
        platform: str,
        key_info: Dict[str, Any],
        spec: Dict[str, Any]
    ) -> str:
        """构建LLM提示词"""
        return f"""请为{platform}平台生成营销文案。

项目信息：
标题: {key_info.get('title')}
摘要: {key_info.get('summary')}
关键特性: {', '.join(key_info.get('key_features', []))}

平台要求：
- 最大长度: {spec['max_length']}字符
- 语调: {spec['tone']}
- 格式: {spec['format']}

请生成吸引人的营销文案。
"""

    def _generate_with_template(
        self,
        platform: str,
        key_info: Dict[str, Any],
        spec: Dict[str, Any]
    ) -> str:
        """使用模板生成内容"""

        templates = {
            "reddit": """# {title}

{summary}

## 主要特性

{features}

---

了解更多: {link}
""",
            "x": """{title}

{summary}

{hashtags}
""",
            "xiaohongshu": """{title} ✨

{summary}

主要特点：
{features}

{hashtags}

#分享 #推荐
""",
            "tiktok": """{title}

{summary}

{hashtags}
""",
            "douyin": """{title}

{summary}

{hashtags}
""",
            "bilibili": """【{title}】

{summary}

视频内容：
{features}

{hashtags}
"""
        }

        template = templates.get(platform, templates["x"])

        # 格式化特性列表
        features = key_info.get("key_features", [])
        features_text = "\n".join(f"- {f}" for f in features)

        # 生成hashtags
        hashtags = self._generate_hashtags(platform, key_info)

        return template.format(
            title=key_info.get("title", ""),
            summary=key_info.get("summary", ""),
            features=features_text,
            hashtags=hashtags,
            link="https://example.com"
        )

    def _generate_hashtags(
        self,
        platform: str,
        key_info: Dict[str, Any]
    ) -> str:
        """生成平台适配的标签"""
        title = key_info.get("title", "")

        # 从标题提取关键词
        keywords = []
        if "AI" in title or "人工智能" in title:
            keywords.extend(["#AI", "#人工智能"])
        if "营销" in title:
            keywords.extend(["#Marketing", "#营销"])
        if "开发" in title or "开发" in key_info.get("target_audience", ""):
            keywords.extend(["#Developer", "#开发者"])

        # 平台特定标签
        if platform == "xiaohongshu":
            keywords.extend(["#分享", "#推荐", "#好物"])
        elif platform == "tiktok":
            keywords.extend(["#fyp", "#viral"])
        elif platform == "douyin":
            keywords.extend(["#推荐", "#热门"])

        return " ".join(keywords[:5])  # 限制标签数量

    def _schedule_publishing(
        self,
        contents: Dict[str, Dict[str, Any]],
        platforms: List[str],
        schedule_time: datetime
    ) -> Dict[str, Any]:
        """
        安排定时发布

        Args:
            contents: 各平台内容字典
            platforms: 平台列表
            schedule_time: 定时发布时间 (需要时区感知)

        Returns:
            调度结果，包含task_id用于状态查询
        """
        import uuid
        from src.db import init_db, store_content, create_task

        # 确保数据库已初始化
        init_db()

        # 生成唯一ID
        task_id = str(uuid.uuid4())
        content_id = str(uuid.uuid4())

        # 将内容存储到SQLite (避免Celery消息体过大)
        store_content(content_id, contents)

        try:
            # 尝试使用Celery调度
            from src.tasks import publish_scheduled_task

            celery_task = publish_scheduled_task.apply_async(
                args=[task_id, content_id, platforms, self.config.get("platform_configs")],
                eta=schedule_time
            )

            # 记录任务到SQLite
            create_task(task_id, celery_task.id, content_id, platforms, schedule_time)

            return {
                "task_id": task_id,
                "celery_task_id": celery_task.id,
                "scheduled_time": schedule_time.isoformat(),
                "platforms": platforms,
                "status": "scheduled"
            }

        except Exception as e:
            # Celery不可用时的降级处理
            import logging
            logging.warning(f"Celery调度失败: {e}，任务已记录但需要手动执行")

            # 仍然记录任务 (无celery_task_id)
            create_task(task_id, None, content_id, platforms, schedule_time)

            return {
                "task_id": task_id,
                "celery_task_id": None,
                "scheduled_time": schedule_time.isoformat(),
                "platforms": platforms,
                "status": "pending_manual",
                "warning": "Celery不可用，需要手动执行或启动Celery worker"
            }


# 单独的内容生成Agent（用于CrewAI）
if CREWAI_AVAILABLE:
    content_writer = Agent(
        role="营销文案创作专家",
        goal="创作高质量、高转化率的营销文案",
        backstory="""你是一位拥有10年经验的数字营销专家，
        深谙各社交媒体平台的内容规律和用户心理。
        你擅长将复杂的产品信息转化为吸引人的营销文案。""",
        verbose=True,
        allow_delegation=False
    )

    image_designer = Agent(
        role="视觉内容设计师",
        goal="生成符合品牌调性和平台要求的视觉素材",
        backstory="""你是一位专业的视觉设计师，
        精通AI图像生成和品牌视觉一致性。
        你能为不同平台创作最合适的视觉内容。""",
        verbose=True,
        allow_delegation=False
    )

    platform_specialist = Agent(
        role="社交媒体运营专家",
        goal="确保内容符合各平台的最佳实践",
        backstory="""你是一位资深的社交媒体运营专家，
        熟悉所有主流平台的发布规则、最佳发布时间和用户偏好。""",
        verbose=True,
        allow_delegation=False
    )
