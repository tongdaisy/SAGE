# school life

import random

class Student:
    def __init__(self, id, grade, is_attending=True):
        self.id = id
        self.grade = grade
        self.is_attending = is_attending

    def change_grade(self, new_grade):
        self.grade = new_grade

    def change_attendance(self, is_attending):
        self.is_attending = is_attending


class Teacher:
    def __init__(self, id):
        self.id = id

    def give_lecture(self, subject):
        print(f"Teacher {self.id} is giving a lecture on {subject}")


class School:
    def __init__(self, num_students, num_teachers, graduate_grade):
        self.students = [Student(id, random.randint(1, graduate_grade)) for id in range(num_students)]
        self.teachers = [Teacher(id) for id in range(num_teachers)]
        self.graduate_grade = graduate_grade
        self.student_teacher_ratio = self.cal_stu_teacher_ratio()

    def enroll_student(self, student):
        self.students.append(student)

    def hire_teacher(self):
        more_teacher=[]
        if self.student_teacher_ratio>10:
            more_teacher=[Teacher(id+len(self.teachers)) for id in range(int(self.student_teacher_ratio)+1-10)]
        self.teachers+=more_teacher

    def graduate(self):
        update_students = self.students.copy()
        for s in self.students:
            if s.grade > self.graduate_grade:
                update_students.remove(s)
        self.students = update_students

    def cal_stu_teacher_ratio(self):
        return len(self.students) / len(self.teachers)


class Lecture:
    def __init__(self, school, subject):
        self.school = school
        self.subject = subject

    def start(self):
        for teacher in self.school.teachers:
            teacher.give_lecture(self.subject)

    def end(self):
        print("Lecture has ended.")


def simulation(num_students, num_teachers, subject, graduate_grade):
    school = School(num_students, num_teachers, graduate_grade)
    lecture = Lecture(school, subject)
    student_teacher_ratio_record=[school.student_teacher_ratio]
    for i in range(10):
        lecture.start()
        for student in school.students:
            is_attending = random.choice([True, False])
            student.change_attendance(is_attending)
            if is_attending:
                student.change_grade(student.grade + 1)
        lecture.end()
        school.graduate()
        num_new_student = random.randint(10, 20)
        new_students = [Student(id, 1) for id in
                        range(len(school.students), len(school.students) + num_new_student)]
        for s in new_students:
            school.enroll_student(s)
        school.student_teacher_ratio = school.cal_stu_teacher_ratio()
        student_teacher_ratio_record.append(school.student_teacher_ratio)
        school.hire_teacher()
        
    return student_teacher_ratio_record

student_teacher_ratio_record=simulation(num_students=100, num_teachers=10, subject="Math", graduate_grade=6)
print(student_teacher_ratio_record)