from entity import Entity
from skill import Skill
from util import *

class Boss(Entity):
  def __init__(self, boss_name, attack, damage, defense, health, boss_summon):
    self.damage = damage
    self.skills = {}
    self.skills["attack"] = Skill("attack", "attack", attack)
    self.skills["defense"] = Skill("defense", "defense", defense)

    self.boss_summon = boss_summon
    super().__init__(boss_name, health)

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

  def do_boss_summon(self, game):
    if self.boss_summon == "do_hiveling_queen_boss_summon":
      self.do_hiveling_queen_boss_summon(game)

  def do_hiveling_queen_boss_summon(self, game):
    # When Hiveling Queen is revealed, it summons all remaining Hiveling from deck.
    queen_location = self.location
    hiveling_ids = []

    for card in game.monster_deck.cards:
      if isinstance(card, Monster) and card.monster_name == "Hiveling":
        hiveling_ids.append(card.id)

    for id in hiveling_ids:
      hiveling = game.monster_deck.draw_specific_card(id)
      queen_location.enemies[hiveling.id] = hiveling
      hiveling.location = queen_location
      game.add_entity(hiveling)

    print("As the Hiveling Queen appears, her voracious cry summons all the hivelings from the deck.")
    print(str(len(hiveling_ids)) + " hivelings appear to guard their queen.")