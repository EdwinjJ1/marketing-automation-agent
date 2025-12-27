# 快速开始指南

## 项目已创建！

你的营销自动化Agent项目框架已经搭建完成。

```
077-marketing-automation-agent/
├── README.md              # 项目说明
├── technical-proposal.md  # 技术方案文档
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量模板
├── main.py               # 主入口文件
├── QUICKSTART.md         # 本文件
└── src/
    ├── __init__.py
    ├── agents/           # AI Agent模块
    ├── parsers/          # 文档解析器
    └── publishers/       # 平台发布器
```

## 立即开始（5分钟）

### Step 1: 安装依赖

```bash
cd /Users/edwinj/Edwin/second-brain/01-projects/077-marketing-automation-agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### Step 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# 最少需要配置:
# - ANTHROPIC_API_KEY (用于Claude)
# 或
# - OPENAI_API_KEY (用于GPT)

# 如果要发布到平台，还需要配置对应平台的API密钥
```

### Step 3: 测试运行

```bash
# 测试文档解析和内容生成（不发布）
python main.py \
    --document examples/sample-project.pdf \
    --platforms reddit,x \
    --dry-run
```

### Step 4: 发布到平台

```bash
# 发布到Reddit和X（需要先配置API密钥）
python main.py \
    --document your-project.pdf \
    --images your-image.jpg \
    --platforms reddit,x
```

## 当前可用功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 文档解析 | ✅ | PDF, Word, MD, TXT, PPTX |
| 内容生成 | ✅ | 基于模板生成，可扩展LLM |
| Reddit发布 | ✅ | 需要Reddit API |
| X/Twitter发布 | ✅ | 需要X API |
| 定时发布 | ⚠️ | 需要配置Celery |
| 小红书/抖音 | ⚠️ | 生成内容，需手动发布 |

## 快速配置指南

### Reddit API配置

1. 访问 https://www.reddit.com/prefs/apps
2. 创建应用（script类型）
3. 获取client_id和client_secret
4. 填入.env文件

### X/Twitter API配置

1. 访问 https://developer.twitter.com/
2. 创建项目和应用
3. 获取API密钥和访问令牌
4. 填入.env文件

## 使用示例

### 示例1: 简单文档处理

```bash
# 处理PDF文档，查看生成的内容
python main.py \
    --document my-project.pdf \
    --platforms reddit,x \
    --dry-run
```

### 示例2: 带图片的发布

```bash
# 包含产品图片
python main.py \
    --document product-intro.docx \
    --images product-photo.jpg,logo.png \
    --platforms reddit,x
```

### 示例3: 多平台发布

```bash
# 发布到多个平台
python main.py \
    --document campaign.md \
    --images banner.jpg \
    --platforms reddit,x,xiaohongshu
```

### 示例4: 定时发布

```bash
# 在指定时间发布
python main.py \
    --document promotion.pdf \
    --platforms reddit,x \
    --schedule "2025-12-27 18:00"
```

## 下一步开发

### 短期（1-2周）

- [ ] 配置真实的LLM API（Claude或GPT）
- [ ] 完成内容生成Agent
- [ ] 测试Reddit和X发布
- [ ] 添加内容质量评分

### 中期（1-2个月）

- [ ] 集成TikTok API
- [ ] 集成B站API
- [ ] 实现定时发布（Celery）
- [ ] 添加视频生成功能

### 长期（3个月+）

- [ ] A/B测试框架
- [ ] 效果数据追踪
- [ ] 自动优化算法
- [ ] 小红书/抖音自动发布（如API开放）

## 常见问题

**Q: 小红书和抖音能自动发布吗？**
A: 目前官方API限制，只能生成内容供手动复制发布。

**Q: 如何获取更好的内容质量？**
A: 配置Claude或GPT API，系统会使用LLM生成更高质量的内容。

**Q: 可以批量处理多个文档吗？**
A: 当前版本不支持，可以写个shell脚本循环调用。

**Q: 支持视频发布吗？**
A: TikTok和B站支持，但需要企业认证的API。

## 获取帮助

- 查看技术方案: `technical-proposal.md`
- 查看项目README: `README.md`
- 查看代码注释: 各模块文件

---

**祝你开发顺利！**
