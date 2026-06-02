import streamlit as st
import psycopg2
import pandas as pd
from google import genai

# ================= CONFIGURATION =================
# Apni Neon connection string ko yahan set karein
DATABASE_URL = "postgresql://neondb_owner:npg_oqgPNiTnE8B4@ep-blue-scene-aopoibfw-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# System Prompt (Olist E-commerce Schema ke liye)
prompt = """
You are an expert in writing PostgreSQL queries for Olist E-commerce data.
The database has these tables:
1. CUSTOMERS (customer_id, customer_city, customer_state, ...)
2. ORDERS (order_id, customer_id, order_status, order_purchase_timestamp, ...)
3. PRODUCTS (product_id, product_category_name, ...)

If the user asks about sales or orders, join ORDERS and CUSTOMERS on customer_id.
Return only the raw SQL query, no markdown, no extra text.
"""


def get_gemini_response(question, system_prompt):
    # 1. API Key set karo
    api_key = st.secrets["AQ.Ab8RN6JpXnQRmdoBv4JB4FLvJXr6aPu-JYsFLrgywpY0WPEQnA"]
    genai.configure(api_key=api_key)
    
    # 2. Model call karo
    model = genai.GenerativeModel('gemini-1.5-flash', 
                                  system_instruction=system_prompt)
    response = model.generate_content(question)
    return response.text.strip()

# Baki sab wahi purana code...

def read_sql_query(sql):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    conn.close()
    return rows, colnames

# --- UI ---
st.set_page_config(page_title="Olist AI Assistant", layout="wide")
st.title("🛒 Olist E-commerce AI Data Analyst")

user_question = st.text_input("Ask Question (e.g., 'How many customers are from Sao Paulo?')")

if st.button("Get Data"):
    with st.spinner("Processing..."):
        sql = get_gemini_response(user_question, prompt)
        st.code(sql)
        data, cols = read_sql_query(sql)
        st.dataframe(pd.DataFrame(data, columns=cols))
