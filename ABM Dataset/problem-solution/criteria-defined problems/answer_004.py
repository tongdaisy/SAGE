import random
import numpy as np
class Student:
    def __init__(self, id, grade, is_attending=True, satisfaction=0):
        self.id = id
        self.grade = grade
        self.is_attending = is_attending
        self.satisfaction = satisfaction

    def change_grade(self, new_grade):
        self.grade = new_grade

    def change_attendance(self, is_attending):
        self.is_attending = is_attending

    def update_satisfaction(self):
        self.satisfaction = random.randint(0, 3)


class Teacher:
    def __init__(self, id, performance_rating=1, student_satisfaction=1, attendance_rate=1):
        self.id = id
        self.performance_rating = performance_rating
        self.student_satisfaction = student_satisfaction
        self.attendance_rate = attendance_rate
        self.salary=10

    def give_lecture(self, subject):
        print(f"Teacher {self.id} is giving a lecture on {subject}")

    def evaluate_performance(self, students):
        total_satisfaction = sum(student.satisfaction for student in students)
        self.student_satisfaction = total_satisfaction / len(students)

        total_attendance = sum(student.is_attending for student in students)
        self.attendance_rate = total_attendance / len(students)


class School:
    def __init__(self, num_students, num_teachers, graduate_grade):
        self.students = [Student(id, random.randint(1, graduate_grade)) for id in range(num_students)]
        self.teachers = [Teacher(id) for id in range(num_teachers)]
        self.graduate_grade = graduate_grade
        self.student_teacher_ratio = self.cal_stu_teacher_ratio()

    def enroll_student(self, student):
        self.students.append(student)

    def hire_teacher(self):
        if self.student_teacher_ratio > 10:
            more_teacher = [Teacher(id + len(self.teachers)) for id in
                            range(int(self.student_teacher_ratio) + 1 - 10)]
            self.teachers += more_teacher

    def promote_teachers(self, num_teachers_promoted):
        sorted_teachers = sorted(self.teachers, key=lambda teacher: teacher.student_satisfaction*teacher.attendance_rate, reverse=True)
        promoted_teachers = sorted_teachers[:num_teachers_promoted]
        for teacher in promoted_teachers:
            teacher.salary *=1.1

    def fire_teachers(self, num_teachers_fired):
        sorted_teachers = sorted(self.teachers, key=lambda teacher: teacher.student_satisfaction*teacher.attendance_rate)
        fired_teachers = sorted_teachers[:num_teachers_fired]
        for teacher in fired_teachers:
            self.teachers.remove(teacher)

    def graduate(self):
        update_students = self.students.copy()
        for s in self.students:
            if s.grade > self.graduate_grade:
                update_students.remove(s)
        self.students = update_students

    def cal_stu_teacher_ratio(self):
        return len(self.students) / len(self.teachers)


class Lecture:
    def __init__(self, school, subject,teacher, students):
        self.school = school
        self.subject = subject
        self.teacher=teacher
        self.students=students

    def start(self):
        for student in self.students:
            is_attending = random.choice([True, False])
            student.change_attendance(is_attending)
            if is_attending:
                student.change_grade(student.grade + 1)
            student.update_satisfaction()

    def end(self):
        for student in self.students:
            student.update_satisfaction()
        self.teacher.evaluate_performance(self.students)
        print("Lecture has ended.")


def simulation(num_students, num_teachers, subject, graduate_grade):
    school = School(num_students, num_teachers, graduate_grade)
    for i in range(10):
        random.shuffle(school.teachers)
        for j,t in enumerate(school.teachers):
            stus=school.students[int(j*school.student_teacher_ratio):int((j+1)*school.student_teacher_ratio)]
            if len(stus)==0:
                break
            lecture = Lecture(school, subject,t,stus)
            lecture.start()
            lecture.end()
        school.graduate()
        num_new_student = random.randint(10, 20)
        new_students = [Student(id, 1) for id in
                        range(len(school.students), len(school.students) + num_new_student)]
        for s in new_students:
            school.enroll_student(s)
        school.promote_teachers(1)
        school.fire_teachers(1)
        school.student_teacher_ratio = school.cal_stu_teacher_ratio()
        school.hire_teacher()
        for teacher in school.teachers:
            teacher.evaluate_performance(school.students)
    teacher_salary_variance = np.var([t.salary for t in school.teachers])
    return teacher_salary_variance

teacher_salary_variance = simulation(num_students=100, num_teachers=10, subject="Math", graduate_grade=6)
print(teacher_salary_variance)