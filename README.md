# Google Trends 市场机会分析系统

> 每天自动采集 Google Trends 关键词数据，分析趋势走向，发现新产品/服务市场机会。
>
> **完全免费部署** — GitHub Actions + Supabase + Vercel，月费用 $0。

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│              GitHub Actions (免费)                    │
│         每天凌晨2点自动运行 Python 程序                 │
│  ┌─────────────────────────────────────────────┐    │
│  │ 1. pytrends 采集 Google Trends 数据          │    │
│  │ 2. scipy/numpy 趋势分析和机会评分            │    │
│  │ 3. 写入 Supabase 数据库                      │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │ 写入数据
                       ▼
┌─────────────────────────────────────────────────────┐
│              Supabase (免费)                          │
│         免费 PostgreSQL 数据库 (500MB)                │
│  ┌─────────────┬──────────────┬────────────────┐     │
│  │ trends_data │ trend_analysis│ opportunities  │     │
│  └─────────────┴──────────────┴────────────────┘     │
└──────────────────────┬──────────────────────────────┘
                       │ 读取数据
                       ▼
┌─────────────────────────────────────────────────────┐
│              Vercel (免费)                            │
│         Next.js 前端仪表板托管                         │
│  ┌─────────────────────────────────────────────┐    │
│  │ 📊 仪表板 │ 🎯 市场机会 │ 📈 趋势分析       │    │
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
│   │   ├── database.py          # Supabase 数据库操作
│   │   ├── collector.py         # Google Trends 数据采集
│   │   ├── analyzer.py          # 趋势分析（评分/预测/异常检测）
│   │   └── opportunity.py       # 市场机会识别
│   ├── requirements.txt         # Python 依赖
│   └── run_daily.py             # 每日任务入口
│
├── frontend/                    # Next.js 前端（部署到 Vercel）
│   ├── src/
│   │   ├── app/                 # 页面
│   │   │   ├── page.tsx         # 仪表板
│   │   │   ├── opportunities/   # 市场机会
│   │   │   └── trends/          # 趋势分析
│   │   └── lib/                 # 工具库
│   └── package.json
│
├── supabase/
│   └── schema.sql               # 数据库建表脚本
│
├── .github/workflows/
│   └── daily-collection.yml     # GitHub Actions 定时任务
│
├── .env.example                 # 环境变量模板
└── README.md                    # 本文件
```

## 部署指南（约15分钟）

### 第1步：创建 Supabase 数据库（3分钟）

1. 打开 https://supabase.com 注册账号（可用 GitHub 登录）
2. 点击 **New Project** 创建项目
3. 填写项目名称，选择离你最近的区域，设置数据库密码
4. 等待项目创建完成（约1-2分钟）
5. 进入项目后，左侧菜单点击 **SQL Editor**
6. 点击 **New query**，将 `supabase/schema.sql` 的内容粘贴进去
7. 点击 **Run** 执行建表脚本
8. 左侧菜单进入 **Settings > API**，记录以下信息：
   - **Project URL**（如 `https://xxxx.supabase.co`）
   - **anon public key**（一长串字符）

### 第2步：创建 GitHub 仓库并配置 Secrets（3分钟）

1. 打开 https://github.com 新建一个仓库（公开或私有均可）
2. 将本项目代码推送到仓库：
   ```bash
   git init
   git add .
   git commit -m "初始化 Google Trends 分析系统"
   git branch -M main
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git push -u origin main
   ```
3. 在仓库页面进入 **Settings > Secrets and variables > Actions**
4. 点击 **New repository secret**，添加以下 secrets：
   - Name: `SUPABASE_URL`，Value: 第1步记录的 Project URL
   - Name: `SUPABASE_KEY`，Value: 第1步记录的 anon public key
   - （可选）`TRENDS_KEYWORDS`：自定义监控关键词，逗号分隔
   - （可选）`TRENDS_REGIONS`：自定义地区代码，逗号分隔

### 第3步：测试 GitHub Actions（2分钟）

1. 在仓库页面点击 **Actions** 标签
2. 左侧选择 **Daily Trends Collection**
3. 点击 **Run workflow** 手动触发一次测试
4. 等待执行完成（约3-5分钟），查看日志确认无错误
5. 执行成功后，数据会自动写入 Supabase

### 第4步：部署前端到 Vercel（5分钟）

1. 打开 https://vercel.com 注册账号（可用 GitHub 登录）
2. 点击 **Add New > Project**
3. 选择你刚创建的 GitHub 仓库
4. 配置项目：
   - **Root Directory**: 点击 Edit，选择 `frontend` 目录
   - **Framework Preset**: Next.js
   - **Environment Variables**: 添加以下两个变量：
     - `NEXT_PUBLIC_SUPABASE_URL` = 你的 Supabase URL
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = 你的 Supabase anon key
5. 点击 **Deploy**
6. 等待部署完成（约2-3分钟），获得访问网址（如 `https://your-app.vercel.app`）

### 第5步：验证（2分钟）

1. 打开 Vercel 分配的网址
2. 如果 GitHub Actions 已执行成功，你会看到：
   - 仪表板显示统计数据
   - 市场机会页面展示发现的机会
   - 趋势分析页面显示图表和数据表格
3. 之后每天凌晨2点，GitHub Actions 会自动采集和分析数据

## 本地开发

### Python 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 填入 Supabase URL 和 Key

# 手动运行一次采集
python run_daily.py
```

### 前端

```bash
cd frontend
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 填入 Supabase URL 和 Key

# 启动开发服务器
npm run dev
# 打开 http://localhost:3000
```

## 自定义配置

### 修改监控关键词

在 GitHub 仓库 **Settings > Secrets** 中设置：
- `TRENDS_KEYWORDS`: `关键词1,关键词2,关键词3,...`

或直接编辑 `backend/src/config.py` 中的默认值。

### 修改监控地区

地区代码参考：
- `""` = 全球
- `US` = 美国，`CN` = 中国，`GB` = 英国
- `DE` = 德国，`JP` = 日本，`FR` = 法国

在 GitHub Secrets 中设置 `TRENDS_REGIONS`。

### 修改采集时间

编辑 `.github/workflows/daily-collection.yml` 中的 cron 表达式：
```yaml
cron: '0 18 * * *'  # UTC 18:00 = 北京时间 02:00
```

## 常见问题

**Q: GitHub Actions 执行失败怎么办？**
A: 在仓库 Actions 页面点击失败的任务，查看日志排查。常见原因是 Supabase 密钥配置错误。

**Q: Google Trends 请求被限制怎么办？**
A: 代码已内置随机延迟（2-5秒）。如果仍被限制，减少关键词数量或降低采集频率。

**Q: Supabase 免费额度够用吗？**
A: 500MB 存储可存约50万条记录，按每天300条计算可使用4年以上。

**Q: 前端页面没有数据？**
A: 确认 GitHub Actions 已成功执行，且 Vercel 环境变量配置正确。

## 费用说明

| 服务 | 免费额度 | 本项目用量 | 费用 |
|------|---------|-----------|------|
| GitHub Actions | 2000分钟/月 | ~750分钟/月 | $0 |
| Supabase | 500MB 存储 | ~5MB/6个月 | $0 |
| Vercel | 100GB 流量 | <1GB/月 | $0 |
| **合计** | | | **$0/月** |
