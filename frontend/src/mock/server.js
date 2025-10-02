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
      created_at: '2024-01-01T00:00:00Z'
    }
  ],

  // 文档数据
  documents: [
    {
      id: 1,
      title: '人工智能发展趋势报告',
      description: '人工智能技术正在快速发展...',
      link: 'https://example.com/ai-report.pdf',
      pub_date: '2024-01-15T10:30:00Z',
      author: 'AI研究院',
      tags: 'AI,人工智能',
      rss_source_id: 1,
      crawled_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      title: '机器学习最佳实践',
      description: '机器学习在各个领域的应用...',
      link: 'https://example.com/ml-practices.docx',
      pub_date: '2024-01-14T15:20:00Z',
      author: '技术博客',
      tags: '机器学习,ML',
      rss_source_id: 1,
      crawled_at: '2024-01-14T15:20:00Z'
    },
    {
      id: 3,
      title: '深度学习框架对比',
      description: 'TensorFlow、PyTorch等框架的详细对比...',
      link: 'https://example.com/framework-comparison.pdf',
      pub_date: '2024-01-13T09:15:00Z',
      author: '开源社区',
      tags: '深度学习,框架',
      rss_source_id: 2,
      crawled_at: '2024-01-13T09:15:00Z'
    }
  ],

  // RSS源数据
  rssSources: [
    {
      id: 1,
      name: 'AI新闻RSS',
      url: 'https://example.com/ai-news.rss',
      interval: 'SIX_HOUR', // 6小时
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-15T12:00:00Z'
    },
    {
      id: 2,
      name: '科技博客',
      url: 'https://example.com/tech-blog',
      interval: 'TWELVE_HOUR', // 12小时
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-15T11:30:00Z'
    }
  ],

  // 聚类分析数据
  clusterAnalysis: {
    id: 1,
    created_at: '2024-01-15T12:00:00Z',
    clusters: [
      {
        id: 1,
        percentage: 35.5,
        keyword: '人工智能'
      },
      {
        id: 2,
        percentage: 28.3,
        keyword: '机器学习'
      },
      {
        id: 3,
        percentage: 20.2,
        keyword: '深度学习'
      },
      {
        id: 4,
        percentage: 16.0,
        keyword: '自然语言处理'
      }
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
          code: 200,
          message: '登录成功',
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
        created_at: new Date().toISOString()
      }
      mockData.users.push(newUser)
      return {
        code: 200,
        message: '注册成功',
        data: {
          token: 'mock-jwt-token-' + Date.now(),
          user: newUser
        }
      }
    },

    async logout() {
      await delay(200)
      return {
        code: 200,
        message: '登出成功',
        data: null
      }
    },

    async getProfile() {
      await delay()
      return {
        code: 200,
        message: '获取用户信息成功',
        data: mockData.users[0]
      }
    },

    async updateProfile(userData) {
      await delay()
      const updatedUser = { ...mockData.users[0], ...userData }
      mockData.users[0] = updatedUser
      return {
        code: 200,
        message: '更新用户信息成功',
        data: updatedUser
      }
    },

    async refreshToken() {
      await delay()
      return {
        code: 200,
        message: '刷新令牌成功',
        data: {
          token: 'mock-jwt-token-' + Date.now()
        }
      }
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
          doc.title.toLowerCase().includes(search.toLowerCase()) ||
          doc.description.toLowerCase().includes(search.toLowerCase())
        )
      }

      const start = (page - 1) * size
      const end = start + size

      return {
        code: 200,
        message: '获取文档列表成功',
        data: {
          items: filtered.slice(start, end),
          total: filtered.length,
          page,
          size,
          total_pages: Math.ceil(filtered.length / size)
        }
      }
    },

    async getPage(params = {}) {
      await delay()
      const { page = 1, size = 10, search = '' } = params
      let filtered = mockData.documents

      if (search) {
        filtered = filtered.filter(doc =>
          doc.title.toLowerCase().includes(search.toLowerCase()) ||
          doc.description.toLowerCase().includes(search.toLowerCase())
        )
      }

      const start = (page - 1) * size
      const end = start + size

      return {
        code: 200,
        message: '获取文档分页列表成功',
        data: {
          items: filtered.slice(start, end),
          total: filtered.length,
          page,
          size,
          total_pages: Math.ceil(filtered.length / size)
        }
      }
    },

    async getDetail(id) {
      await delay()
      const document = mockData.documents.find(doc => doc.id === id)
      if (document) {
        return {
          code: 200,
          message: '获取文档详情成功',
          data: document
        }
      }
      throw new Error('文档不存在')
    },

    async getDocumentsBySourceId(sourceId) {
      await delay()
      const documents = mockData.documents.filter(doc => doc.rss_source_id === sourceId)
      return {
        code: 200,
        message: '获取源文档成功',
        data: documents
      }
    },

    async getClusterAnalysis() {
      await delay()
      return {
        code: 200,
        message: '获取聚类分析成功',
        data: mockData.clusterAnalysis
      }
    },

    async getLatestClusterAnalysis() {
      await delay()
      return {
        code: 200,
        message: '获取最新聚类分析成功',
        data: mockData.clusterAnalysis
      }
    },

    async uploadExcel(file) {
      await delay(1000)

      return {
        code: 200,
        message: '上传Excel成功',
        data: {
          message: 'Excel文件上传成功，已添加3个文档'
        }
      }
    },

    async upload(formData, onProgress) {
      await delay(1000)
      // 模拟上传进度
      if (onProgress) {
        for (let i = 0; i <= 100; i += 20) {
          setTimeout(() => onProgress({ loaded: i, total: 100 }), i * 10)
        }
      }

      const newDoc = {
        id: mockData.documents.length + 1,
        title: formData.get('title') || '新文档',
        description: formData.get('description') || '文档描述',
        link: formData.get('link') || '',
        pub_date: new Date().toISOString(),
        author: formData.get('author') || '未知作者',
        tags: formData.get('tags') || '',
        rss_source_id: parseInt(formData.get('rss_source_id')) || 1,
        crawled_at: new Date().toISOString()
      }
      mockData.documents.push(newDoc)

      return {
        code: 200,
        message: '上传文档成功',
        data: {
          id: newDoc.id
        }
      }
    },

    async delete(id) {
      await delay()
      const index = mockData.documents.findIndex(doc => doc.id === id)
      if (index > -1) {
        mockData.documents.splice(index, 1)
        return {
          code: 200,
          message: '删除文档成功',
          data: null
        }
      }
      throw new Error('文档不存在')
    }
  },

  // RSS源相关
  rss: {
    async getRssSources(params = {}) {
      await delay()
      return {
        code: 200,
        message: '获取RSS源列表成功',
        data: {
          items: mockData.rssSources,
          total: mockData.rssSources.length
        }
      }
    },

    async getRssSource(id) {
      await delay()
      const source = mockData.rssSources.find(src => src.id === id)
      if (source) {
        return {
          code: 200,
          message: '获取RSS源成功',
          data: source
        }
      }
      throw new Error('RSS源不存在')
    },

    async createRssSource(sourceData) {
      await delay()
      const newSource = {
        id: mockData.rssSources.length + 1,
        ...sourceData,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      mockData.rssSources.push(newSource)
      return {
        code: 200,
        message: '创建RSS源成功',
        data: newSource
      }
    },

    async updateRssSource(id, sourceData) {
      await delay()
      const index = mockData.rssSources.findIndex(source => source.id === id)
      if (index > -1) {
        mockData.rssSources[index] = {
          ...mockData.rssSources[index],
          ...sourceData,
          updated_at: new Date().toISOString()
        }
        return {
          code: 200,
          message: '更新RSS源成功',
          data: mockData.rssSources[index]
        }
      }
      throw new Error('RSS源不存在')
    },

    async deleteRssSource(id) {
      await delay()
      const index = mockData.rssSources.findIndex(source => source.id === id)
      if (index > -1) {
        mockData.rssSources.splice(index, 1)
        return {
          code: 200,
          message: '删除RSS源成功',
          data: null
        }
      }
      throw new Error('RSS源不存在')
    },

    async getRssFeeds(id) {
      await delay()
      // 模拟RSS订阅内容
      const feeds = [
        {
          id: 1,
          title: 'AI新闻1',
          description: '人工智能最新动态',
          link: 'https://example.com/ai-news-1',
          pub_date: new Date().toISOString(),
          author: 'AI新闻编辑部'
        },
        {
          id: 2,
          title: 'AI新闻2',
          description: '机器学习新突破',
          link: 'https://example.com/ai-news-2',
          pub_date: new Date(Date.now() - 3600000).toISOString(),
          author: 'AI新闻编辑部'
        }
      ]
      return {
        code: 200,
        message: '获取RSS订阅内容成功',
        data: feeds
      }
    },

    async triggerRssCollection(id) {
      await delay(1500)
      return {
        code: 200,
        message: 'RSS采集任务已触发',
        data: {
          message: 'RSS采集任务已成功触发，预计需要2分钟完成'
        }
      }
    }
  },

  // 助手相关
  assistant: {
    async query(params) {
      await delay(1200)
      const { query, options = {} } = params

      return {
        code: 200,
        message: '查询成功',
        data: {
          response: `基于您的问题"${query}"，我为您找到了以下信息：\n\n这是一个模拟的AI回答，展示了系统如何处理您的查询。在实际环境中，这里会显示基于RAG技术生成的智能回答，结合知识库和在线搜索的结果。`,
          sources: [
            {
              title: '人工智能发展趋势报告',
              content: '人工智能技术正在快速发展...',
              link: 'https://example.com/ai-report.pdf'
            },
            {
              title: '机器学习最佳实践',
              content: '机器学习在各个领域的应用...',
              link: 'https://example.com/ml-practices.docx'
            }
          ]
        }
      }
    },

    async health() {
      await delay(300)
      return {
        code: 200,
        message: '服务正常',
        data: {
          status: 'healthy',
          message: 'AI助手服务运行正常'
        }
      }
    }
  }
}

export default mockAPI