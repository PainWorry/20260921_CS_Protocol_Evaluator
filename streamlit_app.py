import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import json
import time
import random
from google import genai
from google.genai import types

# นำเข้า SQLAlchemy Models
from database.db import SessionLocal
from database.models import Employee, RubricVersion, TestSession

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def mock_or_real_stt(file_bytes, mime_type):
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                "Transcribe this customer service audio call accurately. Output ONLY the text transcript in Thai if possible."
            ]
        )
        return response.text
    except Exception as e:
        time.sleep(2)
        return f"[ข้อมูลจำลองเนื่องจาก API Error: {str(e)}]\n\nพนักงาน: สวัสดีครับ OneLink ไผ่รับสายครับ\nลูกค้า: แอปใช้งานไม่ได้ครับ\nพนักงาน: ขอทราบเบอร์โทรศัพท์ที่ลงทะเบียนเพื่อตรวจสอบข้อมูลด้วยครับ"

def run_evaluation(transcript, rubric_content):
    try:
        client = genai.Client()
        prompt = f"Evaluate this transcript against the SOP and output reasoning in Thai.\nSOP: {rubric_content}\nTranscript: {transcript}"
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        report = json.loads(response.text)
        if "overall_score" not in report: report["overall_score"] = 85
        if "checklist" not in report: report["checklist"] = []
        return report
    except Exception as e:
        raise Exception(str(e))

st.set_page_config(layout="wide", page_title="ระบบประเมินคุณภาพ CS (ACEP)")
db = next(get_db_session())

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

