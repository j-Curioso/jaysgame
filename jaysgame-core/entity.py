import uuid

class Entity: # players, monsters, bosses, 
  def __init__(self, name, health):
    self.id = str(uuid.uuid4())
    self.name = name
    self.max_health = self.health = health
    self.alive = True
    self.location = None # A Tile
    self.previous_location = None # A Tile

  def apply_damage(self, dmg):
    self.health -= dmg
    if(self.health <= 0):
      self.alive = False

  def get_health_string(self):
    return str(self.health) + "/" + str(self.max_health)