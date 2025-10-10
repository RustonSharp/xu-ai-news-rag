// API 端点常量类型定义
type EndpointFunction = (id: string | number) => string

interface AuthEndpoints {
  LOGIN: string
  REGISTER: string
  REFRESH: string
  LOGOUT: string
  PROFILE: string
}

interface DocumentsEndpoints {
  LIST: string
  CREATE: string
  DETAIL: EndpointFunction
  UPDATE: EndpointFunction
  DELETE: EndpointFunction
  SEARCH: string
  BATCH_DELETE: string
  UPLOAD: string
  UPLOAD_EXCEL: string
}

interface SearchEndpoints {
  QUERY: string
  CHAT: string
  HISTORY: string
  SUGGESTIONS: string
}

interface CollectionEndpoints {
  RSS_SOURCES: string
  RSS_SOURCE: EndpointFunction
  RSS_FEEDS: EndpointFunction
  WEB_SOURCES: string
  WEB_SOURCE: EndpointFunction
  WEB_CRAWL: string
  CRAWL_TASKS: string
  CRAWL_TASK: EndpointFunction
}

interface AnalyticsEndpoints {
  OVERVIEW: string
  DOCUMENTS_STATS: string
  SEARCH_STATS: string
  USER_ACTIVITY: string
  TRENDS: string
}

interface AssistantEndpoints {
  QUERY: string
  HEALTH: string
}

interface UploadEndpoints {
  FILE: string
  BATCH: string
  PROGRESS: EndpointFunction
}

interface ApiEndpoints {
  AUTH: AuthEndpoints
  DOCUMENTS: DocumentsEndpoints
  SEARCH: SearchEndpoints
  COLLECTION: CollectionEndpoints
  ANALYTICS: AnalyticsEndpoints
  UPLOAD: UploadEndpoints
  ASSISTANT: AssistantEndpoints
}

// API 端点常量
export const API_ENDPOINTS: ApiEndpoints = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    REFRESH: '/api/auth/refresh',
    LOGOUT: '/api/auth/logout',
    PROFILE: '/api/auth/profile'
  },

  // 文档相关
  DOCUMENTS: {
    LIST: '/api/documents',
    CREATE: '/api/documents',
    DETAIL: (id: string | number) => `/api/documents/${id}`,
    UPDATE: (id: string | number) => `/api/documents/${id}`,
    DELETE: (id: string | number) => `/api/documents/${id}`,
    SEARCH: '/api/documents/search',
    BATCH_DELETE: '/api/documents/batch',
    UPLOAD: '/api/documents/upload',
    UPLOAD_EXCEL: '/api/documents/upload_excel'
  },

  // 搜索相关
  SEARCH: {
    QUERY: '/api/search/query',
    CHAT: '/api/chat/completions',
    HISTORY: '/api/search/history',
    SUGGESTIONS: '/api/search/suggestions'
  },

  // 采集相关
  COLLECTION: {
    RSS_SOURCES: '/api/sources',
    RSS_SOURCE: (id: string | number) => `/api/sources/${id}`,
    RSS_FEEDS: (id: string | number) => `/api/sources/${id}/feeds`,
    WEB_SOURCES: '/api/sources',
    WEB_SOURCE: (id: string | number) => `/api/sources/${id}`,
    WEB_CRAWL: '/api/collection/crawl',
    CRAWL_TASKS: '/api/collection/tasks',
    CRAWL_TASK: (id: string | number) => `/api/collection/tasks/${id}`
  },

  // 分析相关
  ANALYTICS: {
    OVERVIEW: '/api/analytics/overview',
    DOCUMENTS_STATS: '/api/analytics/documents',
    SEARCH_STATS: '/api/analytics/search',
    USER_ACTIVITY: '/api/analytics/activity',
    TRENDS: '/api/analytics/trends'
  },

  // 上传相关
  UPLOAD: {
    FILE: '/api/upload/file',
    BATCH: '/api/upload/batch',
    PROGRESS: (taskId: string | number) => `/api/upload/progress/${taskId}`
  },

  // 助手相关
  ASSISTANT: {
    QUERY: '/api/assistant/query',
    HEALTH: '/api/assistant/health'
  }
}

// HTTP 方法常量
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
  PATCH: 'PATCH'
} as const

export type HttpMethod = typeof HTTP_METHODS[keyof typeof HTTP_METHODS]

// 响应状态码常量
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const

export type HttpStatus = typeof HTTP_STATUS[keyof typeof HTTP_STATUS]