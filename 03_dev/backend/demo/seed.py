"""
灌 demo 测试数据。

跑法（virtualenv 激活 + 后端已经跑过一次自动建表后）：
    python seed.py
"""
from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 如果已经有学生，跳过
if db.query(models.Student).count() == 0:
    students = [
        models.Student(name="itsuki"),       # 演示用主角
        models.Student(name="張三"),
        models.Student(name="李四"),
        models.Student(name="王五"),
        models.Student(name="田中太郎"),
        models.Student(name="佐藤花子"),
    ]
    db.add_all(students)
    db.commit()
    print(f"Seeded {len(students)} students:")
    for s in students:
        print(f"  id={s.id}, name={s.name}")
else:
    print("学生表已有数据，跳过 seed。")
    print("现有学生：")
    for s in db.query(models.Student).all():
        print(f"  id={s.id}, name={s.name}")

db.close()
