

class Skill():
  def __init__(self, name, category, value=0):
    self.name = name
    self.value = value
    self.category = category # attack, defense, utility

  def increase(self, value):
    self.value += value

  def decrease(self, value):
    self.value -= value