# school life

import random


class Student:
    def __init__(self, id, grade, is_attending=True):
        self.id = id
        self.grade = grade
        self.is_attending = is_attending
        self.learning_enthusiasm = 1
        self.experience_points = 0
        self.test_score = 60

    def change_grade(self, new_grade):
        self.grade = new_grade
        self.learning_enthusiasm *= 0.9

    def change_attendance(self, is_attending):
        self.is_attending = is_attending

    def earn_experience_points(self, points):
        self.experience_points += points

    def improvement_be_rewarded(self):
        self.learning_enthusiasm *= 1.1



class Teacher:
    def __init__(self, id):
        self.id = id

    def give_lecture(self, subject):
        print(f"Teacher {self.id} is giving a lecture on {subject}")

    def assign_group_work(self, students):
        # specific code on how to assign_group_work
        group_size = 4
        num_groups = int(len(students) / group_size)
        groups = []
        for i in range(num_groups):
            group = students[i*group_size:(i+1)*group_size]
            groups.append(group)
        if len(students) % group_size != 0:
            groups.append(students[num_groups*group_size:])
        return groups


class School:
    def __init__(self, num_students, num_teachers, graduate_grade):
        self.students = [Student(id, random.randint(1, 12)) for id in range(num_students)]
        self.teachers = [Teacher(id) for id in range(num_teachers)]
        self.graduate_grade = graduate_grade

    def enroll_student(self, student):
        self.students.append(student)

    def hire_teacher(self, teacher):
        self.teachers.append(teacher)

    def graduate(self):
        update_students = self.students.copy()
        for s in self.students:
            if s.grade > self.graduate_grade:
                update_students.remove(s)
        self.students = update_students
    
    def assign_group_work(self, students):
        for teacher in self.teachers:
            groups=teacher.assign_group_work(students)
            best_perfomance_group=random.randint(0,len(groups)-1)
            for s in groups[best_perfomance_group]:
                s.improvement_be_rewarded()



class Lecture:
    def __init__(self, school, subject):
        self.school = school
        self.subject = subject

    def start(self):
        for teacher in self.school.teachers:
            teacher.give_lecture(self.subject)

    def test(self):
        for student in self.school.students:
            score = random.randint(student.test_score - 10, student.test_score + 10) + student.experience_points
            if score > student.test_score:
                student.improvement_be_rewarded()
            student.test_score = score

    def end(self):
        print("Lecture has ended.")


def simulation(num_students, num_teachers, subject, graduate_grade):
    school = School(num_students, num_teachers, graduate_grade)
    lecture = Lecture(school, subject)
    for student in school.students:
        new_grade = random.randint(1, graduate_grade)
        student.change_grade(new_grade)
    for i in range(10):
        lecture.start()
        for student in school.students:
            student.change_grade(student.grade + 1)
            is_attending = random.choice([True, False])
            student.change_attendance(is_attending)
            if is_attending:
                student.earn_experience_points(5)
        students_attending = [student for student in school.students if student.is_attending]
        school.assign_group_work(students_attending)
        lecture.test()
        lecture.end()
        school.graduate()
        num_new_student = random.randint(10, 20)
        new_students = [Student(id, 1) for id in
                        range(len(school.students), len(school.students) + num_new_student)]
        for s in new_students:
            school.enroll_student(s)


    enthusiasm = sum(s.learning_enthusiasm for s in school.students) / len(school.students)

    return enthusiasm


enthusiasm = simulation(num_students=100, num_teachers=10, subject="Math", graduate_grade=6)