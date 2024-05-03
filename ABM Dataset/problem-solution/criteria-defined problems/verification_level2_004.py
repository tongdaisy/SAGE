def verification(variables):
    [teacher_salary_variance] = variables
    results = []
    if teacher_salary_variance > 0:
        results.append(True)
    else:
        results.append(False)
    return results