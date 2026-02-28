import random
import json
import config
from monster import Monster
from boss import Boss

def roll():
  return random.randint(1, 20)

def prompt(msg, default_value=""):
  if default_value == "":
    value = input(f"{msg} ")
  else:
    value = input(f"{msg} ({default_value}) ")

  if not value:
    value = default_value

  return value

def safe_prompt(prompt_msg, default_value=""):
  choice = -1
  while choice == -1:
    try:
      choice = int(prompt(prompt_msg))
    except:
      continue
  return choice

def is_edge_tile(x, y):
  if (x == 0 or 
      x == config.board_size-1 or
      y == 0 or
      y == config.board_size-1):
    return True

monster_bestiary = {}
boss_bestiary = {}
def build_bestiaries():
  build_monster_bestiary(config.monster_cards_file)
  build_boss_bestiary(config.boss_cards_file)

def build_monster_bestiary(cards_file_path):
  cards_file = open(cards_file_path, 'r')
  cards_json = json.loads(cards_file.read())
  for card in cards_json:
    monster = Monster(card['name'], 
                      card['name'], 
                      card['attack'], 
                      card['damage'], 
                      card['defense'],
                      card['health'])
    monster_bestiary[monster.name.lower()] = monster

def build_boss_bestiary(cards_file_path):
  cards_file = open(cards_file_path, 'r')
  cards_json = json.loads(cards_file.read())
  for card in cards_json:
    boss = Boss(card['name'], 
                  card['attack'], 
                  card['damage'], 
                  card['defense'],
                  card['health'],
                  card['boss_summon'])
    boss_bestiary[boss.name.lower()] = boss