def verification(variables):
    [workers_salary_variance] = variables
    results = []
    if workers_salary_variance > 5:
        results.append(True)
    else:
        results.append(False)
    return results