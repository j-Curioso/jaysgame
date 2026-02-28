from entity import Entity
from skill import Skill

class Monster(Entity):
  def __init__(self, specific_name, monster_name, attack, damage, defense, health):
    self.monster_name = monster_name
    self.damage = damage
    self.skills = {}
    self.skills["attack"] = Skill("attack", "attack", attack)
    self.skills["defense"] = Skill("defense", "defense", defense)
    super().__init__(specific_name, health)

  def get_stat_card(self):
    max_len = 7
    name_len = len(self.name) + 1
    msg = ""
    msg += self.name.ljust(name_len, " ")
    msg += "| "
    msg += str("hp").ljust(max_len, " ")
    msg += str("dmg").ljust(max_len, " ")
    msg += str("atk").ljust(max_len, " ")
    msg += str("def").ljust(max_len, " ")
    msg += "\n"
    msg += "".ljust(name_len, " ")
    msg += "| "
    msg += str(str(self.health) + "/" + str(self.max_health)).ljust(max_len, " ")
    msg += str(self.damage).ljust(max_len, " ")
    msg += str(self.skills["attack"].value).ljust(max_len, " ")
    msg += str(self.skills["defense"].value).ljust(max_len, " ")
    return msg