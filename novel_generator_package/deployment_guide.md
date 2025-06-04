# 自动小说生成器项目部署文档

## 项目概述

自动小说生成器是一个基于多智能体协作的全自动多轮交互式小说生成系统，采用模块化架构设计，包含多个专门化的智能体和知识库管理系统。系统支持从创意概述、世界观构建、大纲设计、人物刻画到章节内容生成的完整小说创作流程。

## 系统架构

系统采用前后端分离架构：
- 后端：基于FastAPI的RESTful API服务，集成多个专业化智能体
- 前端：基于React的响应式Web应用，提供直观的用户交互界面
- 数据存储：内存数据存储（可扩展为持久化数据库）
- 部署方式：永久部署在公共可访问的服务器上

## 部署步骤

### 1. 后端部署

1. 安装依赖：
```bash
cd /home/ubuntu/novel_generator/backend
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
export OPENAI_API_KEY=your_openai_api_key
```

3. 启动后端服务：
```bash
cd /home/ubuntu/novel_generator/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端部署

1. 安装依赖：
```bash
cd /home/ubuntu/novel_generator/frontend
pnpm install
```

2. 构建前端应用：
```bash
cd /home/ubuntu/novel_generator/frontend
pnpm build
```

3. 部署静态文件：
```bash
# 将构建好的静态文件部署到Web服务器
```

### 3. 永久部署

使用deploy_apply_deployment工具将应用永久部署到公共可访问的URL：

```bash
# 部署后端Flask应用
deploy_apply_deployment --type flask --local_dir /home/ubuntu/novel_generator/backend

# 部署前端静态网站
deploy_apply_deployment --type static --local_dir /home/ubuntu/novel_generator/frontend/dist
```

## 访问方式

部署完成后，可通过以下URL访问系统：

- 前端应用：https://[deployed_frontend_url]
- 后端API：https://[deployed_backend_url]/api

## 系统功能

系统提供以下核心功能：

1. **项目管理**：创建、查看、编辑和删除小说项目
2. **概述生成**：基于用户输入生成多个小说创意概述
3. **世界观构建**：生成详细、自洽的世界观设定
4. **大纲设计**：生成章节大纲和情节发展规划
5. **人物刻画**：生成主要人物的详细设定
6. **章节生成**：基于大纲生成小说章节内容
7. **剧情分支**：提供多个剧情发展方向选择
8. **内容润色**：优化和提升已生成的内容质量

## 使用指南

1. 访问系统首页，点击"开始创作"按钮
2. 创建新项目，输入项目标题和描述
3. 按照引导完成小说创作流程：
   - 输入创作灵感，生成小说概述
   - 选择喜欢的概述，生成世界观设定
   - 基于世界观设定生成章节大纲
   - 生成人物设定
   - 逐章生成小说内容
4. 在项目详情页查看创作进度和已生成内容
5. 可随时编辑、润色或重新生成任何部分内容

## 系统维护

- 定期检查API密钥有效性
- 监控系统性能和响应时间
- 根据用户反馈持续优化和更新系统功能

## 技术栈

- 后端：Python, FastAPI, LangChain, OpenAI API
- 前端：TypeScript, React, Tailwind CSS
- 部署：永久部署服务

## 联系方式

如有任何问题或需要技术支持，请联系系统管理员。
