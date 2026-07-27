# Google Trends 市场机会分析系统

> 每天自动采集 Google Trends 关键词数据，分析趋势走向，发现新产品/服务市场机会。
>
> **完全免费部署** — GitHub Actions + Neon + Vercel，月费用 $0。

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│              GitHub Actions (免费)                    │
│         每天凌晨2点自动运行 Python 程序                 │
│  ┌─────────────────────────────────────────────┐    │
│  │ 1. pytrends 采集 Google Trends 数据          │    │
│  │ 2. scipy/numpy 趋势分析和机会评分            │    │
│  │ 3. psycopg2 写入 Neon 数据库                 │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │ 写入数据
                       ▼
┌─────────────────────────────────────────────────────┐
│              Neon (免费)                              │
│         免费 PostgreSQL 数据库 (3GB)                  │
│  ┌─────────────┬──────────────┬────────────────┐     │
│  │ trends_data │ trend_analysis│ opportunities  │     │
│  └─────────────┴──────────────┴────────────────┘     │
└──────────────────────┬──────────────────────────────┘
                       │ 读取数据
                       ▼
┌─────────────────────────────────────────────────────┐
│              Vercel (免费)                            │
│      Next.js 前端 + API Routes (Serverless)           │
│  ┌─────────────────────────────────────────────┐    │
│  │ 仪表板 │ 市场机会 │ 趋势分析                  │    │
│  │ @neondatabase/serverless 驱动直连数据库      │    │
│  └─────────────────────────────────────────────┘    │
│  网址: xxx.vercel.app                               │
└─────────────────────────────────────────────────────┘
```

## 目录结构

```
google_trends_data/
├── backend/                     # Python 后端（运行在 GitHub Actions）
│   ├── src/
│   │   ├── config.py            # 环境变量配置
│   │   ├── database.py          # Neon PostgreSQL 操作 (psycopg2)
│   │   ├── collector.py         # Google Trends 数据采集
│   │   ├── analyzer.py          # 趋势分析
│   │   └── opportunity.py       # 市场机会识别
│   ├── requirements.txt
│   └── run_daily.py             # 每日任务入口
│
├── frontend/                    # Next.js 前端（部署到 Vercel）
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # 仪表板
│   │   │   ├── opportunities/   # 市场机会
│   │   │   ├── trends/          # 趋势分析
│   │   │   └── api/             # API Routes (Serverless)
│   │   ├── components/          # 图表组件
│   │   └── lib/
│   │       ├── db.ts            # Neon 连接
│   │       └── utils.ts         # 工具函数
│   └── package.json
│
├── database/
│   └── schema.sql               # 数据库建表脚本
│
├── .github/workflows/
│   └── daily-collection.yml     # GitHub Actions 定时任务
│
├── .env.example                 # 环境变量模板
└── README.md
```

## 部署指南（约15分钟）

### 第1步：创建 Neon 数据库（3分钟）

1. 打开 https://neon.tech 注册账号（可用 GitHub 登录）
2. 点击 **New Project** 创建项目
3. 填写项目名称，选择离你最近的区域
4. 等待项目创建完成（约30秒）
5. 在项目 Dashboard 页面，找到 **Connection Details**
6. 复制 **Connection String**（格式如 `postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require`）
7. 在 Neon 的 SQL Editor 中，将 `database/schema.sql` 的内容粘贴进去并执行
8. 保存好你的 Connection String

### 第2步：创建 GitHub 仓库并配置 Secrets（3分钟）

1. 打开 https://github.com 新建一个仓库
2. 将本项目代码推送到仓库：
   ```bash
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git push -u origin main
   ```
3. 在仓库 **Settings > Secrets and variables > Actions** 中添加：
   - Name: `DATABASE_URL`，Value: Neon 的 Connection String
   - （可选）`TRENDS_KEYWORDS`：自定义监控关键词
   - （可选）`TRENDS_REGIONS`：自定义地区代码

### 第3步：测试 GitHub Actions（2分钟）

1. 在仓库页面点击 **Actions** 标签
2. 选择 **Daily Trends Collection**
3. 点击 **Run workflow** 手动触发一次
4. 等待执行完成（约3-5分钟），确认无错误

### 第4步：部署前端到 Vercel（5分钟）

1. 打开 https://vercel.com 注册账号（可用 GitHub 登录）
2. 点击 **Add New > Project**，选择你的 GitHub 仓库
3. 配置项目：
   - **Root Directory**: 选择 `frontend` 目录
   - **Framework Preset**: Next.js
   - **Environment Variables**:
     - `DATABASE_URL` = Neon 的 Connection String
4. 点击 **Deploy**
5. 等待部署完成，获得访问网址

### 第5步：验证

1. 打开 Vercel 分配的网址
2. 确认 GitHub Actions 已成功执行后，仪表板会显示数据
3. 之后每天凌晨2点自动更新

## 本地开发

### Python 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 填入 DATABASE_URL

python run_daily.py
```

### 前端

```bash
cd frontend
npm install

cp .env.example .env.local
# 编辑 .env.local 填入 DATABASE_URL

npm run dev
# 打开 http://localhost:3000
```

## 费用说明

| 服务 | 免费额度 | 本项目用量 | 费用 |
|------|---------|-----------|------|
| GitHub Actions | 2000分钟/月 | ~750分钟/月 | $0 |
| Neon | 3GB 存储 | ~5MB/6个月 | $0 |
| Vercel | 100GB 流量 | <1GB/月 | $0 |
| **合计** | | | **$0/月** |
