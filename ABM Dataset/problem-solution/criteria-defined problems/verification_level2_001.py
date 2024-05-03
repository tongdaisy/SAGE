def verification(variables):
    total_num_students = variables[0]
    results = []
    if total_num_students >= 80 and total_num_students <= 120:
        results.append(True)
    else:
        results.append(False)
    return results