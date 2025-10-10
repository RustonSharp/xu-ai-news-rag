"""
Scheduler service for RSS feed scheduling and management.
"""
import threading
import time
import datetime
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from models.source import Source
from models.document import Document
from core.database import db_manager
from services.document_service import DocumentService
from utils.logging_config import app_logger
import os


class SchedulerService:
    """Service for RSS scheduling operations."""
    
    def __init__(self):
        self.running = False
        self.threads = {}
        self.lock = threading.Lock()
        # Automatically start scheduler based on environment variable
        auto_start = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
        if auto_start:
            self.start()
    
    def start(self):
        """Start the scheduled task scheduler."""
        if self.running:
            app_logger.warning("RSS scheduler is already running")
            return
            
        self.running = True
        app_logger.info("Starting RSS scheduler")
        
        # Start main scheduler thread
        scheduler_thread = threading.Thread(target=self._scheduler_loop)
        scheduler_thread.daemon = True
        scheduler_thread.start()
    
    def stop(self):
        """Stop the scheduled task scheduler."""
        if not self.running:
            app_logger.warning("RSS scheduler is not running")
            return
            
        self.running = False
        app_logger.info("Stopping RSS scheduler")
        
        # Wait for all threads to end
        with self.lock:
            for rss_id, thread in self.threads.items():
                if thread.is_alive():
                    thread.join(timeout=1)
            self.threads.clear()
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                now = datetime.datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                # Change from debug to info level so it's always visible
                app_logger.info(f"Scheduler tick at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Only execute at the top of the hour (minute is 0)
                if current_minute == 0:
                    with db_manager.get_session() as session:
                        # Determine target interval type based on current time
                        target_interval = None
                        if current_hour == 0:
                            target_interval = 'ONE_DAY'
                        elif current_hour == 6:
                            target_interval = 'SIX_HOUR'
                        elif current_hour == 12:
                            target_interval = 'TWELVE_HOUR'
                        
                        # If it's a target time, execute RSS sources with matching interval
                        if target_interval:
                            app_logger.info(f"Executing RSS sources with interval {target_interval} at {current_hour}:00")
                            
                            # Get all non-paused RSS sources with matching interval type
                            statement = select(Source).where(
                                Source.interval == target_interval,
                                Source.source_type == "rss"
                            )
                            # Check if is_paused field exists and filter
                            if hasattr(Source, 'is_paused'):
                                statement = statement.where(Source.is_paused == False)
                            
                            rss_sources = session.exec(statement).all()
                            
                            for rss_source in rss_sources:
                                # Check if there's already a thread running for this RSS source
                                with self.lock:
                                    if rss_source.id in self.threads and self.threads[rss_source.id].is_alive():
                                        continue
                                    
                                    # Create new thread to handle RSS source
                                    thread = threading.Thread(
                                        target=self._process_rss_source,
                                        args=(rss_source.id,)
                                    )
                                    thread.daemon = True
                                    thread.start()
                                    self.threads[rss_source.id] = thread
                                    app_logger.info(f"Started RSS fetch thread for source {rss_source.name} (ID: {rss_source.id}) with interval {rss_source.interval}")
                
                # Check every minute
                time.sleep(60)
                
            except Exception as e:
                app_logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Wait 1 minute when error occurs
    
    def _process_rss_source(self, rss_id: int):
        """Process scheduled task for a single RSS source."""
        try:
            with db_manager.get_session() as session:
                # Check if RSS source still exists
                rss_source = session.exec(
                    select(Source).where(Source.id == rss_id, Source.source_type == "rss")
                ).first()
                if not rss_source:
                    app_logger.info(f"RSS source with ID {rss_id} no longer exists, stopping thread")
                    return
                
                # Check if RSS source is paused
                if hasattr(rss_source, 'is_paused') and rss_source.is_paused:
                    app_logger.info(f"RSS source {rss_source.name} (ID: {rss_id}) is paused, skipping fetch")
                    return
                
                # Execute RSS fetch
                app_logger.info(f"Fetching RSS for source {rss_source.name} (ID: {rss_id})")
                document_service = DocumentService(session)
                success = document_service.fetch_rss_feeds(rss_id)
                
                if success:
                    # Update last sync time
                    from datetime import datetime
                    rss_source.last_sync = datetime.now()
                    
                    # Set next run time based on interval
                    now = datetime.now()
                    from datetime import timedelta
                    if rss_source.interval == 'SIX_HOUR':
                        # Run every 6 hours
                        rss_source.next_sync = now + timedelta(hours=6)
                    elif rss_source.interval == 'TWELVE_HOUR':
                        # Run every 12 hours
                        rss_source.next_sync = now + timedelta(hours=12)
                    else:  # ONE_DAY
                        # Run every 24 hours
                        rss_source.next_sync = now + timedelta(days=1)
                    
                    session.commit()
                    app_logger.info(f"Successfully fetched RSS for source {rss_source.name} (ID: {rss_id})")
                else:
                    app_logger.warning(f"Failed to fetch RSS for source {rss_source.name} (ID: {rss_id})")
                    
        except Exception as e:
            app_logger.error(f"Error processing RSS source {rss_id}: {str(e)}")
        finally:
            # Clean up when thread ends
            with self.lock:
                if rss_id in self.threads:
                    del self.threads[rss_id]
            app_logger.info(f"RSS fetch thread for source ID {rss_id} completed")

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        with self.lock:
            active_threads = {k: v.is_alive() for k, v in self.threads.items()}
        
        return {
            "running": self.running,
            "active_threads": active_threads,
            "total_threads": len(self.threads)
        }

    def force_sync_source(self, source_id: int) -> bool:
        """Force sync a specific source."""
        try:
            with db_manager.get_session() as session:
                document_service = DocumentService(session)
                success = document_service.fetch_rss_feeds(source_id)
                
                if success:
                    app_logger.info(f"Force sync successful for source {source_id}")
                else:
                    app_logger.warning(f"Force sync failed for source {source_id}")
                
                return success
        except Exception as e:
            app_logger.error(f"Error in force sync for source {source_id}: {str(e)}")
            return False

    def pause_source(self, source_id: int) -> bool:
        """Pause a specific source."""
        try:
            with db_manager.get_session() as session:
                source = session.exec(select(Source).where(Source.id == source_id)).first()
                if source and hasattr(source, 'is_paused'):
                    source.is_paused = True
                    session.commit()
                    app_logger.info(f"Source {source_id} paused")
                    return True
                return False
        except Exception as e:
            app_logger.error(f"Error pausing source {source_id}: {str(e)}")
            return False

    def resume_source(self, source_id: int) -> bool:
        """Resume a specific source."""
        try:
            with db_manager.get_session() as session:
                source = session.exec(select(Source).where(Source.id == source_id)).first()
                if source and hasattr(source, 'is_paused'):
                    source.is_paused = False
                    session.commit()
                    app_logger.info(f"Source {source_id} resumed")
                    return True
                return False
        except Exception as e:
            app_logger.error(f"Error resuming source {source_id}: {str(e)}")
            return False


# Global scheduler service instance
scheduler_service = SchedulerService()
