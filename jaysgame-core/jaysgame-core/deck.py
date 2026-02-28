from monster import Monster
from boss import Boss
from trap import Trap
import config
import json
import random

class Deck:
  def __init__(self, deck_type, is_graveyard=False):
    self.cards = []
    self.deck_type = deck_type # 0=monster, 1=boss, 2=item
    if not is_graveyard:
      if self.deck_type == 0:
        self.load_monsters_from_file(config.monster_cards_file)
        self.load_traps_from_file(config.trap_cards_file)
      elif self.deck_type == 1:
        self.load_bosses_from_file(config.boss_cards_file)

  def load_monsters_from_file(self, deck_file):
    cards_file = open(deck_file, 'r')
    cards_json = json.loads(cards_file.read())
    for card in cards_json:
      for x in range(card['count']):
        monster = Monster(card['name'] + " " + str(x), 
                          card['name'], 
                          card['attack'], 
                          card['damage'], 
                          card['defense'],
                          card['health'])
        self.cards.append(monster)

  def load_traps_from_file(self, deck_file):
    cards_file = open(deck_file, 'r')
    cards_json = json.loads(cards_file.read())
    for card in cards_json:
      for x in range(card['count']):
        trap = Trap(card['name'],
                    card['life'],
                    card['trap'],
                    card['damage'])
        self.cards.append(trap)

  def load_bosses_from_file(self, deck_file):
    cards_file = open(deck_file, 'r')
    cards_json = json.loads(cards_file.read())
    for card in cards_json:
      boss = Boss(card["name"],
                  card["attack"],
                  card["damage"],
                  card["defense"],
                  card["health"],
                  card["boss_summon"])
      self.cards.append(boss)

  def shuffle(self, count=69):
    for n in range(count):
      temp = self.cards.copy()
      self.cards = []
      while(len(temp) > 0):
        idx = random.randint(0, len(temp)-1)
        self.cards.append(temp.pop(idx))

  def draw_card(self):
    return self.cards.pop() if len(self.cards) > 0 else None

  def draw_specific_card(self, id):
    for card in self.cards:
      if card.id == id:
        return card

  def peek_card(self, idx=-1):
    if idx > 0 and idx < len(self.cards):
      return self.cards[idx]
    else:
      return self.cards[len(self.cards)-1]

  def append_card(self, card):
    self.cards.append(card)

  def insert_card(self, card, pos):
    self.cards.insert(card, pos)

  # TODO refactor self.cards as dict for easier/faster searches
  def contains(self, card_name):
    for card in self.cards:
      if card.name == card_name:
        return True
    return False

  def size(self):
    return len(self.cards)

  def print(self):
    for card in self.cards:
      print(card.name)