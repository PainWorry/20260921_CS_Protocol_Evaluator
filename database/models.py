from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Employee(Base):
    """ข้อมูลพนักงาน (Employees)"""
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    emp_code = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    
    sessions = relationship("TestSession", back_populates="employee")

class RubricVersion(Base):
    """ตารางเก็บเวอร์ชันของเกณฑ์ประเมิน (Temporal Tables สำหรับ PDCA)"""
    __tablename__ = "rubric_versions"
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String) # เช่น "SD-CS-01 v1.0"
    content = Column(Text) # เนื้อหาของกฎ
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sessions = relationship("TestSession", back_populates="rubric")

class TestSession(Base):
    """บันทึกประวัติการทดสอบแต่ละครั้ง (Test Sessions)"""
    __tablename__ = "test_sessions"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    rubric_id = Column(Integer, ForeignKey("rubric_versions.id"))
    
    test_type = Column(String) # "Theory", "Applied", "Real 3CX"
    transcript = Column(Text)
    report_json = Column(Text)
    overall_score = Column(Float)
    status = Column(String) # "Pass", "Review Required"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    employee = relationship("Employee", back_populates="sessions")
    rubric = relationship("RubricVersion", back_populates="sessions")
    cases = relationship("CaseRepository", back_populates="session")

class CaseRepository(Base):
    """คลังเก็บกรณีศึกษาที่น่าสนใจสำหรับทำโค้ชชิ่ง (Case Repository)"""
    __tablename__ = "case_repository"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"))
    tags = Column(String) # เช่น "ลูกค้าโกรธ", "ลืมรหัสผ่าน"
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("TestSession", back_populates="cases")
