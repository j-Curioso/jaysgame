from entity import Entity
from util import *

class Trap(Entity):
  def __init__(self, trap_name, life, trap, damage):
    self.trap = trap
    self.damage = damage
    super().__init__(trap_name, life)

  def get_stat_card(self):
    max_len = 7
    name_len = len(self.name) + 1
    msg = ""
    msg += self.name.ljust(name_len, " ")
    msg += "| "
    msg += str("trap").ljust(max_len, " ")
    msg += str("dmg").ljust(max_len, " ")
    msg += "\n"
    msg += "".ljust(name_len, " ")
    msg += "| "
    msg += str(self.trap).ljust(max_len, " ")
    msg += str(self.damage).ljust(max_len, " ")
    return msg