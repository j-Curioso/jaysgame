from entity import Entity
from skill import Skill
from util import *
import config

class Player(Entity):
  def __init__(self, player_name):
    self.max_skill_level = config.player_max_skill_level
    self.max_level = config.player_max_level
    self.level = config.player_start_level
    self.damage = config.player_start_damage
    self.max_block_tries = self.block_tries = config.player_start_block_tries
    self.critical_hit_roll = config.player_start_critical
    self.skill_points = config.player_start_skill_points
    self.skills = {}
    self._init_skills()
    self.helmet = None
    self.chest = None
    self.left_hand = None
    self.right_hand = None
    self.boots = None
    self.inventory = {} # id is name of item, key is item
    self.max_actions = self.actions = 2
    super().__init__(player_name, config.player_start_life)

  def _init_skills(self):
    self.skills["melee"]   = Skill("melee", "attack")
    self.skills["ranged"]  = Skill("ranged", "attack")
    self.skills["defense"] = Skill("defense", "defense")
    self.skills["block"]   = Skill("block", "defense")
    self.skills["trap"]    = Skill("trap", "utility")

  def equip_item(self, item):
    return

  def level_up(self):
    if self.level < self.max_level:
      self.level += 1
      self.skill_points += 2
      prompt(f"{self.name} is now level {self.level}.")
    else:
      prompt(self.name + " is at max level.")

  def apply_skill(self, skill, value=1):
    curr_val = self.skills[skill].value
    if curr_val + value <= self.max_skill_level:
      self.skills[skill].increase(value)
      self.skill_points -= value

  def get_attack_skills(self):
    attack_skills = []
    for skill in self.skills.values():
      if skill.category == "attack":
        attack_skills.append(skill)
    return attack_skills

  def get_skill_value(self, skill):
    return self.skills[skill].value

  def get_levelable_skills(self):
    levelable_skills = []
    for skill_name, skill in self.skills.items():
      if skill.value < self.max_skill_level:
        levelable_skills.append(skill_name)
    return levelable_skills

  def get_skill_list(self):
    skill_list = f"available: {self.skill_points}  |  "
    for skill_name, skill in self.skills.items():
      skill_list += f"{skill_name}: {skill.value}  "
    return skill_list

  def get_stat_card(self):
    max_len = 9
    name_len = len(self.name) + 1
    msg = ""
    msg += self.name.ljust(name_len, " ")
    msg += "| "
    msg += str("act").ljust(max_len, " ")
    msg += str("loc").ljust(max_len, " ")
    msg += str("sp").ljust(max_len, " ")
    msg += str("lvl").ljust(max_len, " ")
    msg += str("hp").ljust(max_len, " ")
    msg += str("dmg").ljust(max_len, " ")
    for skill_name in self.skills.keys():
      msg += skill_name.ljust(max_len, " ")
    msg += "\n"
    msg += "".ljust(name_len, " ")
    msg += "| "
    msg += str(self.actions).ljust(max_len, " ")
    msg += str(str(self.location.x) + "," + str(self.location.y)).ljust(max_len, " ")
    msg += str(self.skill_points).ljust(max_len, " ")
    msg += str(self.level).ljust(max_len, " ")
    msg += str(str(self.health) + "/" + str(self.max_health)).ljust(max_len, " ")
    msg += str(self.damage).ljust(max_len, " ")
    for skill in self.skills.values():
      msg += str(skill.value).ljust(max_len, " ")
    return msg

  def round_reset(self):
    self.actions = self.max_actions
    self.block_tries = self.max_block_tries