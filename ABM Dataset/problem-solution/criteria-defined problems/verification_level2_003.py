def verification(variables):
    results = []
    [student_teacher_ratio_record] = variables
    results.append(True)
    for ratio in student_teacher_ratio_record:
        if ratio < 8 or ratio > 12:
            results[-1] =False
            break
    return results