import request from '../request';

export interface SchedulerStatus {
  running: boolean;
  rss_sources: Array<{
    id: number;
    name: string;
    url: string;
    interval: string | number; // 支持字符串和数字类型，以适应后端变更
    active: boolean;
  }>;
}

export const schedulerAPI = {
  // 获取调度器状态
  getStatus: async (): Promise<{ success: boolean; data?: SchedulerStatus; message?: string }> => {
    return request.get('/api/scheduler/status');
  },

  // 启动调度器
  start: async (): Promise<{ success: boolean; message?: string }> => {
    return request.post('/api/scheduler/start');
  },

  // 停止调度器
  stop: async (): Promise<{ success: boolean; message?: string }> => {
    return request.post('/api/scheduler/stop');
  },

  // 重启调度器
  restart: async (): Promise<{ success: boolean; message?: string }> => {
    return request.post('/api/scheduler/restart');
  },

  // 立即获取指定RSS源的新闻
  fetchRSS: async (rssId: number): Promise<{ success: boolean; message?: string }> => {
    return request.post(`/api/scheduler/fetch/${rssId}`);
  }
};