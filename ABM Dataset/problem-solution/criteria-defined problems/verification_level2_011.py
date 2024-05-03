def verification(variables):
    [num_accidents] = variables
    results = []
    if num_accidents == 0:
        results.append(True)
    else:
        results.append(False)
    return results