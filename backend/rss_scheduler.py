import threading
import time
import datetime
from sqlmodel import Session, select
from models.rss_source import RssSource
from models.document import Document
from utils.logging_config import app_logger
from utils.init_sqlite import engine
from fetch_document import fetch_rss_feeds
import os

class RSSScheduler:
    def __init__(self):
        self.running = False
        self.threads = {}
        self.lock = threading.Lock()
        # Automatically start scheduler based on environment variable
        auto_start = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
        if auto_start:
            self.start()
        
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
                # Change from debug to info level so it's always visible
                app_logger.info(f"Scheduler tick at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                # 只在整点执行（分钟为0）
                if current_minute == 0:
                    with Session(engine) as session:
                        # 根据当前时间确定要执行的间隔类型
                        target_interval = None
                        if current_hour == 0:
                            target_interval = 'ONE_DAY'
                        elif current_hour == 6:
                            target_interval = 'SIX_HOUR'
                        elif current_hour == 12:
                            target_interval = 'TWELVE_HOUR'
                        
                        # 如果是目标时间点，则执行对应间隔的RSS源
                        if target_interval:
                            app_logger.info(f"Executing RSS sources with interval {target_interval} at {current_hour}:00")
                            
                            # 获取所有未暂停且间隔类型匹配的RSS源
                            statement = select(RssSource).where(
                                RssSource.interval == target_interval
                            )
                            # 检查是否有is_paused字段并过滤
                            if hasattr(RssSource, 'is_paused'):
                                statement = statement.where(RssSource.is_paused == False)
                            
                            rss_sources = session.exec(statement).all()
                            
                            for rss_source in rss_sources:
                                # 检查是否已经有该RSS源的线程在运行
                                with self.lock:
                                    if rss_source.id in self.threads and self.threads[rss_source.id].is_alive():
                                        continue
                                    
                                    # 创建新的线程来处理RSS源
                                    thread = threading.Thread(
                                        target=self._process_rss_source,
                                        args=(rss_source.id,)
                                    )
                                    thread.daemon = True
                                    thread.start()
                                    self.threads[rss_source.id] = thread
                                    app_logger.info(f"Started RSS fetch thread for source {rss_source.name} (ID: {rss_source.id}) with interval {rss_source.interval}")
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                app_logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # 发生错误时等待1分钟
    
    
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
                    # 更新上次同步时间
                    from datetime import datetime
                    rss_source.last_sync = datetime.now()
                    
                    # 根据interval设置下次运行时间
                    now = datetime.now()
                    from datetime import timedelta
                    if rss_source.interval == 'SIX_HOUR':
                        # 每6小时运行一次
                        rss_source.next_sync = now + timedelta(hours=6)
                    elif rss_source.interval == 'TWELVE_HOUR':
                        # 每12小时运行一次
                        rss_source.next_sync = now + timedelta(hours=12)
                    else:  # ONE_DAY
                        # 每24小时运行一次
                        rss_source.next_sync = now + timedelta(days=1)
                    
                    session.commit()
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