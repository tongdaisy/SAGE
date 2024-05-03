def verification(variables):
    [max_spread_rate] = variables
    results = []
    if max_spread_rate < 0.1:
        results.append(True)
    else:
        results.append(False)
    return results