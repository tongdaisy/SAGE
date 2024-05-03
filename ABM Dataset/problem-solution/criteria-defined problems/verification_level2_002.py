def verification(variables):
  [enthusiasm] = variables
  results = []
  
  if enthusiasm > 1.0:
    results.append(True)
  else:  
    results.append(False)

  return results