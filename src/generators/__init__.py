"""
内容生成模块
支持图像和视频生成
集成多种AI模型：Stable Diffusion, DALL-E, Veo 3, Kling AI等
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ImageGenerator:
    """图像生成器基类"""

    def __init__(self, model: str = "stable-diffusion-3"):
        self.model = model
        self._init_client()

    def _init_client(self):
        """初始化生成器客户端"""
        raise NotImplementedError("子类需要实现此方法")

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图像

        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            **kwargs: 其他参数

        Returns:
            生成结果，包含:
                - success: 是否成功
                - image_path: 图像路径
                - url: 图像URL（如果有）
                - error: 错误信息（如果失败）
        """
        raise NotImplementedError("子类需要实现此方法")


class StableDiffusionGenerator(ImageGenerator):
    """Stable Diffusion 图像生成器（通过Replicate）"""

    def _init_client(self):
        try:
            import replicate
            self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
        except ImportError:
            self.client = None
            print("警告: replicate未安装，图像生成功能不可用")

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        **kwargs
    ) -> Dict[str, Any]:
        """使用Stable Diffusion 3生成图像"""
        if not self.client:
            return {
                "success": False,
                "error": "Replicate客户端未初始化"
            }

        try:
            output = self.client.run(
                "stability-ai/stable-diffusion-3",
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt or "blurry, bad quality, distorted",
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "output_format": "png"
                }
            )

            return {
                "success": True,
                "url": output,
                "model": "stable-diffusion-3"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "stable-diffusion-3"
            }


