def verification(variables):
    unemployed_rate = variables[0]
    results = []
    if unemployed_rate < 0.2:
        results.append(True)
    else:
        results.append(False)
    return results