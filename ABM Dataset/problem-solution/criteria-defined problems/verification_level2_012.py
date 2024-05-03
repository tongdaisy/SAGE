def verification(variables):
    [num_accidents, num_change_directions] = variables
    results = []
    if num_accidents == 0:
        results.append(True)
    else:
        results.append(False)
    if num_change_directions > 0:
        results.append(True)
    else:
        results.append(False)
    return results