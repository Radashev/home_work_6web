-- 02_query_top_5_students.sql

SELECT students.id, students.name, ROUND(AVG(grades.grade), 2) AS average_grade
FROM students
JOIN grades ON students.id = grades.student_id
GROUP BY students.id, students.name
ORDER BY average_grade DESC
LIMIT 5;

-- 03_query_highest_avg_subject.sql

SELECT s.name AS student_name, ROUND(AVG(g.grade), 2) AS average_grade
FROM students s
JOIN grades g ON s.id = g.student_id
WHERE g.subject_id = 1  -- Замініть на конкретний ідентифікатор предмета
GROUP BY s.id, s.name
ORDER BY average_grade DESC
LIMIT 1;

-- 04_query_avg_grade_by_group_subject.sql

SELECT g.name AS group_name, 
       ROUND(AVG(gr.grade), 2) AS average_grade
FROM groups g
JOIN students s ON g.id = s.group_id
JOIN grades gr ON s.id = gr.student_id
WHERE gr.subject_id = 2  -- Замініть на конкретний ідентифікатор предмета
GROUP BY g.id, g.name
ORDER BY group_name;

-- 05_query_avg_grade_overall.sql

SELECT ROUND(AVG(grade), 2) AS average_grade
FROM grades;

-- 06_query_courses_by_teacher.sql

SELECT s.name AS subject_name
FROM subjects s
WHERE s.teacher_id = 1;  -- Замініть на конкретний ідентифікатор викладача

-- 07_query_students_in_group.sql

SELECT s.name AS student_name
FROM students s
WHERE s.group_id = 2;  -- Замініть на конкретний ідентифікатор групи

-- 08_query_grades_in_group_subject.sql

SELECT s.name AS student_name, g.grade, g.grade_date
FROM students s
JOIN grades g ON s.id = g.student_id
WHERE s.group_id = 2 AND g.subject_id = 2;  -- Замініть на конкретні ідентифікатори групи та предмета

-- 09_query_avg_grade_by_teacher.sql

SELECT t.name AS teacher_name, ROUND(AVG(g.grade), 2) AS average_grade
FROM teachers t
JOIN subjects s ON t.id = s.teacher_id
JOIN grades g ON s.id = g.subject_id
WHERE t.id = 2  -- Замініть на конкретний ідентифікатор викладача
GROUP BY t.id, t.name;

-- 10_query_courses_by_student.sql

SELECT sub.name AS subject_name
FROM subjects sub
JOIN grades gr ON sub.id = gr.subject_id
WHERE gr.student_id = 35;  -- Замініть на конкретний ідентифікатор студента

-- 11_query_courses_student_teacher.sql

SELECT sub.name AS subject_name
FROM subjects sub
JOIN grades gr ON sub.id = gr.subject_id
WHERE gr.student_id = 35 AND sub.teacher_id = 1;  -- Замініть на конкретні ідентифікатори студента і викладача

-- 10_query_avg_grade_teacher_student.sql

SELECT t.name AS teacher_name,
       s.name AS student_name,
       ROUND(AVG(g.grade), 2) AS average_grade
FROM teachers t
JOIN subjects subj ON t.id = subj.teacher_id
JOIN grades g ON subj.id = g.subject_id
JOIN students s ON g.student_id = s.id
WHERE t.id = 3  -- Замініть на конкретний ідентифікатор викладача
  AND s.id = 35  -- Замініть на конкретний ідентифікатор студента
GROUP BY t.name, s.name;

-- 11_query_latest_grades_group_subject.sql

SELECT s.name AS student_name,
       g.grade,
       g.grade_date
FROM students s
JOIN grades g ON s.id = g.student_id
JOIN groups grp ON s.group_id = grp.id
WHERE grp.id = 3  -- Замініть на конкретний ідентифікатор групи
  AND g.subject_id = 1  -- Замініть на конкретний ідентифікатор предмета
  AND g.grade_date = (
      SELECT MAX(g2.grade_date)
      FROM grades g2
      WHERE g2.student_id = g.student_id
        AND g2.subject_id = g.subject_id
  )
ORDER BY s.name;
