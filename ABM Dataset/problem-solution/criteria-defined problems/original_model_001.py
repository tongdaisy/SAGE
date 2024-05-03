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
    def __init__(self, num_students, num_teachers):
        self.students = [Student(id, random.randint(1, 12)) for id in range(num_students)]
        self.teachers = [Teacher(id) for id in range(num_teachers)]
        self.total_num_students=len(self.students)

    def enroll_student(self, student):
        self.students.append(student)
        self.total_num_students=len(self.students)

    def hire_teacher(self, teacher):
        self.teachers.append(teacher)


class Lecture:
    def __init__(self, school, subject):
        self.school = school
        self.subject = subject

    def start(self):
        for teacher in self.school.teachers:
            teacher.give_lecture(self.subject)

    def end(self):
        print("Lecture has ended.")


def simulation(num_students, num_teachers, subject):
    school = School(num_students, num_teachers)
    lecture = Lecture(school, subject)
    for student in school.students:
        new_grade = random.randint(1, 6)
        student.change_grade(new_grade)
    for i in range(10):
        lecture.start()
        for student in school.students:
            is_attending = random.choice([True, False])
            student.change_attendance(is_attending)
            if is_attending:
                student.change_grade(student.grade + 1)
        lecture.end()
        num_new_student = random.randint(10, 20)
        new_students = [Student(id, 1) for id in
                        range(len(school.students), len(school.students) + num_new_student)]
        for s in new_students:
            school.enroll_student(s)
    return school.total_num_students

total_num_students=simulation(num_students=100, num_teachers=10, subject="Math")