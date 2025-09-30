# API 封装使用指南

本项目已经完成了专业的 API 封装，统一管理所有接口调用。以下是使用指南：

## 目录结构

```
src/api/
├── index.js          # 统一入口文件
├── request.js        # 核心请求封装
├── endpoints.js      # API 端点常量
└── modules/          # API 模块
    ├── auth.js       # 认证相关接口
    ├── documents.js  # 文档相关接口
    ├── search.js     # 搜索相关接口
    ├── collection.js # 采集相关接口
    └── analytics.js  # 分析相关接口
```

## 基本使用

### 1. 导入 API 模块

```javascript
// 导入单个模块
import { authAPI, documentsAPI, searchAPI } from "../api";

// 或者导入默认对象
import api from "../api";
```

### 2. 使用示例

#### 认证相关

```javascript
// 用户登录
const loginResult = await authAPI.login("user@example.com", "password");

// 用户注册
const registerResult = await authAPI.register("user@example.com", "password");

// 获取用户信息
const userProfile = await authAPI.getProfile();

// 用户登出
await authAPI.logout();
```

#### 文档管理

```javascript
// 获取文档列表
const documents = await documentsAPI.getDocuments({
  page: 1,
  size: 20,
  search: "关键词",
  type: "pdf",
});

// 获取文档详情
const document = await documentsAPI.getDocument(documentId);

// 上传文档
const formData = new FormData();
formData.append("file", file);
const uploadResult = await documentsAPI.uploadDocument(formData, (progress) => {
  console.log(`上传进度: ${progress}%`);
});

// 删除文档
await documentsAPI.deleteDocument(documentId);

// 批量删除
await documentsAPI.batchDeleteDocuments([id1, id2, id3]);
```

#### 搜索功能

```javascript
// 语义搜索
const searchResults = await searchAPI.search({
  query: "人工智能",
  filters: { type: "pdf" },
  size: 20,
});

// 智能问答
const chatResponse = await searchAPI.chat({
  query: "什么是机器学习？",
  conversation_id: "conv_123",
});

// 获取搜索历史
const history = await searchAPI.getSearchHistory({ page: 1, size: 10 });

// 获取搜索建议
const suggestions = await searchAPI.getSearchSuggestions("AI");
```

#### 数据采集

```javascript
// 获取 RSS 源列表
const rssSources = await collectionAPI.getRssSources();

// 创建 RSS 源
const newRssSource = await collectionAPI.createRssSource({
  name: "TechCrunch",
  url: "https://techcrunch.com/feed/",
  description: "科技新闻",
  update_interval: 60,
});

// 创建网页爬取任务
const crawlTask = await collectionAPI.createWebCrawlTask({
  url: "https://example.com",
  name: "示例网站爬取",
  config: { max_pages: 10 },
});

// 获取爬取任务状态
const taskStatus = await collectionAPI.getCrawlTask(taskId);
```

#### 数据分析

```javascript
// 获取总览数据
const overview = await analyticsAPI.getOverview({ period: "7d" });

// 获取文档统计
const docStats = await analyticsAPI.getDocumentsStats({
  period: "month",
  groupBy: "type",
});

// 获取搜索统计
const searchStats = await analyticsAPI.getSearchStats({ period: "week" });

// 获取趋势数据
const trends = await analyticsAPI.getTrends({
  metric: "documents",
  period: "day",
  days: 30,
});
```

## 错误处理

所有 API 调用都应该使用 try-catch 进行错误处理：

```javascript
try {
  const result = await authAPI.login(email, password);
  if (result.data.success) {
    // 处理成功逻辑
  }
} catch (error) {
  console.error("API 调用失败:", error);
  // 处理错误逻辑
  if (error.response?.status === 401) {
    // 处理认证失败
  } else if (error.response?.status === 500) {
    // 处理服务器错误
  }
}
```

## 认证管理

项目提供了便捷的认证管理方法：

```javascript
import { setAuthToken, getAuthToken, clearAuth } from "../api";

// 设置认证 token
setAuthToken("your-jwt-token");

// 获取当前 token
const token = getAuthToken();

// 清除认证信息
clearAuth();
```

## 自定义请求实例

如果需要创建带有特定配置的请求实例：

```javascript
import { createAPIInstance } from "../api";

const customAPI = createAPIInstance({
  baseURL: "https://api.example.com",
  timeout: 10000,
  headers: {
    "Custom-Header": "value",
  },
});
```

## 注意事项

1. **统一错误处理**: 所有 API 调用都通过统一的拦截器处理错误
2. **自动认证**: 请求会自动添加认证 token
3. **响应格式**: 所有 API 返回的都是 axios response 对象，数据在 `response.data` 中
4. **类型安全**: 建议配合 TypeScript 使用以获得更好的类型提示
5. **缓存策略**: 可以根据需要在各个模块中添加缓存逻辑

## 迁移指南

如果你的代码中还在使用 `axios` 直接调用，请按以下方式迁移：

### 迁移前

```javascript
import axios from "axios";

const response = await axios.post("/auth/login", { email, password });
```

### 迁移后

```javascript
import { authAPI } from "../api";

const response = await authAPI.login(email, password);
```

这样的封装提供了更好的代码组织、类型安全和维护性。
