import psycopg2

try:
    print("⏳ Cloud Database se connect ho rahe hain...")
    
    # Aapki Neon details ke saath connection setup
    connection = psycopg2.connect(
        host="ep-weathered-mountain-aor3k8jf.c-2.ap-southeast-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_vAq3jnVJEph0",
        port="5432",
        sslmode="require"  # Cloud DB ke liye yeh bohot zaroori hai
    )
    
    cursor = connection.cursor()

    # 1. Purane tables drop karein (fresh start ke liye)
    cursor.execute("DROP TABLE IF EXISTS ATTENDANCE CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS STUDENT CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS COURSES CASCADE;")

    # 2. Naye Tables banayein
    cursor.execute("""
    CREATE TABLE COURSES (
        COURSE_ID INT PRIMARY KEY,
        COURSE_NAME VARCHAR(50),
        FEES INT
    );
    """)

    cursor.execute("""
    CREATE TABLE STUDENT (
        ID INT PRIMARY KEY,
        NAME VARCHAR(25),
        COURSE_ID INT REFERENCES COURSES(COURSE_ID),
        SECTION VARCHAR(5),
        MARKS INT
    );
    """)

    cursor.execute("""
    CREATE TABLE ATTENDANCE (
        STUDENT_ID INT REFERENCES STUDENT(ID),
        ATTENDANCE_PCT INT
    );
    """)

    # 3. Dummy Data Insert Karein
    courses_data = [
        (101, 'Data Science', 50000),
        (102, 'Web Dev', 40000),
        (103, 'Cyber Security', 45000)
    ]
    cursor.executemany("INSERT INTO COURSES VALUES (%s, %s, %s);", courses_data)

    students_data = [
        (1, 'Aarav', 101, 'A', 90),
        (2, 'Isha', 101, 'B', 85),
        (3, 'Vivaan', 102, 'A', 75),
        (4, 'Ananya', 102, 'B', 95),
        (5, 'Kabir', 101, 'A', 60)
    ]
    cursor.executemany("INSERT INTO STUDENT VALUES (%s, %s, %s, %s, %s);", students_data)

    attendance_data = [
        (1, 92),
        (2, 88),
        (3, 75),
        (4, 96),
        (5, 65)
    ]
    cursor.executemany("INSERT INTO ATTENDANCE VALUES (%s, %s);", attendance_data)

    # Changes ko save karein
    connection.commit()
    print("🚀 Mubarak ho! Cloud PostgreSQL par aapka data successfully upload ho gaya hai!")

except Exception as error:
    print(f"❌ Cloud DB Connect karne mein dikkat aayi: {error}")

finally:
    if connection:
        cursor.close()
        connection.close()