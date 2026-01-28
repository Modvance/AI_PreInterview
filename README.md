# AI 快速面试系统

AI驱动的快速面试系统，用于在正式面试前评估候选人的逻辑思维能力。

## 功能特点

- **快速面试**：2-3道逻辑思维题，约10分钟完成
- **智能评估**：AI面试官根据答案和解题思路给出反馈
- **即时报告**：面试结束后自动生成详细评估报告
- **人性化交互**：模拟真实面试官的反馈方式

## 技术栈

- **前端**：Vue 3 + Vite + Tailwind CSS + Pinia
- **后端**：Python FastAPI
- **AI服务**：Aliyun DashScope (LLM / ASR / TTS)
- **部署**：Docker容器化

## 项目结构

```
AI_PreInterview/
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── stores/         # Pinia状态管理
│   │   ├── services/       # API服务
│   │   └── router/         # 路由配置
│   └── ...
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── services/       # 业务逻辑
│   │   ├── schemas/        # 数据模型
│   │   └── core/           # 核心配置
│   ├── data/               # 题库数据
│   └── ...
├── docker-compose.yml       # Docker编排
└── README.md
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- Docker & Docker Compose（可选，用于容器化部署）

### 本地开发

#### 1. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 2. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 即可使用。

### Docker部署

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## Configuration

### Environment Variables (backend/.env)

```env
# Application Settings
APP_NAME=AI-PreInterview
APP_ENV=development
DEBUG=true

# DashScope API Key (unified for all AI services)
# Get your API Key from: https://help.aliyun.com/zh/model-studio/get-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key-here

# LLM Model
LLM_MODEL=deepseek-v3

# ASR Model (Speech to Text)
ASR_MODEL=qwen3-asr-flash-realtime

# TTS Model (Text to Speech)
TTS_MODEL=qwen3-tts-flash-realtime
TTS_VOICE=Maia
```

### Supported Models

| Service | Models | Description |
|---------|--------|-------------|
| LLM | deepseek-v3, qwen-plus, qwen-turbo, qwen-flash | Large Language Model |
| ASR | qwen3-asr-flash-realtime, paraformer-realtime-v2 | Speech to Text |
| TTS | qwen3-tts-flash-realtime, cosyvoice-v1 | Text to Speech |

## API文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/interview/sessions | POST | 创建面试会话 |
| /api/interview/sessions/{id}/start | POST | 开始面试 |
| /api/interview/sessions/{id}/submit-answer | POST | 提交答案 |
| /api/interview/sessions/{id}/report | GET | 获取报告 |

## 面试流程

1. **创建会话**：填写基本信息，选择题目数量
2. **开始面试**：AI面试官欢迎语
3. **答题环节**：查看题目 → 选择答案 → 说明思路 → 获取反馈
4. **生成报告**：面试结束后查看详细评估报告

## 题库管理

当前题库存储在 `backend/data/questions.json`，包含以下类型：

- **logic**：逻辑推理题
- **math**：数学计算题
- **algorithm**：算法思维题
- **scenario**：场景分析题

## 待办事项

- [ ] 接入简历/JD解析服务
- [x] 实现ASR语音输入 (DashScope qwen3-asr-flash-realtime)
- [x] 实现TTS语音反馈 (DashScope qwen3-tts-flash-realtime)
- [ ] 数据库持久化存储
- [ ] 用户认证系统
- [ ] 面试记录管理后台
- [ ] 前端集成ASR/TTS功能

## 许可证

MIT License
