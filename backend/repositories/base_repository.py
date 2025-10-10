"""
Base repository class with common database operations.
"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlmodel import Session, select, func, and_, or_
from abc import ABC, abstractmethod
from utils.logging_config import app_logger

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    def create(self, obj: T) -> T:
        """Create a new object."""
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            app_logger.info(f"Created {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
            return obj
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get object by ID."""
        try:
            return self.session.get(self.model_class, id)
        except Exception as e:
            app_logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {str(e)}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination."""
        try:
            statement = select(self.model_class).offset(skip).limit(limit)
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error getting all {self.model_class.__name__}: {str(e)}")
            raise
    
    def update(self, id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """Update object by ID."""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return None
            
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            self.session.commit()
            self.session.refresh(obj)
            app_logger.info(f"Updated {self.model_class.__name__} with ID: {id}")
            return obj
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error updating {self.model_class.__name__} with ID {id}: {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """Delete object by ID."""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return False
            
            self.session.delete(obj)
            self.session.commit()
            app_logger.info(f"Deleted {self.model_class.__name__} with ID: {id}")
            return True
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"Error deleting {self.model_class.__name__} with ID {id}: {str(e)}")
            raise
    
    def count(self) -> int:
        """Count total objects."""
        try:
            statement = select(func.count()).select_from(self.model_class)
            return self.session.exec(statement).one()
        except Exception as e:
            app_logger.error(f"Error counting {self.model_class.__name__}: {str(e)}")
            raise
    
    def search(self, search_term: str, search_fields: List[str], skip: int = 0, limit: int = 100) -> List[T]:
        """Search objects by multiple fields."""
        try:
            conditions = []
            for field in search_fields:
                if hasattr(self.model_class, field):
                    field_attr = getattr(self.model_class, field)
                    conditions.append(field_attr.contains(search_term))
            
            if not conditions:
                return []
            
            statement = select(self.model_class).where(or_(*conditions)).offset(skip).limit(limit)
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error searching {self.model_class.__name__}: {str(e)}")
            raise
    
    def filter_by(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """Filter objects by multiple criteria."""
        try:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    field_attr = getattr(self.model_class, field)
                    if isinstance(value, list):
                        conditions.append(field_attr.in_(value))
                    else:
                        conditions.append(field_attr == value)
            
            if not conditions:
                return self.get_all(skip, limit)
            
            statement = select(self.model_class).where(and_(*conditions)).offset(skip).limit(limit)
            return list(self.session.exec(statement))
        except Exception as e:
            app_logger.error(f"Error filtering {self.model_class.__name__}: {str(e)}")
            raise
