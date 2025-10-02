import threading
import time
from sqlmodel import Session, select
from models.rss_source import RssSource
from models.document import Document
from utils.logging_config import app_logger
from utils.init_sqlite import engine
from fetch_document import fetch_rss_feeds

class RSSScheduler:
    def __init__(self):
        self.running = False
        self.threads = {}
        self.lock = threading.Lock()
        
    def start(self):
        """启动定时任务调度器"""
        if self.running:
            app_logger.warning("RSS scheduler is already running")
            return
            
        self.running = True
        app_logger.info("Starting RSS scheduler")
        
        # 启动主调度线程
        scheduler_thread = threading.Thread(target=self._scheduler_loop)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
    def stop(self):
        """停止定时任务调度器"""
        if not self.running:
            app_logger.warning("RSS scheduler is not running")
            return
            
        self.running = False
        app_logger.info("Stopping RSS scheduler")
        
        # 等待所有线程结束
        with self.lock:
            for rss_id, thread in self.threads.items():
                if thread.is_alive():
                    thread.join(timeout=1)
            self.threads.clear()
    
    def _scheduler_loop(self):
        """主调度循环"""
        while self.running:
            try:
                with Session(engine) as session:
                    # 获取所有RSS源
                    rss_sources = session.exec(select(RssSource)).all()
                    
                    for rss_source in rss_sources:
                        # 检查是否已经有该RSS源的线程在运行
                        with self.lock:
                            if rss_source.id in self.threads and self.threads[rss_source.id].is_alive():
                                continue
                            
                            # 将字符串间隔转换为秒数
                            interval_seconds = self._interval_to_seconds(rss_source.interval)
                            
                            # 创建新的线程来处理RSS源
                            thread = threading.Thread(
                                target=self._process_rss_source,
                                args=(rss_source.id, interval_seconds)
                            )
                            thread.daemon = True
                            thread.start()
                            self.threads[rss_source.id] = thread
                            app_logger.info(f"Started RSS fetch thread for source {rss_source.name} (ID: {rss_source.id}) with interval {rss_source.interval} ({interval_seconds}s)")
                
                # 休眠一段时间，避免过于频繁的检查
                time.sleep(10)
                
            except Exception as e:
                app_logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(30)  # 发生错误时等待更长时间
    
    def _interval_to_seconds(self, interval_str):
        """将字符串间隔转换为秒数"""
        if interval_str == 'SIX_HOUR':
            return 6 * 60 * 60  # 6小时
        elif interval_str == 'TWELVE_HOUR':
            return 12 * 60 * 60  # 12小时
        elif interval_str == 'ONE_DAY':
            return 24 * 60 * 60  # 24小时
        else:
            # 默认为24小时
            return 24 * 60 * 60
    
    def _process_rss_source(self, rss_id: int, interval: int):
        """处理单个RSS源的定时任务"""
        while self.running:
            try:
                with Session(engine) as session:
                    # 检查RSS源是否仍然存在
                    rss_source = session.exec(select(RssSource).where(RssSource.id == rss_id)).first()
                    if not rss_source:
                        app_logger.info(f"RSS source with ID {rss_id} no longer exists, stopping thread")
                        break
                    
                    # 执行RSS获取
                    app_logger.info(f"Fetching RSS for source {rss_source.name} (ID: {rss_id})")
                    success = fetch_rss_feeds(rss_id, session)
                    
                    if success:
                        app_logger.info(f"Successfully fetched RSS for source {rss_source.name} (ID: {rss_id})")
                    else:
                        app_logger.warning(f"Failed to fetch RSS for source {rss_source.name} (ID: {rss_id})")
                
                # 等待指定的间隔时间
                # 将等待时间分成小块，以便能够及时响应停止信号
                wait_time = interval
                while wait_time > 0 and self.running:
                    sleep_chunk = min(10, wait_time)  # 每次最多休眠10秒
                    time.sleep(sleep_chunk)
                    wait_time -= sleep_chunk
                    
            except Exception as e:
                app_logger.error(f"Error processing RSS source {rss_id}: {str(e)}")
                # 发生错误时等待一段时间再重试
                time.sleep(60)
        
        # 线程结束时清理
        with self.lock:
            if rss_id in self.threads:
                del self.threads[rss_id]
        app_logger.info(f"RSS fetch thread for source ID {rss_id} stopped")

# 创建全局调度器实例
rss_scheduler = RSSScheduler()