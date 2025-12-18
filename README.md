# Aigen - AI 原生智能前端代码生成平台

> 🚧 **项目状态：持续更新与优化中 (Active Development)**
>
> 本项目目前处于快速迭代阶段，功能特性和架构设计可能会随时调整优化。欢迎 Star 关注最新进展！

Aigen 是一个基于 LLM（大语言模型）的智能软件工程 Agent 平台。它不仅仅是一个简单的代码生成器，而是一个利用 **LangGraph4j** 编排的复杂智能体工作流系统。

通过自然语言对话，Aigen 能够自动完成需求分析、素材收集、代码生成、质量检测、自动构建及部署的全流程，支持生成单页 HTML、多文件项目以及完整的 Vue 3 工程。

## ✨ 核心特性

- **🤖 智能工作流编排**: 基于图（Graph）结构的 Agent 协作流，包含素材收集、提示词增强、智能路由、代码生成、自我修正（Self-Correction）等环节。
- **🧩 多模式代码生成**:
  - **HTML 模式**: 生成轻量级单页应用。
  - **Vue 工程模式**: 生成包含组件、路由、状态管理的完整 Vue 3 + Vite + TypeScript 项目。
- **🛠️ 强大的文件系统操作**: Agent 具备“感知”和“操作”能力，可通过工具调用（Function Calling）读写、修改、删除项目文件，像人类程序员一样进行增量修改。
- **🎨 自动化素材集成**: 集成 Pexels (图片)、Undraw (插画)、Mermaid (架构图) 和 Wanx (Logo生成)，自动为生成的网站填充丰富内容。
- **🚀 自动化构建与部署**: 内置 Java 虚拟线程驱动的构建系统，自动执行 `npm install/build`，并实现一键部署与网页截图预览。
- **⚡ 沉浸式流式体验**: 基于 SSE (Server-Sent Events) 实现全链路流式响应，实时展示 Agent 的思考过程、工具调用状态和代码生成进度。

## 🛠️ 技术栈

### **Backend (Server)**
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.x-6DB33F?style=flat-square&logo=spring&logoColor=white)
![LangChain4j](https://img.shields.io/badge/AI-LangChain4j-blue?style=flat-square)
![LangGraph4j](https://img.shields.io/badge/Agent-LangGraph4j-blueviolet?style=flat-square)
![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![MyBatis-Flex](https://img.shields.io/badge/ORM-MyBatis_Flex-black?style=flat-square)

### **Frontend (Client)**
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Pinia](https://img.shields.io/badge/Store-Pinia-FFE46B?style=flat-square&logo=pinia&logoColor=black)
![Vue Router](https://img.shields.io/badge/Router-Vue_Router_4-4FC08D?style=flat-square&logo=vue.js&logoColor=white)

### **Infrastructure & Tools**
![DashScope](https://img.shields.io/badge/LLM-Alibaba_DashScope-FF6A00?style=flat-square)
![Selenium](https://img.shields.io/badge/Test-Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)
![Caffeine](https://img.shields.io/badge/Cache-Caffeine-orange?style=flat-square&logo=java&logoColor=white)
![Tencent Cloud](https://img.shields.io/badge/Cloud-Tencent_COS-00A4FF?style=flat-square&logo=tencent-qq&logoColor=white)

## 🏗️ 系统架构

本项目采用前后端分离架构，核心工作流基于 **LangGraph4j** 实现：

```mermaid
graph LR
    Start --> ImageCollector[素材收集]
    ImageCollector --> PromptEnhancer[提示词增强]
    PromptEnhancer --> Router[智能路由]
    Router --> CodeGenerator[代码生成]
    CodeGenerator --> QualityCheck{质量检查}
    QualityCheck -->|不通过| CodeGenerator
    QualityCheck -->|通过| ProjectBuilder[项目构建]
    ProjectBuilder --> End
