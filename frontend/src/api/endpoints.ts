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
}

// API 端点常量
export const API_ENDPOINTS: ApiEndpoints = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile'
  },
  
  // 文档相关
  DOCUMENTS: {
    LIST: '/documents',
    CREATE: '/documents',
    DETAIL: (id: string | number) => `/documents/${id}`,
    UPDATE: (id: string | number) => `/documents/${id}`,
    DELETE: (id: string | number) => `/documents/${id}`,
    SEARCH: '/documents/search',
    BATCH_DELETE: '/documents/batch',
    UPLOAD: '/documents/upload'
  },
  
  // 搜索相关
  SEARCH: {
    QUERY: '/search/query',
    CHAT: '/chat/completions',
    HISTORY: '/search/history',
    SUGGESTIONS: '/search/suggestions'
  },
  
  // 采集相关
  COLLECTION: {
    RSS_SOURCES: '/collection/rss',
    RSS_SOURCE: (id: string | number) => `/collection/rss/${id}`,
    WEB_CRAWL: '/collection/crawl',
    CRAWL_TASKS: '/collection/tasks',
    CRAWL_TASK: (id: string | number) => `/collection/tasks/${id}`
  },
  
  // 分析相关
  ANALYTICS: {
    OVERVIEW: '/analytics/overview',
    DOCUMENTS_STATS: '/analytics/documents',
    SEARCH_STATS: '/analytics/search',
    USER_ACTIVITY: '/analytics/activity',
    TRENDS: '/analytics/trends'
  },
  
  // 上传相关
  UPLOAD: {
    FILE: '/upload/file',
    BATCH: '/upload/batch',
    PROGRESS: (taskId: string | number) => `/upload/progress/${taskId}`
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