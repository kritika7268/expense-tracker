import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("expensely.database")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

def get_engine():
    target_url = settings.DATABASE_URL
    is_mysql = target_url.startswith("mysql")
    
    if is_mysql:
        try:
            # Check if MySQL server is reachable and create DB if it doesn't exist
            from urllib.parse import urlparse
            parsed = urlparse(target_url)
            db_name = parsed.path.lstrip("/")
            
            # Base connection without db to verify/create database
            server_url = f"{parsed.scheme}://{parsed.netloc}/"
            server_engine = create_engine(server_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with server_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
            server_engine.dispose()
            
            engine = create_engine(target_url, pool_pre_ping=True, pool_recycle=3600)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database: %s", db_name)
            return engine
        except Exception as e:
            logger.warning("Could not connect to MySQL at %s: %s", target_url, str(e))
            logger.warning("Falling back to robust local SQLite database (expense_tracker.db) so application runs smoothly.")
            sqlite_url = "sqlite:///./expense_tracker.db"
            return create_engine(sqlite_url, connect_args={"check_same_thread": False})
    else:
        connect_args = {"check_same_thread": False} if "sqlite" in target_url else {}
        return create_engine(target_url, connect_args=connect_args)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models # ensure all models are imported before create_all
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
