from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# ใช้ SQLite เพื่อไม่ให้มีค่าใช้จ่าย (สามารถเปลี่ยนเป็น PostgreSQL ได้ทันทีในอนาคต)
SQLALCHEMY_DATABASE_URL = "sqlite:///./acep_database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """สร้างตารางทั้งหมดในฐานข้อมูล"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """เชื่อมต่อและคืนค่า Session สำหรับใช้งาน"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
