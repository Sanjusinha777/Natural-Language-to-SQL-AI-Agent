import pandas as pd
import os
from sqlalchemy import create_engine

# 1. Apni Neon Connection String
DATABASE_URL = "postgresql://neondb_owner:npg_oqgPNiTnE8B4@ep-blue-scene-aopoibfw-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DATABASE_URL)

# 2. Files ki mapping (File ka naam aur Table ka naam)
# Dhyan rahe: Agar files 'dataset' folder mein hain, toh path 'dataset/filename' hoga
files_to_upload = {
    "dataset/olist_customers_dataset.csv": "customers",
    "dataset/olist_orders_dataset.csv": "orders",
    "dataset/olist_products_dataset.csv": "products"
}

# 3. Automatic upload script
for path, table_name in files_to_upload.items():
    if os.path.exists(path):
        print(f"✅ File mili: {path}. Upload shuru ho raha hai...")
        try:
            df = pd.read_csv(path)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"🚀 Success: '{table_name}' table upload ho gayi!")
        except Exception as e:
            print(f"❌ Error during upload: {e}")
    else:
        print(f"❌ Error: File nahi mili - {path}")
        print("💡 Tip: Check karein ki 'dataset' folder aur files usi folder mein hain jahan yeh script hai.")