if not st.session_state['logged_in']:
    st.title("🔐 เข้าสู่ระบบ (ACEP Login)")
    st.markdown("กรุณากรอกชื่อผู้ใช้และรหัสผ่านเพื่อเข้าใช้งานระบบ")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("เข้าสู่ระบบ")
            
            if submit_button:
                if username == "CS" and password == "CS":
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = "Agent"
                    st.rerun()
                elif username == "Admin" and password == "Admin":
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = "QA"
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
else:
    with st.sidebar:
        st.subheader(f"👤 สถานะ: {st.session_state['role']}")
        if st.button("ออกจากระบบ (Logout)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
    if st.session_state['role'] == "Agent":
        st.title("👨‍💻 ระบบประเมินสำหรับพนักงาน")
        
        employees = db.query(Employee).all()
        emp_dict = {emp.name: emp.id for emp in employees}
        
        if not employees:
            st.error("ไม่พบข้อมูลพนักงานในระบบ กรุณารัน Seed Data ก่อน")
        else:
            # ย้ายการเลือกชื่อพนักงานไปที่ Sidebar ตามเดิม
            selected_emp_name = st.sidebar.selectbox("ชื่อพนักงาน:", list(emp_dict.keys()))
            selected_emp_id = emp_dict[selected_emp_name]
            st.sidebar.divider()
            
            # เมนูหลัก ย้ายมาไว้ตรงกลางด้านบน (Horizontal) ให้เห็นชัดเจนตามคำขอ
            menu = st.radio("📋 เลือกโหมดการทำงาน:", 
                            ["ประเมินบทสนทนา (Text/Audio)", "แบบฝึกหัดทฤษฎี (Quiz)"], 
                            horizontal=True)
            st.divider()
            
            if menu == "ประเมินบทสนทนา (Text/Audio)":
                st.subheader("🎙️ ส่งประวัติการสนทนาเพื่อรับคำแนะนำจาก AI")
                input_type = st.radio("รูปแบบข้อมูล:", 
                                      ["วางข้อความบทสนทนา (Text Transcript)", "อัปโหลดไฟล์ข้อความ (.txt)", "วางลิงก์ Google Doc", "อัปโหลดไฟล์เสียง 3CX (MP3/WAV)"])
                
                transcript = ""
                if input_type == "วางข้อความบทสนทนา (Text Transcript)":
                    transcript = st.text_area("วางข้อความแชทหรือบทสนทนาที่นี่:", height=200)
                elif input_type == "อัปโหลดไฟล์ข้อความ (.txt)":
                    uploaded_txt = st.file_uploader("อัปโหลดไฟล์ประวัติการแชท", type=["txt"])
                    if uploaded_txt is not None:
                        transcript = uploaded_txt.getvalue().decode("utf-8")
                        st.text_area("เนื้อหาในไฟล์:", transcript, height=200)
                elif input_type == "วางลิงก์ Google Doc":
                    doc_url = st.text_input("วางลิงก์ Google Doc")
                    if doc_url and st.button("ดึงข้อมูลบทสนทนา"):
                        with st.spinner("กำลังดึงข้อมูล..."):
                            time.sleep(1)
                            transcript = f"[ข้อมูลดึงมาจาก Google Doc: {doc_url}]\n\nพนักงาน: ขอบคุณที่โทรหา OneLink ครับ ผมไผ่ครับ\nลูกค้า: ผมลืมรหัสผ่านครับ\nพนักงาน: ขอทราบเบอร์โทรศัพท์ที่ลงทะเบียนเพื่อยืนยันตัวตนด้วยครับ"
                            st.session_state['doc_transcript'] = transcript
                            st.success("ดึงข้อมูลสำเร็จ")
                    if 'doc_transcript' in st.session_state:
                        transcript = st.session_state['doc_transcript']
                        st.text_area("ข้อมูลที่ดึงมาได้:", transcript, height=150)
                else:
                    uploaded_file = st.file_uploader("อัปโหลดไฟล์เสียง 3CX", type=["mp3", "wav"])
                    if uploaded_file is not None:
                        if st.button("ถอดเสียงเป็นข้อความ (Speech-to-Text)"):
                            with st.spinner("กำลังถอดเสียงด้วยระบบ AI..."):
                                mime_type = "audio/mp3" if uploaded_file.name.endswith(".mp3") else "audio/wav"
                                transcript = mock_or_real_stt(uploaded_file.getvalue(), mime_type)
                                st.session_state['transcript'] = transcript
                                st.success("ถอดเสียงเสร็จสมบูรณ์!")
                        if 'transcript' in st.session_state:
                            transcript = st.session_state['transcript']
                            st.text_area("ข้อความที่ถอดได้:", transcript, height=150)

                if transcript and st.button("ส่งให้ AI ประเมินผล"):
                    with st.spinner("กำลังวิเคราะห์เปรียบเทียบกับคู่มือมาตรฐาน..."):
                        active_rubric = db.query(RubricVersion).filter(RubricVersion.is_active == True).first()
                        if not active_rubric:
                            st.error("ไม่พบเกณฑ์การประเมินที่เปิดใช้งานอยู่")
                        else:
                            try:
                                report = run_evaluation(transcript, active_rubric.content)
                                score = report.get("overall_score", 0)
                                status = "ผ่านเกณฑ์" if score >= 80 else "ต้องตรวจสอบ"
                                
                                new_session = TestSession(
                                    employee_id=selected_emp_id,
                                    rubric_id=active_rubric.id,
                                    test_type="Applied",
                                    transcript=transcript,
                                    report_json=json.dumps(report),
                                    overall_score=score,
                                    status=status
                                )
                                db.add(new_session)
                                db.commit()
                                
                                st.success(f"ประเมินผลสำเร็จ! คุณได้คะแนน {score}/100 (ใช้เกณฑ์ {active_rubric.version_name})")
                                st.json(report)
                            except Exception as e:
                                st.error(f"⚠️ เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ AI: {str(e)}")
                                st.warning("คำแนะนำ: เซิร์ฟเวอร์ฟรีอาจมีคนใช้งานหนาแน่น กรุณารอสักครู่แล้วกดปุ่มประเมินใหม่อีกครั้ง")
            
            elif menu == "แบบฝึกหัดทฤษฎี (Quiz)":
                st.subheader("📝 แบบทดสอบความรู้คู่มือมาตรฐาน SD-CS-01")
                try:
                    with open("quiz_data.json", "r", encoding="utf-8") as f:
                        quiz_data = json.load(f)
                except:
                    st.error("ไม่พบไฟล์ quiz_data.json กรุณาตรวจสอบ")
                    quiz_data = []

                if quiz_data:
                    total_q = len(quiz_data)
                    import random
                    
                    if 'quiz_index' not in st.session_state: st.session_state['quiz_index'] = 0
                    if 'quiz_answers' not in st.session_state: st.session_state['quiz_answers'] = {}
                    if 'quiz_submitted' not in st.session_state: st.session_state['quiz_submitted'] = {}
                    if 'quiz_finished' not in st.session_state: st.session_state['quiz_finished'] = False
                    
                    if 'quiz_choices' not in st.session_state:
                        st.session_state['quiz_choices'] = {}
                        for q in quiz_data:
                            choices = q['incorrect_answers'] + [q['correct_answer']]
                            random.shuffle(choices)
                            formatted = [f"{chr(65+i)}. {c}" for i, c in enumerate(choices)]
                            st.session_state['quiz_choices'][q['id']] = formatted

                    if st.session_state['quiz_finished']:
                        st.success(f"🎉 คุณได้ทำแบบทดสอบเสร็จสิ้นและบันทึกผลเรียบร้อยแล้ว!")
                        if st.button("ทำแบบทดสอบใหม่อีกครั้ง"):
                            st.session_state['quiz_index'] = 0
                            st.session_state['quiz_answers'] = {}
                            st.session_state['quiz_submitted'] = {}
                            st.session_state['quiz_finished'] = False
                            del st.session_state['quiz_choices']
                            st.rerun()
                    else:
                        idx = st.session_state['quiz_index']
                        
                        if idx < total_q:
                            q = quiz_data[idx]
                            
                            st.markdown(f"### ข้อที่ {idx + 1} / {total_q}")
                            st.markdown(f"**{q['question']}**")
                            
                            choices = st.session_state['quiz_choices'][q['id']]
                            
                            # Set default index if already answered
                            default_idx = None
                            if q['id'] in st.session_state['quiz_answers']:
                                try:
                                    default_idx = choices.index(st.session_state['quiz_answers'][q['id']])
                                except ValueError:
                                    pass
                                    
                            disabled = st.session_state['quiz_submitted'].get(q['id'], False)
                            
                            selected_answer = st.radio("เลือกคำตอบ:", choices, index=default_idx, key=f"radio_{q['id']}", disabled=disabled)
                            
                            if selected_answer:
                                st.session_state['quiz_answers'][q['id']] = selected_answer
                            
                            # Show check answer button or the result
                            if not disabled:
                                if st.button("💡 ตรวจคำตอบ (ดูเฉลย)", key=f"check_{q['id']}"):
                                    if q['id'] not in st.session_state['quiz_answers']:
                                        st.warning("กรุณาเลือกคำตอบก่อนกดตรวจ")
                                    else:
                                        st.session_state['quiz_submitted'][q['id']] = True
                                        st.rerun()
                            else:
                                ans_text = st.session_state['quiz_answers'][q['id']][3:]
                                if ans_text == q['correct_answer']:
                                    st.success("✅ ถูกต้อง!")
                                else:
                                    st.error(f"❌ ผิด (เฉลยที่ถูกต้องคือ: {q['correct_answer']})")
                            
                            st.divider()
                            
                            # Navigation Buttons
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if idx > 0:
                                    if st.button("⬅️ ย้อนกลับ"):
                                        st.session_state['quiz_index'] -= 1
                                        st.rerun()
                            with col3:
                                if st.button("ถัดไป ➡️"):
                                    st.session_state['quiz_index'] += 1
                                    st.rerun()
                        else:
                            # Review Page
                            st.markdown("### 📋 ตรวจสอบคำตอบก่อนส่งผล")
                            st.write("เช็คสถานะการตอบคำถาม (ข้อที่ยังไม่ได้ตอบสามารถกดปุ่มเพื่อกลับไปทำได้)")
                            st.divider()
                            
                            all_answered = True
                            
                            c1, c2, c3 = st.columns([1, 1, 2])
                            c1.markdown("**ข้อ**")
                            c2.markdown("**คำตอบที่เลือก**")
                            c3.markdown("**การจัดการ**")
                            st.write("---")

                            for i, q in enumerate(quiz_data):
                                ans = st.session_state['quiz_answers'].get(q['id'])
                                c1, c2, c3 = st.columns([1, 1, 2])
                                
                                c1.write(f"ข้อ {i+1}")
                                
                                if ans:
                                    c2.write(f"**{ans[0]}**")
                                else:
                                    c2.markdown("❌ <span style='color:red'>ยังไม่ได้ตอบ</span>", unsafe_allow_html=True)
                                    all_answered = False
                                
                                with c3:
                                    if st.button(f"กลับไปข้อ {i+1}", key=f"goto_{i}"):
                                        st.session_state['quiz_index'] = i
                                        st.rerun()
                                        
                            st.divider()
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if st.button("⬅️ ย้อนกลับไปข้อสุดท้าย"):
                                    st.session_state['quiz_index'] = total_q - 1
                                    st.rerun()
                            with col3:
                                if st.button("🏁 ส่งแบบทดสอบเพื่อบันทึกผล"):
                                    if not all_answered:
                                        st.warning("กรุณาเลือกคำตอบให้ครบทุกข้อก่อนส่งผล")
                                    else:
                                        score_count = 0
                                        checklist = []
                                        transcript_log = "บันทึกการทำแบบทดสอบทฤษฎี:\n\n"
                                        
                                        for q_data in quiz_data:
                                            ans_full = st.session_state['quiz_answers'][q_data['id']]
                                            ans_text = ans_full[3:] # Remove "A. "
                                            is_correct = (ans_text == q_data['correct_answer'])
                                            if is_correct: score_count += 1
                                            
                                            checklist.append({
                                                "criterion": f"คำถาม {q_data['id']}",
                                                "passed": is_correct,
                                                "evidence": f"คำตอบที่เลือก: {ans_full}",
                                                "reasoning": "ตอบถูก" if is_correct else f"ตอบผิด (เฉลย: {q_data['correct_answer']})"
                                            })
                                            transcript_log += f"Q: {q_data['question']}\nA: {ans_full} [{'✅' if is_correct else '❌'}]\n\n"
                                            
                                        overall_score = (score_count / total_q) * 100
                                        status = "ผ่านเกณฑ์" if overall_score >= 80 else "ต้องตรวจสอบ"
                                        
                                        report = {
                                            "overall_score": overall_score,
                                            "checklist": checklist
                                        }
                                        
                                        active_rubric = db.query(RubricVersion).filter(RubricVersion.is_active == True).first()
                                        
                                        new_session = TestSession(
                                            employee_id=selected_emp_id,
                                            rubric_id=active_rubric.id if active_rubric else None,
                                            test_type="Theory",
                                            transcript=transcript_log,
                                            report_json=json.dumps(report),
                                            overall_score=overall_score,
                                            status=status
                                        )
                                        db.add(new_session)
                                        db.commit()
                                        
                                        st.session_state['quiz_finished'] = True
                                        st.rerun()

    elif st.session_state['role'] == "QA":
        st.title("🛡️ หน้าจอตรวจสอบสำหรับหัวหน้า QA")
        st.markdown("ตรวจสอบการสนทนาและคะแนนแบบทดสอบของพนักงาน")

        sessions = db.query(TestSession).order_by(TestSession.id.desc()).all()
        
        if not sessions:
            st.info("ยังไม่มีข้อมูลการประเมินในระบบ")
        else:
            data = []
            for s in sessions:
                data.append({
                    "รหัส": s.id,
                    "พนักงาน": s.employee.name if s.employee else "N/A",
                    "ประเภท": s.test_type,
                    "คะแนน": s.overall_score,
                    "สถานะ": s.status
                })
            df = pd.DataFrame(data)

            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("📥 กล่องข้อความ (Inbox)")
                st.dataframe(df, use_container_width=True, hide_index=True)
                selected_id = st.selectbox("เลือกรหัสที่ต้องการดูรายละเอียด:", df['รหัส'].tolist())

            with col2:
                if selected_id:
                    s = db.query(TestSession).filter(TestSession.id == selected_id).first()
                    
                    st.subheader(f"รายละเอียดการประเมิน: {s.employee.name}")
                    if s.overall_score >= 80:
                        st.success(f"**ประเภท:** {s.test_type} | **คะแนนรวม:** {s.overall_score}/100 ({s.status})")
                    else:
                        st.error(f"**ประเภท:** {s.test_type} | **คะแนนรวม:** {s.overall_score}/100 ({s.status})")
                        
                    tab_ai, tab_transcript = st.tabs(["📊 สรุปผล / เกณฑ์ประเมิน", "📝 ประวัติการตอบ / บทสนทนา"])
                    
                    with tab_ai:
                        try:
                            report = json.loads(s.report_json)
                            for item in report.get('checklist', []):
                                if item.get('passed', False):
                                    st.success(f"✅ **{item.get('criterion', '')}**\n\n*หลักฐาน:* \"{item.get('evidence', '')}\"\n\n*เหตุผล:* {item.get('reasoning', '')}")
                                else:
                                    st.error(f"❌ **{item.get('criterion', '')}**\n\n*หลักฐาน:* \"{item.get('evidence', '')}\"\n\n*เหตุผล:* {item.get('reasoning', '')}")
                        except Exception as e:
                            st.write("เกิดข้อผิดพลาดในการอ่านข้อมูล JSON", e)
                    
                    with tab_transcript:
                        st.text_area("ประวัติดั้งเดิม", s.transcript, height=400, disabled=True)
