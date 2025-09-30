// Mock 服务器 - 模拟后端 API 响应

// 模拟数据
const mockData = {
  // 用户数据
  users: [
    {
      id: 1,
      email: 'admin@example.com',
      username: 'admin',
      role: 'admin',
      createdAt: '2024-01-01T00:00:00Z'
    }
  ],
  
  // 文档数据
  documents: [
    {
      id: 1,
      title: '人工智能发展趋势报告',
      content: '人工智能技术正在快速发展...',
      type: 'pdf',
      size: 1024000,
      uploadedAt: '2024-01-15T10:30:00Z',
      created_at: '2024-01-15T10:30:00Z',
      status: 'processed',
      source: 'AI研究院',
      url: 'https://example.com/ai-report.pdf',
    },
    {
      id: 2,
      title: '机器学习最佳实践',
      content: '机器学习在各个领域的应用...',
      type: 'docx',
      size: 512000,
      uploadedAt: '2024-01-14T15:20:00Z',
      created_at: '2024-01-14T15:20:00Z',
      status: 'processed',
      source: '技术博客',
      url: 'https://example.com/ml-practices.docx',
    },
    {
      id: 3,
      title: '深度学习框架对比',
      content: 'TensorFlow、PyTorch等框架的详细对比...',
      type: 'pdf',
      size: 2048000,
      uploadedAt: '2024-01-13T09:15:00Z',
      created_at: '2024-01-13T09:15:00Z',
      status: 'processed',
      source: '开源社区',
      url: 'https://example.com/framework-comparison.pdf',
    }
  ],
  
  // 数据源
  sources: [
    {
      id: 1,
      name: 'AI新闻RSS',
      entry: 'https://example.com/ai-news.rss',
      description: 'AI相关新闻的RSS订阅源',
      schedule: '1h',
      enabled: true,
      last_run: '2024-01-15T12:00:00Z',
      next_run: '2024-01-15T13:00:00Z',
      articles_count: 25,
      filters: {
        keywords: 'AI,人工智能',
        excludeKeywords: '广告',
        minLength: 100
      },
      template: {
        type: 'rss'
      }
    },
    {
      id: 2,
      name: '科技博客',
      entry: 'https://example.com/tech-blog',
      description: '科技博客网站爬取',
      schedule: '2h',
      enabled: true,
      last_run: '2024-01-15T11:30:00Z',
      next_run: '2024-01-15T13:30:00Z',
      articles_count: 18,
      filters: {
        keywords: '科技,技术',
        excludeKeywords: '',
        minLength: 200
      },
      template: {
        type: 'css'
      }
    }
  ],
  
  // 分析数据
  analytics: {
    overview: {
      totalDocuments: 156,
      totalQueries: 1234,
      totalUsers: 45,
      systemHealth: 98.5
    },
    trends: [
      { date: '2024-01-01', documents: 10, queries: 50 },
      { date: '2024-01-02', documents: 15, queries: 75 },
      { date: '2024-01-03', documents: 12, queries: 60 }
    ]
  }
}

// 模拟延迟
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms))

// Mock API 响应
export const mockAPI = {
  // 认证相关
  auth: {
    async login(email, password) {
      await delay()
      if (email === 'admin@example.com' && password === 'admin123') {
        return {
          success: true,
          data: {
            token: 'mock-jwt-token-' + Date.now(),
            user: mockData.users[0]
          }
        }
      }
      throw new Error('用户名或密码错误')
    },
    
    async register(userData) {
      await delay()
      const newUser = {
        id: mockData.users.length + 1,
        ...userData,
        role: 'user',
        createdAt: new Date().toISOString()
      }
      mockData.users.push(newUser)
      return {
        success: true,
        data: {
          token: 'mock-jwt-token-' + Date.now(),
          user: newUser
        }
      }
    },
    
    async logout() {
      await delay(200)
      return { success: true }
    }
  },
  
  // 文档相关
  documents: {
    async getList(params = {}) {
      await delay()
      const { page = 1, size = 10, search = '' } = params
      let filtered = mockData.documents
      
      if (search) {
        filtered = filtered.filter(doc => 
          doc.title.toLowerCase().includes(search.toLowerCase())
        )
      }
      
      const start = (page - 1) * size
      const end = start + size
      
      return {
        success: true,
        data: {
          items: filtered.slice(start, end),
          total: filtered.length,
          page,
          size
        }
      }
    },
    
    async upload(file, onProgress) {
      await delay(1000)
      // 模拟上传进度
      if (onProgress) {
        for (let i = 0; i <= 100; i += 20) {
          setTimeout(() => onProgress({ loaded: i, total: 100 }), i * 10)
        }
      }
      
      const newDoc = {
        id: mockData.documents.length + 1,
        title: file.name,
        type: file.type,
        size: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'processing'
      }
      mockData.documents.push(newDoc)
      
      return {
        success: true,
        data: newDoc
      }
    },
    
    async delete(id) {
      await delay()
      const index = mockData.documents.findIndex(doc => doc.id === id)
      if (index > -1) {
        mockData.documents.splice(index, 1)
        return { success: true }
      }
      throw new Error('文档不存在')
    }
  },
  
  // 搜索相关
  search: {
    async semantic(query, params = {}) {
      await delay(800)
      return {
        success: true,
        data: {
          results: [
            {
              id: 1,
              title: '相关文档1',
              content: `关于"${query}"的相关内容...`,
              score: 0.95,
              source: 'document_1.pdf'
            },
            {
              id: 2,
              title: '相关文档2',
              content: `这里包含了"${query}"的详细信息...`,
              score: 0.87,
              source: 'document_2.docx'
            }
          ],
          total: 2
        }
      }
    },
    
    async chat(messages) {
      await delay(1200)
      const lastMessage = messages[messages.length - 1]
      return {
        success: true,
        data: {
          response: `基于您的问题"${lastMessage.content}"，我为您找到了以下信息：\n\n这是一个模拟的AI回答，展示了系统如何处理您的查询。在实际环境中，这里会显示基于RAG技术生成的智能回答。`,
          sources: [
            { title: '参考文档1', url: '/doc/1' },
            { title: '参考文档2', url: '/doc/2' }
          ]
        }
      }
    }
  },
  
  // 数据采集相关
  collection: {
    async getSources(params = {}) {
      await delay()
      return {
        success: true,
        data: {
          items: mockData.sources,
          total: mockData.sources.length
        }
      }
    },
    
    async createSource(sourceData) {
      await delay()
      const newSource = {
        id: mockData.sources.length + 1,
        ...sourceData,
        status: 'active',
        lastSync: new Date().toISOString()
      }
      mockData.sources.push(newSource)
      return {
        success: true,
        data: newSource
      }
    },
    
    async updateSource(id, sourceData) {
      await delay()
      const index = mockData.sources.findIndex(source => source.id === id)
      if (index > -1) {
        mockData.sources[index] = { ...mockData.sources[index], ...sourceData }
        return {
          success: true,
          data: mockData.sources[index]
        }
      }
      throw new Error('数据源不存在')
    },
    
    async deleteSource(id) {
      await delay()
      const index = mockData.sources.findIndex(source => source.id === id)
      if (index > -1) {
        mockData.sources.splice(index, 1)
        return { success: true }
      }
      throw new Error('数据源不存在')
    }
  },
  
  // 分析相关
  analytics: {
    async getOverview() {
      await delay()
      return {
        success: true,
        data: mockData.analytics.overview
      }
    },
    
    async getTrends(params = {}) {
      await delay()
      return {
        success: true,
        data: mockData.analytics.trends
      }
    }
  }
}

export default mockAPI