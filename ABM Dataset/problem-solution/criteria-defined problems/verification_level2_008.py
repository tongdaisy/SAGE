def verification(variables):
    [GDP_decrease_ratio, NDI_decrease_ratio] = variables
    results=[]
    if GDP_decrease_ratio < 0.1:
        results.append(True)
    else:
        results.append(False)
    if NDI_decrease_ratio < 0.1:
        results.append(True)
    else:
        results.append(False)
    return results