class DALLEGenerator(ImageGenerator):
    """DALL-E 3 图像生成器"""

    def _init_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            self.client = None
            print("警告: openai未安装，DALL-E生成功能不可用")

    def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        **kwargs
    ) -> Dict[str, Any]:
        """使用DALL-E 3生成图像"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI客户端未初始化"
            }

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )

            return {
                "success": True,
                "url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "model": "dall-e-3"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "dall-e-3"
            }


class VideoGenerator:
    """视频生成器基类"""

    def __init__(self, model: str = "veo-3"):
        self.model = model
        self._init_client()

    def _init_client(self):
        """初始化生成器客户端"""
        raise NotImplementedError("子类需要实现此方法")

    def generate(
        self,
        prompt: str,
        duration: int = 8,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 提示词
            duration: 视频时长（秒）
            aspect_ratio: 宽高比
            **kwargs: 其他参数

        Returns:
            生成结果，包含:
                - success: 是否成功
                - video_path: 视频路径
                - url: 视频URL（如果有）
                - error: 错误信息（如果失败）
        """
        raise NotImplementedError("子类需要实现此方法")

    def image_to_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图生视频

        Args:
            image_path: 输入图像路径
            prompt: 动画描述
            duration: 视频时长
            **kwargs: 其他参数

        Returns:
            生成结果
        """
        raise NotImplementedError("子类需要实现此方法")


class Veo3Generator(VideoGenerator):
    """
    Google Veo 3 视频生成器

    文档: https://ai.google.dev/gemini-api/docs/video
    """

    def _init_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai
        except ImportError:
            self.client = None
            print("警告: google-generativeai未安装，Veo 3功能不可用")

    def generate(
        self,
        prompt: str,
        duration: int = 8,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        **kwargs
    ) -> Dict[str, Any]:
        """使用Veo 3生成视频"""
        if not self.client:
            return {
                "success": False,
                "error": "Google Generative AI客户端未初始化"
            }

        try:
            # Veo 3 通过 Gemini API 调用
            # 注意: 实际API可能需要特定配置
            model = self.client.GenerativeModel("gemini-2.0-flash-exp")

            # 构建视频生成请求
            response = model.generate_content(
                f"""Generate a {duration} second video with the following description:
                {prompt}

                Specifications:
                - Aspect ratio: {aspect_ratio}
                - Resolution: {resolution}
                - Include audio generation
                """
            )

            return {
                "success": True,
                "response": response,
                "model": "veo-3"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "veo-3",
                "note": "Veo 3 API可能需要特殊配置或企业访问权限"
            }


class KlingAIGenerator(VideoGenerator):
    """
    快手可灵 Kling AI 视频生成器

    文档: https://klingai.com/cn/dev
    定价: https://klingai.com/cn/dev/pricing
    """

    def _init_client(self):
        self.api_key = os.getenv("KLINGAI_API_KEY")
        self.api_secret = os.getenv("KLINGAI_API_SECRET")
        self.base_url = "https://api.klingai.com/v1"

        if not self.api_key or not self.api_secret:
            print("警告: KLINGAI_API_KEY 或 KLINGAI_API_SECRET 未配置")

    def generate(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        model: str = "kling-v-1-6",
        **kwargs
    ) -> Dict[str, Any]:
        """使用Kling AI生成视频"""
        if not self.api_key:
            return {
                "success": False,
                "error": "Kling AI API密钥未配置"
            }

        try:
            import requests

            # Kling AI 文生视频接口
            url = f"{self.base_url}/videos/text2video"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "model": model,
                "enable_audio": kwargs.get("enable_audio", True)
            }

            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("task_id"),
                    "status": data.get("status"),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code} - {response.text}",
                    "model": model
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model
            }

    def image_to_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 5,
        model: str = "kling-2-6-pro",
        **kwargs
    ) -> Dict[str, Any]:
        """使用Kling AI进行图生视频"""
        if not self.api_key:
            return {
                "success": False,
                "error": "Kling AI API密钥未配置"
            }

        try:
            import requests
            import base64

            # 读取并编码图像
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            url = f"{self.base_url}/videos/image2video"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "image": image_data,
                "prompt": prompt,
                "duration": duration,
                "model": model
            }

            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("task_id"),
                    "status": data.get("status"),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code} - {response.text}",
                    "model": model
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model
            }

    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """检查视频生成任务状态"""
        if not self.api_key:
            return {
                "success": False,
                "error": "Kling AI API密钥未配置"
            }

        try:
            import requests

            url = f"{self.base_url}/videos/tasks/{task_id}"

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get("status"),
                    "video_url": data.get("video_url"),
                    "progress": data.get("progress", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 工厂函数
def create_image_generator(model: str = "stable-diffusion-3") -> ImageGenerator:
    """
    创建图像生成器

    Args:
        model: 模型名称 (stable-diffusion-3, dall-e-3)

    Returns:
        对应的图像生成器实例
    """
    generators = {
        "stable-diffusion-3": StableDiffusionGenerator,
        "sd3": StableDiffusionGenerator,
        "dall-e-3": DALLEGenerator,
        "dalle": DALLEGenerator,
    }

    generator_class = generators.get(model.lower())
    if not generator_class:
        raise ValueError(f"不支持的图像模型: {model}")

    return generator_class(model=model)


def create_video_generator(model: str = "veo-3") -> VideoGenerator:
    """
    创建视频生成器

    Args:
        model: 模型名称 (veo-3, kling, klingai)

    Returns:
        对应的视频生成器实例
    """
    generators = {
        "veo-3": Veo3Generator,
        "veo": Veo3Generator,
        "kling": KlingAIGenerator,
        "klingai": KlingAIGenerator,
    }

    generator_class = generators.get(model.lower())
    if not generator_class:
        raise ValueError(f"不支持的视频模型: {model}")

    return generator_class(model=model)


# 使用示例
if __name__ == "__main__":
    # 图像生成示例
    print("测试图像生成...")
    img_gen = create_image_generator("stable-diffusion-3")
    result = img_gen.generate("A cute cat wearing sunglasses, digital art")
    print(result)

    # 视频生成示例
    print("\n测试视频生成...")
    vid_gen = create_video_generator("kling")
    result = vid_gen.generate(
        prompt="A peaceful sunset over mountains, cinematic quality",
        duration=5
    )
    print(result)
