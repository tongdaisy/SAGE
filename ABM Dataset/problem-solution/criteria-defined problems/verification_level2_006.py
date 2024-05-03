def verification(variables):
    [treatment_rate] = variables
    results = []
    if treatment_rate > 0.25:
        results.append(True)
    else:
        results.append(False)
    return results