import threading
import time
import datetime
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
                now = datetime.datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                
                with Session(engine) as session:
                    # 获取所有RSS源
                    rss_sources = session.exec(select(RssSource)).all()
                    
                    for rss_source in rss_sources:
                        # 检查RSS源是否暂停
                        if hasattr(rss_source, 'is_paused') and rss_source.is_paused:
                            continue
                            
                        # 检查是否已经有该RSS源的线程在运行
                        with self.lock:
                            if rss_source.id in self.threads and self.threads[rss_source.id].is_alive():
                                continue
                            
                            # 检查是否到了执行时间
                            if self._should_execute_now(rss_source.interval, current_hour, current_minute):
                                # 创建新的线程来处理RSS源
                                thread = threading.Thread(
                                    target=self._process_rss_source,
                                    args=(rss_source.id,)
                                )
                                thread.daemon = True
                                thread.start()
                                self.threads[rss_source.id] = thread
                                app_logger.info(f"Started RSS fetch thread for source {rss_source.name} (ID: {rss_source.id}) with interval {rss_source.interval}")
                
                # 每小时检查一次
                time.sleep(60 * 60)
                
            except Exception as e:
                app_logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60 * 60)  # 发生错误时等待一小时
    
    def _should_execute_now(self, interval_str, current_hour, current_minute):
        """检查当前时间是否应该执行RSS获取"""
        # 只在整点执行（分钟为0）
        if current_minute != 0:
            return False
            
        if interval_str == 'SIX_HOUR':
            # 每6小时执行一次：0点、6点、12点、18点
            return current_hour in [0, 6, 12, 18]
        elif interval_str == 'TWELVE_HOUR':
            # 每12小时执行一次：0点、12点
            return current_hour in [0, 12]
        elif interval_str == 'ONE_DAY':
            # 每天执行一次：0点
            return current_hour == 0
        else:
            # 默认为每天执行一次：0点
            return current_hour == 0
    
    def _process_rss_source(self, rss_id: int):
        """处理单个RSS源的定时任务"""
        try:
            with Session(engine) as session:
                # 检查RSS源是否仍然存在
                rss_source = session.exec(select(RssSource).where(RssSource.id == rss_id)).first()
                if not rss_source:
                    app_logger.info(f"RSS source with ID {rss_id} no longer exists, stopping thread")
                    return
                
                # 检查RSS源是否暂停
                if hasattr(rss_source, 'is_paused') and rss_source.is_paused:
                    app_logger.info(f"RSS source {rss_source.name} (ID: {rss_id}) is paused, skipping fetch")
                    return
                
                # 执行RSS获取
                app_logger.info(f"Fetching RSS for source {rss_source.name} (ID: {rss_id})")
                success = fetch_rss_feeds(rss_id, session)
                
                if success:
                    app_logger.info(f"Successfully fetched RSS for source {rss_source.name} (ID: {rss_id})")
                else:
                    app_logger.warning(f"Failed to fetch RSS for source {rss_source.name} (ID: {rss_id})")
                    
        except Exception as e:
            app_logger.error(f"Error processing RSS source {rss_id}: {str(e)}")
        finally:
            # 线程结束时清理
            with self.lock:
                if rss_id in self.threads:
                    del self.threads[rss_id]
            app_logger.info(f"RSS fetch thread for source ID {rss_id} completed")

# 创建全局调度器实例
rss_scheduler = RSSScheduler()