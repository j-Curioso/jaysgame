from util import roll
from player import Player
import config

class Tile:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.revealed = False
    self.start_tile = False
    self.boss_tile = False
    self.enemies = {}
    self.players = {}
    self.passages = {
      0: False,
      1: False,
      2: False,
      3: False
    }
    for direction in range(len(self.passages)):
      self.passages[direction] = roll() > config.open_passage_chance

  def make_boss_tile(self):
    # Boss rooms have only one door
    # Reveal logic takes care of aligning doors
    self.boss_tile = True
    self.close_all_passages()
    self.passages[0] = True

  def make_start_tile(self):
    self.start_tile = True
    self.close_all_passages()
    direction = int(roll() / 4)
    self.passages[direction] = True

  def close_all_passages(self):
    for direction in range(len(self.passages)):
      self.passages[direction] = False

  @staticmethod
  def cardinal_to_int_direction(cardinal_direction):
    if cardinal_direction == "north":
      return 0
    elif cardinal_direction == "east":
      return 1
    elif cardinal_direction == "south":
      return 2
    elif cardinal_direction == "west":
      return 3

  @staticmethod
  def int_to_cardinal_direction(int_direction):
    if int_direction == 0:
      return "north"
    elif int_direction == 1:
      return "east"
    elif int_direction == 2:
      return "south"
    elif int_direction == 3:
      return "west"

  @staticmethod
  def get_opposing_direction(direction):
    if direction == "north":
      return "south"
    elif direction == "south":
      return "north"
    elif direction == "west":
      return "east"
    elif direction == "east":
      return "west"

  def rotate_tile(self, rotation_direction=config.tile_rotation_direction):
    # rotation_direction should be
    # -1 = counter-clockwise
    #  1 = clockwise
    temp_passages = self.passages.copy()
    self.passages.clear()
    for cardinal_direction, open in temp_passages.items():
      new_direction = (cardinal_direction + rotation_direction) % 4
      self.passages[new_direction] = open

  def add_entity(self, entity):
    if isinstance(entity, Player):
      self.players[entity.id] = entity
    else:
      self.enemies[entity.id] = entity

  def remove_entity(self, entity):
    if isinstance(entity, Player):
      del self.players[entity.id]
    else:
      del self.enemies[entity.id]

  def get_description(self):
    # returns a string with open doors and any entities
    desc = ""
    open_doors = self.get_open_doors()
    if len(open_doors) == 1:
      desc += f"This is a dead end. There is one door to the {open_doors[0]}.\n"
    else:
      desc += f"There are doors to the {str(open_doors)}.\n"

    enemy_names = self.get_enemy_names()
    if len(enemy_names) > 0:
      desc += enemy_names + " lie in wait."
    else:
      desc += "This room is empty."

    return desc

  def get_enemy_by_name(self, name):
    for id, enemy in self.enemies.items():
      if enemy.name.lower() == name.lower():
        return enemy

  def get_enemy_names(self):
    names = ""
    for i, enemy in enumerate(self.enemies.values()):
      names += enemy.name
      if (i < len(self.enemies)-1):
        names += ", "
    return names
  
  def get_open_doors(self):
    # Check open doors
    open_directions = []
    for int_direction, open in self.passages.items():
      if open:
        open_directions.append(Tile.int_to_cardinal_direction(int_direction))
    return open_directions

  def is_clear(self):
    return len(self.enemies) == 0

  def is_passage_open(self, direction):
    if not isinstance(direction, int):
      direction = Tile.cardinal_to_int_direction(direction)
    return self.passages[direction]