# ☁️ Cloud Drive Project

一个基于 Flask 的轻量级云盘系统，支持用户注册登录、文件上传下载与个人文件管理，适用于个人私有云或学习项目。

---

## 📌 项目简介

Cloud Drive Project 是一个基于 Python Flask 开发的 Web 云存储系统，提供完整的用户体系与文件管理功能。

每个用户拥有独立的文件空间，可以上传、下载和管理自己的文件，实现一个简单的“私有网盘”。

---

## ✨ 功能特性

### 👤 用户系统
- 用户注册（邀请码机制）
- 用户登录 / Session 管理
- 密码加密存储（Werkzeug）

### 📁 文件管理
- 文件上传
- 文件下载
- 文件删除
- 用户独立文件目录隔离

### 🔒 安全机制
- 防路径遍历攻击（目录隔离）
- Session 过期控制（30分钟）
- 密码哈希存储

### ⚙️ 系统功能
- 基于 JSON 的轻量数据存储
- 自动创建用户文件目录
- 支持多用户环境

---

## 🧱 技术栈

### 后端
- Python 3
- Flask
- Werkzeug（密码加密）

### 前端
- HTML（Jinja2 模板）
- CSS
- JavaScript

### 数据存储
- JSON 文件（users.json）
- 本地文件系统存储

---
```
## 📁 项目结构
cloud_drive_project/
├── app.py # 主程序（Flask入口）
├── config.py # 配置文件（邀请码等）
├── users.json # 用户数据存储
├── requirements.txt # 依赖列表
├── static/ # 静态资源
│ ├── css/
│ └── js/
├── templates/ # 前端页面
│ ├── login.html
│ ├── register.html
│ └── dashboard.html
└── user_files/ # 用户文件存储目录（自动生成）


---
```

## 🚀 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/lm060719/cloud_drive_project.git
cd cloud_drive_project
```
2️⃣ 安装依赖
```
pip install -r requirements.txt
```
3️⃣ 配置邀请码（可选）

编辑 config.py：
```

INVITATION_CODE = "your_code"
```
4️⃣ 启动项目
```
python app.py
```
5️⃣ 访问系统

打开浏览器：
```
http://127.0.0.1:5000
```
🔐 默认说明

注册需要邀请码

每个用户拥有独立文件目录

文件存储路径：user_files/<username>/

📡 核心逻辑说明
用户数据存储

使用 users.json 存储用户信息

包含用户名 + 加密密码

文件存储

每个用户独立目录

自动创建：
```
user_files/
└── username/
```
安全机制

防止路径跳转（目录限制）

Session 有效期控制

密码哈希（不可逆）

🧠 项目亮点（可以写简历）

✅ 基于 Flask 构建完整 Web 应用

✅ 实现用户系统 + 文件系统

✅ 具备基础安全防护（路径隔离 / 加密）

✅ 轻量架构（无需数据库）

✅ 可扩展为生产级云盘系统

🔮 可扩展方向

📦 文件分享链接（类似百度网盘）

⏱️ 文件过期时间

🔢 下载次数限制

🗂️ 文件夹系统

🧑‍🤝‍🧑 多用户权限管理

☁️ OSS / S3 存储接入

🎨 前端升级（Vue / React）

📸 项目截图（建议添加）

建议添加：

登录页

文件管理页

上传界面

🧑‍💻 作者
```
GitHub: https://github.com/lm060719
