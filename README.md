# ☁️ Cloud Drive Project

一个基于 Web 的轻量级云盘系统，支持文件上传、下载、分享与管理，适用于个人资源分享与小型存储服务。

---

## 📌 项目简介

Cloud Drive Project 是一个简单易用的云存储系统，用户可以通过网页上传文件并生成分享链接，实现文件的便捷分发。

本项目适合作为：

- 💼 软件工程课程设计
- 📦 个人资源分享平台
- 🚀 Web 全栈练习项目

---

## ✨ 功能特性

- 📤 文件上传
- 📥 文件下载
- 🔗 文件分享链接生成
- ⏱️ 文件过期时间控制
- 🔢 下载次数限制
- 📊 流量统计（可扩展）
- 🔐 简单权限管理（单管理员）

---

## 🧱 技术栈

### 后端
- Go (Gin 框架)
- RESTful API

### 前端
- HTML / CSS / JavaScript
- （可扩展 Vue / React）

### 存储
- 本地文件存储（可扩展 OSS / S3）

---

## 📁 项目结构（示例）
cloud_drive_project/
├── server/ # 后端服务
├── web/ # 前端页面
├── uploads/ # 文件存储目录
├── config/ # 配置文件
├── main.go # 程序入口
└── README.md


---

## 🚀 快速开始

### 1️⃣ 克隆项目

```
git clone https://github.com/lm060719/cloud_drive_project.git
cd cloud_drive_project
```
2️⃣ 启动后端
```

go run main.go

或（生产模式）：

GIN_MODE=release ./cloud-drive
```
3️⃣ 打开浏览器

访问：
```
http://localhost:8080
```
⚙️ 配置说明

可在配置文件中修改：

服务端口

文件存储路径

过期时间策略

下载次数限制

📡 API 示例
上传文件
```
POST /upload
```
下载文件
```
GET /download/:id
```
获取分享链接
```
GET /share/:id
