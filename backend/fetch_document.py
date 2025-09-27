from models.rss_source import RssSource
from sqlmodel import Session
from sqlmodel.sql.expression import Select
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.rss_source import RssSource


def fetch_rss_feeds(id:int, session:Session):
    rss_source = session.exec(Select(RssSource).where(RssSource.id == id)).first()
    if rss_source:
        logger.info(rss_source)


if __name__ == "__main__":
    from sqlmodel import Session, SQLModel, create_engine
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        fetch_rss_feeds(1, session)