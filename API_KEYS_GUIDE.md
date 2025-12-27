# API密钥配置完整指南

## 你需要哪些API密钥？

根据你的需求，以下是**必需**和**可选**的API密钥：

### 必需（系统运行基础）

| API | 用途 | 获取难度 | 成本 | 优先级 |
|-----|------|---------|------|--------|
| **Anthropic Claude** | 文案生成 | 🟢 简单 | 💰 | ⭐⭐⭐⭐⭐ |
| **OpenAI GPT** | 备选文案生成 | 🟢 简单 | 💰💰 | ⭐⭐⭐⭐ |

### 内容生成（二选一）

#### 图像生成
| API | 用途 | 获取方式 | 成本 | 推荐度 |
|-----|------|---------|------|--------|
| **Replicate (SD3)** | 主力图像生成 | [replicate.com](https://replicate.com) | 💰 | ⭐⭐⭐⭐⭐ |
| **Stability AI** | 备选图像生成 | [platform.stability.ai](https://platform.stability.ai) | 💰💰 | ⭐⭐⭐⭐ |
| **OpenAI DALL-E** | 高端图像 | [platform.openai.com](https://platform.openai.com) | 💰💰💰 | ⭐⭐⭐ |

#### 视频生成（选择你想要的）
| API | 用途 | 获取方式 | 成本 | 推荐度 |
|-----|------|---------|------|--------|
| **Google Veo 3** | 视频生成 | [ai.google.dev](https://ai.google.dev) | 💰💰 | ⭐⭐⭐⭐⭐ |
| **快手可灵 Kling** | 视频生成 | [klingai.com](https://klingai.com/cn/dev) | 💰💰 | ⭐⭐⭐⭐⭐ |
| **Runway** | 备选视频 | [dev.runwayml.com](https://dev.runwayml.com) | 💰💰💰 | ⭐⭐⭐ |

### 平台发布（根据需要选择）

| 平台 | 发布能力 | 获取难度 | 是否必需 |
|------|---------|---------|---------|
| **Reddit** | 自动发布 | 🟢 简单 | ✅ 推荐 |
| **X/Twitter** | 自动发布 | 🟡 中等 | ✅ 推荐 |
| **TikTok** | 自动发布 | 🔴 复杂（需企业认证） | ⚠️ 可选 |
| **B站** | 自动发布 | 🟡 中等 | ⚠️ 可选 |
| **小红书** | 半自动 | 🔴 受限 | ⚠️ 可选 |
| **抖音** | 半自动 | 🔴 受限 | ⚠️ 可选 |

---

## 详细获取指南

### 1. Anthropic Claude API（文案生成）

**用途**: 生成营销文案、内容优化

**获取步骤**:
1. 访问 [console.anthropic.com](https://console.anthropic.com)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create Key"
5. 复制密钥到 `.env` 文件

**成本**: ~$3-15/百万字符（输入），~$15-75/百万字符（输出）

**配置**:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

### 2. Replicate API（Stable Diffusion 3图像生成）

**用途**: 生成高质量营销图片

**获取步骤**:
1. 访问 [replicate.com](https://replicate.com)
2. 点击 "Sign in" 注册账号
3. 进入 [Account Settings > API Tokens](https://replicate.com/account/api-tokens)
4. 点击 "Create token"
5. 复制token到 `.env` 文件

**成本**: 按使用量计费，约$0.002-0.01/张图

**配置**:
```bash
REPLICATE_API_TOKEN=r8_xxxxx
```

---

### 3. Google Veo 3 API（视频生成 - 推荐方案A）

**用途**: 生成高质量视频内容

**获取步骤**:

**方案A: Gemini API（官方）**
1. 访问 [ai.google.dev](https://ai.google.dev)
2. 创建新项目或选择现有项目
3. 进入 API & Services > Credentials
4. 创建 API Key
5. 启用 Gemini API

**方案B: Google AI Studio**
1. 访问 [aistudio.google.com](https://aistudio.google.com)
2. 免费使用Veo 3（有限额）
3. 获取API Key用于程序调用

**成本**:
- 免费层: 每月有限额
- 付费: 约$0.05-0.15/秒视频

**配置**:
```bash
GOOGLE_API_KEY=AIzaxxxxx
GOOGLE_CLOUD_PROJECT_ID=your-project-id
```

**参考**:
- [Gemini API Video Generation](https://ai.google.dev/gemini-api/docs/video)
- [Veo 3 访问指南](https://skywork.ai/blog/how-to-access-veo-3-1-2025-guide/)

---

### 4. 快手可灵 Kling AI（视频生成 - 推荐方案B）

**用途**: 生成视频内容（中文友好）

**获取步骤**:
1. 访问 [klingai.com 开发者平台](https://klingai.com/cn/dev)
2. 注册/登录账号
3. 进入 "API文档" 或 "定价" 页面
4. 购买额度套餐或申请试用
5. 获取 API Key 和 Secret

**定价**:
- Kling 2.6 Pro: ~$0.074/秒
- Kling 1.6: ~$0.42-0.50/10秒视频
- 套餐: $37-64.99/月

**配置**:
```bash
KLINGAI_API_KEY=your_klingai_api_key
KLINGAI_API_SECRET=your_klingai_api_secret
```

**参考**:
- [可灵AI开发者平台](https://klingai.com/cn/dev)
- [可灵AI定价](https://klingai.com/cn/dev/pricing)

---

### 5. Reddit API（自动发布）

**用途**: 自动发布到Reddit

**获取步骤**:
1. 访问 [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. 滚动到 "develop an app" 部分
3. 点击 "create app" 或 "develop another app"
4. 填写信息:
   - name: 随便填
   - type: 选择 "script"
   - description: 随便填
   - about url: 留空或填你的网站
   - redirect uri: 使用 `http://localhost:8080`
5. 点击 "create app"
6. 复制显示的 client_id 和 client_secret

**成本**: 免费

**配置**:
```bash
REDDIT_CLIENT_ID=your_client_id（14字符的字符串）
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=MarketingAgent/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

---

### 6. X/Twitter API（自动发布）

**用途**: 自动发布到X/Twitter

**获取步骤**:
1. 访问 [developer.twitter.com](https://developer.twitter.com)
2. 申请开发者账号
3. 创建新项目
4. 创建新应用
5. 在应用设置中生成:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

**成本**:
- 免费层: 500推文/月
- 付费: $100/月起

**配置**:
```bash
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_token_secret
X_BEARER_TOKEN=your_bearer_token
```

---

## NanoBananaPro 说明

**注意**: 搜索中未找到 "NanoBananaPro" 的官方API信息。这可能是：
- 一个非常新的/小众的模型
- 名称可能有误
- 内部/私有模型

**替代建议**:
如果指的是某个特定图像生成模型，请提供更多信息。目前推荐使用：
- **Stable Diffusion 3** (通过Replicate) - 最佳性价比
- **DALL-E 3** - 最高质量
- **Midjourney** - 艺术风格最佳（但无官方API）

---

## 快速配置检查清单

### 最小配置（MVP测试）
```bash
# 必需
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 图像生成（选一个）
REPLICATE_API_TOKEN=r8_xxxxx

# 发布平台（选一个）
REDDIT_CLIENT_ID=xxxxx
REDDIT_CLIENT_SECRET=xxxxx
REDDIT_USERNAME=xxxxx
REDDIT_PASSWORD=xxxxx
```

### 完整配置（生产环境）
```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx

# 图像生成
REPLICATE_API_TOKEN=r8_xxxxx

# 视频生成（选一个）
KLINGAI_API_KEY=xxxxx
KLINGAI_API_SECRET=xxxxx
# 或
GOOGLE_API_KEY=AIzaxxxxx

# 发布平台
REDDIT_CLIENT_ID=xxxxx
REDDIT_CLIENT_SECRET=xxxxx
X_API_KEY=xxxxx
X_BEARER_TOKEN=xxxxx
```

---

## 配置文件位置

所有密钥应配置在项目根目录的 `.env` 文件中：

```bash
cd /Users/edwinj/Edwin/second-brain/01-projects/077-marketing-automation-agent
cp .env.example .env
# 编辑 .env 文件，填入你的密钥
```

**安全提醒**:
- ⚠️ **永远不要**将 `.env` 文件提交到Git
- ⚠️ **永远不要**在公开场合分享你的API密钥
- ✅ `.env` 已在 `.gitignore` 中排除

---

## 预算估算

### 月度成本（中等使用量）

| 服务 | 使用量 | 月成本 |
|------|--------|--------|
| Claude API | 1M字符文案 | $20-50 |
| Replicate (SD3) | 500张图 | $5-20 |
| Kling AI | 30个15秒视频 | $100-200 |
| Reddit | 无限发布 | 免费 |
| X/Twitter | 500推文/月 | 免费 |
| **总计** | | **$125-270/月** |

### 节省成本建议

1. **使用免费层**: 大多数API都有免费试用额度
2. **分层生成**: 不是所有内容都需要最高质量
3. **缓存复用**: 相似内容使用模板
4. **按需付费**: 只在需要时启用视频生成

---

## 下一步

1. ✅ 注册并获取上述API密钥
2. ✅ 更新 `.env` 文件
3. ✅ 运行测试: `python main.py --dry-run`
4. ✅ 验证配置是否正确

---

**Sources:**
- [Google Veo 3 API Guide](https://ai.google.dev/gemini-api/docs/video)
- [快手可灵 Kling AI](https://klingai.com/cn/dev)
- [Replicate API](https://replicate.com)
- [Anthropic Console](https://console.anthropic.com)
