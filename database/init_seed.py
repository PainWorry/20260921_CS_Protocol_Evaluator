from database.db import init_db, SessionLocal
from database.models import Employee, RubricVersion

def seed_database():
    init_db()
    db = SessionLocal()
    
    # เช็คว่ามีข้อมูลเกณฑ์ประเมินหรือยัง
    if db.query(RubricVersion).count() == 0:
        print("กำลังเพิ่มข้อมูล Rubric Version แรก...")
        rubric = RubricVersion(
            version_name="SD-CS-01 v1.0",
            content="1. ทักทายด้วยชื่อบริษัทและชื่อพนักงาน 2. ขอเบอร์โทรศัพท์เพื่อยืนยันตัวตนลูกค้า"
        )
        db.add(rubric)
        
        emp1 = Employee(emp_code="EMP001", name="ไผ่ (ทดสอบ)", department="Customer Service")
        emp2 = Employee(emp_code="EMP002", name="สมชาย (ทดสอบ)", department="Customer Service")
        db.add_all([emp1, emp2])
        
        db.commit()
        print("เพิ่มข้อมูลสำเร็จ!")
    else:
        print("ฐานข้อมูลมีข้อมูลอยู่แล้ว")
        
    db.close()

if __name__ == "__main__":
    seed_database()
