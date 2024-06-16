from faker import Faker
import psycopg2
import random


def create_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="567234",  # Ваш пароль
        host="localhost",
        port="5438"  # Ваш порт
    )


def main():
    fake = Faker()
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Видалення існуючих таблиць
        cursor.execute("""
            DROP TABLE IF EXISTS grades;
            DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS subjects;
            DROP TABLE IF EXISTS teachers;
            DROP TABLE IF EXISTS groups;
        """)
        conn.commit()

        # Створення таблиць
        cursor.execute("""
            -- Таблиця груп
            CREATE TABLE groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );

            -- Таблиця викладачів
            CREATE TABLE teachers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );

            -- Таблиця предметів
            CREATE TABLE subjects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                teacher_id INTEGER NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            );

            -- Таблиця студентів
            CREATE TABLE students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                group_id INTEGER NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            );

            -- Таблиця оцінок
            CREATE TABLE grades (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 100),
                grade_date DATE NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            );
        """)
        conn.commit()

        # Додавання груп
        groups = ['Group A', 'Group B', 'Group C']
        for group in groups:
            cursor.execute("INSERT INTO groups (name) VALUES (%s)", (group,))

        conn.commit()

        # Отримання ідентифікаторів груп
        cursor.execute("SELECT id FROM groups")
        group_ids = [row[0] for row in cursor.fetchall()]

        # Додавання викладачів
        for _ in range(4):
            cursor.execute("INSERT INTO teachers (name) VALUES (%s)", (fake.name(),))

        conn.commit()

        # Отримання ідентифікаторів викладачів
        cursor.execute("SELECT id FROM teachers")
        teacher_ids = [row[0] for row in cursor.fetchall()]

        # Додавання предметів
        subjects = ['Math', 'Physics', 'Chemistry', 'History', 'Literature', 'Biology', 'Geography', 'Computer Science']
        for subject in subjects:
            cursor.execute("INSERT INTO subjects (name, teacher_id) VALUES (%s, %s)",
                           (subject, random.choice(teacher_ids)))

        conn.commit()

        # Отримання ідентифікаторів предметів
        cursor.execute("SELECT id FROM subjects")
        subject_ids = [row[0] for row in cursor.fetchall()]

        # Додавання студентів
        for _ in range(50):
            cursor.execute("INSERT INTO students (name, group_id) VALUES (%s, %s)",
                           (fake.name(), random.choice(group_ids)))

        conn.commit()

        # Отримання ідентифікаторів студентів
        cursor.execute("SELECT id FROM students")
        student_ids = [row[0] for row in cursor.fetchall()]

        # Додавання оцінок
        for student_id in student_ids:
            for subject_id in subject_ids:
                grade_entries = []
                for _ in range(random.randint(5, 20)):  # До 20 оцінок
                    grade_entries.append((student_id, subject_id, random.randint(60, 100), fake.date_this_year()))
                cursor.executemany(
                    "INSERT INTO grades (student_id, subject_id, grade, grade_date) VALUES (%s, %s, %s, %s)",
                    grade_entries)

        conn.commit()

        # SQL-запит для отримання топ-5 студентів за середнім балом
        query = """
        SELECT students.id, students.name, ROUND(AVG(grades.grade), 2) AS average_grade
        FROM students
        JOIN grades ON students.id = grades.student_id
        GROUP BY students.id, students.name
        ORDER BY average_grade DESC
        LIMIT 5;
        """
        cursor.execute(query)
        students = cursor.fetchall()
        print("Top 5 Students by Average Grade:")
        for student in students:
            print(f"ID: {student[0]}, Fullname: {student[1]}, Average Grade: {student[2]:.2f}")

        # Знайти студента із найвищим середнім балом з певного предмета
        subject_id = 1  # Замініть на конкретний ідентифікатор предмета
        query = """
        SELECT s.name AS student_name, ROUND(AVG(g.grade), 2) AS average_grade
        FROM students s
        JOIN grades g ON s.id = g.student_id
        WHERE g.subject_id = %s
        GROUP BY s.id, s.name
        ORDER BY average_grade DESC
        LIMIT 1;
        """
        cursor.execute(query, (subject_id,))
        student = cursor.fetchone()

        if student:
            print(f"Student with highest average grade in subject {subject_id}:")
            print(f"Student Name: {student[0]}")
            print(f"Average Grade: {student[1]:.2f}")
        else:
            print(f"No students found for subject {subject_id}")

        # Середній бал у групах з певного предмета
        subject_id = 2  # Замініть на конкретний ідентифікатор предмета
        query = """
        SELECT g.name AS group_name, ROUND(AVG(gr.grade), 2) AS average_grade
        FROM groups g
        JOIN students s ON g.id = s.group_id
        JOIN grades gr ON s.id = gr.student_id
        WHERE gr.subject_id = %s
        GROUP BY g.id, g.name
        ORDER BY group_name;
        """
        cursor.execute(query, (subject_id,))
        groups = cursor.fetchall()
        print(f"Average grade in groups for subject {subject_id}:")
        for group in groups:
            print(f"Group: {group[0]}, Average Grade: {group[1]:.2f}")

        # Середній бал на потоці
        query = """
        SELECT ROUND(AVG(grade), 2) AS average_grade
        FROM grades;
        """
        cursor.execute(query)
        average_grade = cursor.fetchone()
        print(f"Overall average grade: {average_grade[0]:.2f}")

        # Які курси читає певний викладач
        teacher_id = 1  # Замініть на конкретний ідентифікатор викладача
        query = """
        SELECT s.name AS subject_name
        FROM subjects s
        WHERE s.teacher_id = %s;
        """
        cursor.execute(query, (teacher_id,))
        subjects = cursor.fetchall()
        print(f"Subjects taught by teacher {teacher_id}:")
        for subject in subjects:
            print(f"Subject: {subject[0]}")

        # Список студентів у певній групі
        group_id = 2  # Замініть на конкретний ідентифікатор групи
        query = """
        SELECT s.name AS student_name
        FROM students s
        WHERE s.group_id = %s;
        """
        cursor.execute(query, (group_id,))
        students = cursor.fetchall()
        print(f"Students in group {group_id}:")
        for student in students:
            print(f"Student: {student[0]}")

        # Оцінки студентів у окремій групі з певного предмета
        group_id = 2  # Замініть на конкретний ідентифікатор групи
        subject_id = 2  # Замініть на конкретний ідентифікатор предмета
        query = """
        SELECT s.name AS student_name, g.grade, g.grade_date
        FROM students s
        JOIN grades g ON s.id = g.student_id
        WHERE s.group_id = %s AND g.subject_id = %s;
        """
        cursor.execute(query, (group_id, subject_id))
        grades = cursor.fetchall()
        print(f"Grades of students in group {group_id} for subject {subject_id}:")
        for grade in grades:
            print(f"Student: {grade[0]}, Grade: {grade[1]}, Date: {grade[2]}")

        # Середній бал, який ставить певний викладач зі своїх предметів
        teacher_id = 2  # Замініть на конкретний ідентифікатор викладача
        query = """
        SELECT t.name AS teacher_name, ROUND(AVG(g.grade), 2) AS average_grade
        FROM teachers t
        JOIN subjects s ON t.id = s.teacher_id
        JOIN grades g ON s.id = g.subject_id
        WHERE t.id = %s
        GROUP BY t.id, t.name;
        """
        cursor.execute(query, (teacher_id,))
        average_grade = cursor.fetchone()
        print(f"Average grade given by teacher {teacher_id}: {average_grade[1]:.2f}")

        # Які курси проходить студент
        student_id = 35  # Замініть на конкретний ідентифікатор студента
        query = """
        SELECT sub.name AS subject_name
        FROM subjects sub
        JOIN grades gr ON sub.id = gr.subject_id
        WHERE gr.student_id = %s;
        """
        cursor.execute(query, (student_id,))
        subjects = cursor.fetchall()
        print(f"Subjects taken by student {student_id}:")
        for subject in subjects:
            print(f"Subject: {subject[0]}")

        # Які курси проходить студент у конкретного викладача
        student_id = 35  # Замініть на конкретний ідентифікатор студента
        teacher_id = 1  # Замініть на конкретний ідентифікатор викладача
        query = """
        SELECT sub.name AS subject_name
        FROM subjects sub
        JOIN grades gr ON sub.id = gr.subject_id
        WHERE gr.student_id = %s AND sub.teacher_id = %s;
        """
        cursor.execute(query, (student_id, teacher_id))
        subjects = cursor.fetchall()
        print(f"Subjects taken by student {student_id} with teacher {teacher_id}:")
        for subject in subjects:
            print(f"Subject: {subject[0]}")

        # Середній бал, який ставить певний викладач певному студенту
        teacher_id = 3  # Замініть на конкретний ідентифікатор викладача
        student_id = 35  # Замініть на конкретний ідентифікатор студента
        query = """
        SELECT t.name AS teacher_name,
               s.name AS student_name,
               ROUND(AVG(g.grade), 2) AS average_grade
        FROM teachers t
        JOIN subjects subj ON t.id = subj.teacher_id
        JOIN grades g ON subj.id = g.subject_id
        JOIN students s ON g.student_id = s.id
        WHERE t.id = %s
          AND s.id = %s
        GROUP BY t.name, s.name;
        """
        cursor.execute(query, (teacher_id, student_id))
        average_grade = cursor.fetchone()
        print(f"Average grade given by teacher {teacher_id} to student {student_id}: {average_grade[2]:.2f}")

        # Останні оцінки студентів у групі з предмета
        group_id = 3  # Замініть на конкретний ідентифікатор групи
        subject_id = 1  # Замініть на конкретний ідентифікатор предмета
        query = """
        SELECT s.name AS student_name,
               g.grade,
               g.grade_date
        FROM students s
        JOIN grades g ON s.id = g.student_id
        JOIN groups grp ON s.group_id = grp.id
        WHERE grp.id = %s
          AND g.subject_id = %s
          AND g.grade_date = (
              SELECT MAX(g2.grade_date)
              FROM grades g2
              WHERE g2.student_id = g.student_id
                AND g2.subject_id = g.subject_id
          )
        ORDER BY s.name;
        """
        cursor.execute(query, (group_id, subject_id))
        grades = cursor.fetchall()
        print(f"Latest grades of students in group {group_id} for subject {subject_id}:")
        for grade in grades:
            print(f"Student: {grade[0]}, Grade: {grade[1]}, Date: {grade[2]}")

    except psycopg2.Error as e:
        print("Database error:", e)
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()

