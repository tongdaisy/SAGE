# sugerspace
#mesa

import mesa
import numpy as np

class Sugar(mesa.Agent):
  """
  Sugar
  - contains an amount of sugar
  - grows one amount of sugar at each turn
  """
  def __init__(self):
    print("I am sugar")

class Spice(mesa.Agent):
  """
  Spice
  - contains an amount of spice
  - grows one amount of spice at each turn
  """
  def __init__(self):
    print("I am spice")


class Trader(mesa.Agent):
  """
  Trader:
  - has a metabolism of sugar and spice
  - harvest and trade sugar and spice to survive
  """

  def __init__(self):
    print("I am Trader")


class SugarscapeG1mt(mesa.Model):
  """
  Manager class to run Sugarscape with Traders
  """
  def __init__(self, width=50,height=50):

    #Initiate width and heigh of sugarscape
    self.width = width
    self.height = height

    #initiate mesa grid class
    self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)

    #read in landscape file from supplmentary material
    sugar_distribution =np.genfromtxt("sugar-map.txt")
    spice_distribution = np.flip(sugar_distribution, 1)


#model = SugarscapeG1mt()