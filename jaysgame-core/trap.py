from entity import Entity
from util import *

class Trap(Entity):
  def __init__(self, trap_name, life, trap, damage):
    self.trap = trap
    self.damage = damage
    super().__init__(trap_name, life)