import streamlit as st
import psycopg2
import pandas as pd
from google import genai

# ================= CONFIGURATION =================
GEMINI_API_KEY = "AQ.Ab8RN6I3g2YrGWGwSGfTtfLSdsmXgGd19QDFhwz94PBXPbuTQg"  # <-- Apni asli Gemini API key yahan dalein
# Cloud Database Details (Aapki Neon String se extracted)
DB_HOST = "ep-weathered-mountain-aor3k8jf.c-2.ap-southeast-1.aws.neon.tech"
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "npg_vAq3jnVJEph0"
# =================================================

# Latest GenAI Client Setup (Direct Secrets integration)
try:
    # Streamlit Cloud ya local secrets.toml dono se utha lega
    api_key_to_use = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_to_use)
except Exception as e:
    st.error("⚠️ API Key not found in Streamlit Secrets! Please check Advanced Settings.")
    st.stop()

# System Prompt for Multi-Table
prompt = """
You are an expert in converting English questions to PostgreSQL queries!
The database contains 3 tables. Here is the schema:

1. COURSES:
   - COURSE_ID (INT) Primary Key
   - COURSE_NAME (VARCHAR)
   - FEES (INT)

2. STUDENT:
   - ID (INT) Primary Key
   - NAME (VARCHAR)
   - COURSE_ID (INT) Foreign Key references COURSES(COURSE_ID)
   - SECTION (VARCHAR)
   - MARKS (INT)

3. ATTENDANCE:
   - STUDENT_ID (INT) Foreign Key references STUDENT(ID)
   - ATTENDANCE_PCT (INT)

Join Instructions:
- To find which course a student is in, JOIN STUDENT and COURSES on STUDENT.COURSE_ID = COURSES.COURSE_ID.
- To find a student's attendance, JOIN STUDENT and ATTENDANCE on STUDENT.ID = ATTENDANCE.STUDENT_ID.

CRITICAL: Your output must only be the raw SQL query. Do not include markdown blocks like ```sql or ```, do not include the word 'sql', and do not add any extra text. Just return the raw SQL string.
"""

def get_gemini_response(question, system_prompt):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config={'system_instruction': system_prompt}
    )
    return response.text.strip()

def read_sql_query(sql):
    # Cloud Database se secure connection
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port="5432",
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    conn.close()
    return rows, colnames

# --- STREAMLIT UI ---
st.set_page_config(page_title="NL2SQL AI Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Talk to Your Cloud PostgreSQL Database")
st.subheader("Enter your question in plain English and get data instantly from Cloud!")

user_question = st.text_input("Ask a question about the Student Database:", placeholder="e.g., Show me the name of students with their course names")

submit = st.button("Generate & Fetch Data 🚀")

if submit and user_question:
    with st.spinner("AI is thinking and fetching data from cloud..."):
        try:
            # 1. Generate SQL
            generated_sql = get_gemini_response(user_question, prompt)
            st.code(generated_sql, language="sql")
            
            # 2. Fetch from Cloud DB
            data, columns = read_sql_query(generated_sql)
            
            # 3. Display Results
            if data:
                st.success("Data fetched from Cloud successfully!")
                df = pd.DataFrame(data, columns=columns)
                st.dataframe(df, width='stretch')
            else:
                st.warning("Query executed, but no records found.")
                
        except Exception as e:
            st.error(f"Error occurred: {e}")
