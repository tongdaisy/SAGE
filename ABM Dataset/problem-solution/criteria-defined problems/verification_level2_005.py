def verification(variables):
    [final_infect] = variables
    results = []
    if final_infect == 0:
        results.append(True)
    else:
        results.append(False)
    return results