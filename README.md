# Marketing Automation Agent

通用的多平台营销内容自动化生成与发布系统。

## 功能概述

输入项目文档和图片，自动生成适配各平台的内容并发布。

### 支持的输入
- PDF 文档
- Word 文档 (.docx)
- Markdown 文档
- 图片文件 (PNG, JPG, WEBP)

### 支持的输出平台

| 平台 | 自动发布 | 状态 |
|------|---------|------|
| Reddit | ✅ | 完全支持 |
| X/Twitter | ✅ | 完全支持 |
| TikTok | ✅ | 需开发者账号 |
| B站 | ✅ | 需认证 |
| 小红书 | ⚠️ | 半自动（生成内容需手动发布） |
| 抖音 | ⚠️ | 半自动（生成内容需手动发布） |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

### 3. 运行示例

```bash
python main.py \
    --document examples/sample-project.pdf \
    --images examples/product-image.jpg \
    --platforms reddit,x,tiktok
```

## 项目结构

```
077-marketing-automation-agent/
├── src/
│   ├── agents/           # AI Agent定义
│   ├── parsers/          # 文档解析器
│   ├── publishers/       # 平台发布器
│   ├── generators/       # 内容生成器
│   └── utils/            # 工具函数
├── config/               # 配置文件
│   ├── platforms.yaml    # 平台配置
│   └── prompts.yaml      # 提示词模板
├── tests/                # 测试文件
├── examples/             # 示例文件
└── main.py               # 主入口
```

## 使用示例

### 基础用法

```python
from src import MarketingAgent

# 初始化Agent
agent = MarketingAgent()

# 处理项目并发布
result = agent.process_and_publish(
    document="path/to/project.pdf",
    images=["path/to/image1.jpg", "path/to/image2.jpg"],
    platforms=["reddit", "x", "tiktok"],
    schedule="2025-12-27 18:00"  # 可选：定时发布
)

print(result)
```

### 高级用法

```python
from src import MarketingAgent
from src.config import PlatformConfig

# 自定义配置
config = PlatformConfig(
    reddit_subreddit="marketing",
    x_hashtags=["#AI", "#Marketing"],
    tiktok_hashtags=["#人工智能", "#营销"],
    brand_tone="professional"
)

agent = MarketingAgent(config=config)
result = agent.process_and_publish(...)
```

## 开发路线图

### Phase 1: MVP (当前)
- [x] 项目结构搭建
- [ ] 文档解析 (PDF/Word/MD)
- [ ] 基础内容生成
- [ ] Reddit + X 发布
- [ ] 图片处理

### Phase 2: 扩展
- [ ] TikTok/B站集成
- [ ] 视频生成
- [ ] 定时发布
- [ ] A/B测试

### Phase 3: 优化
- [ ] 效果追踪
- [ ] 自动优化
- [ ] 多账号管理

## 配置说明

### 平台配置 (config/platforms.yaml)

```yaml
reddit:
  enabled: true
  subreddit: marketing
  post_type: link  # link, text, image

x:
  enabled: true
  character_limit: 280

tiktok:
  enabled: false  # 需要开发者账号
  video_duration: 15
```

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
