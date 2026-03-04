import random
import math

from deck import Deck
from player import Player
from monster import Monster
from boss import Boss
from trap import Trap
from tile import Tile
from util import *
from stats import Stats
import config

class Game():

  def __init__(self, board_size):
    self.stats = Stats()

    self.running = False
    self.scenario = config.scenario

    self.entities = {} # holds Entities active on board, with id as the key.
    self.center_pos = (math.floor(board_size/2), math.floor(board_size/2))
    self.tiles = self._generate_tiles(board_size, self.center_pos)  # holds tiles with (x, y) as the key.

    self.available_turns = []
    self.completed_turns = []
    self.current_turn_id = None

    build_bestiaries()

    self.monster_deck = Deck(0)
    self.monster_deck.shuffle()
    self.monsters_per_tile = config.monsters_per_tile
    self.number_of_slain_monsters = 0

    self.boss_deck = Deck(1)
    self.boss_deck.shuffle()

    self.monster_graveyard = Deck(0, True)
    self.boss_graveyard = Deck(1, True)

    # if self.scenario == 0:
    #   self.total_number_of_monsters = self.monster_deck.size()

    if self.scenario == 2:
      boss_choice = random.randint(0, self.boss_deck.size())
      boss_card = self.boss_deck.peek_card(boss_choice)
      self.target_boss_name = boss_card.name

  def _generate_tiles(self, board_size, center_pos):
    # Outer tiles are boss rooms.
    # Inner tiles are normal rooms.
    # Center tile is the starting room.
    output = {}
    width, height = board_size, board_size
    for y in range(height):
      for x in range(width):
        tile = Tile(x, y)
        if is_edge_tile(x, y):
          tile.make_boss_tile()
        elif ((x, y) == center_pos):
          # tile.start_tile = True
          tile.make_start_tile()
        output[(x, y)] = tile
    return output

  def add_entity(self, entity):
    self.entities[entity.id] = entity
    self.available_turns.append(entity.id)
    if isinstance(entity, Boss):
        entity.do_boss_summon(self) # self should be the game?

  def calculate_game_stats(self):
    for card in self.monster_graveyard.cards:
      if isinstance(card, Monster):
        self.stats.number_slain_monsters += 1
      elif isinstance(card, Boss):
        self.stats.number_slain_bosses += 1
        self.stats.slain_bosses.append(card.name)

  def check_deaths(self):
    to_remove = []
    for entity in self.entities.values():
        if (not entity.alive):
          to_remove.append(entity)
    for entity in to_remove:
        self.remove_entity(entity)

  def check_win_condition(self):
    scenario = self.scenario
    if scenario == 0:
      return self.monster_graveyard.size() >= config.number_slain_to_win
    elif scenario == 1:
      return self.boss_graveyard.size() > 0
    elif scenario == 2:
      return self.boss_graveyard.contains(self.target_boss_name)

  def do_attack(self, player, args):
    if len(args) == 0:
      return

    target_name = args[0].strip().lower()
    target = player.location.get_enemy_by_name(target_name)

    if target == None:
      print("Not a valid target")
      return

    self.do_player_attack_enemy(player, target)
    player.actions -= 1

    # Check if target dead
    if (not target.alive):
      self.check_deaths()

      player.level_up()
      if (isinstance(target, Boss)):
        player.level_up()
      self.menu_player_skill_interrupt(player)

    # Check if room was cleared.
    if (player.location.is_clear()):
      self.room_clear(player.location)

  def do_enemy_attack_player(self, enemy, player):
    prompt(enemy.name + " attacks " + player.name)

    attack_skill = enemy.skills["attack"].value
    defense_skill = player.skills["defense"].value

    # Determine if attack will be blocked
    will_block = False
    if (player.block_tries > 0):
      will_block = self.menu_block(player)

    # Get total attack roll
    raw_attack_roll = roll()
    critical_hit = isinstance(enemy, Player) and raw_attack_roll >= player.critcal_hit_roll
    attack_roll = raw_attack_roll + attack_skill
    roll_string = str(attack_roll) + " (" + str(raw_attack_roll) + "+" + str(attack_skill) + ")"
    prompt(enemy.name + " rolls a " + roll_string + " to hit")

    if will_block:
      # Get total block roll
      player.block_tries -= 1
      raw_block_roll = roll()
      block_skill = player.skills["block"].value
      block_roll = raw_block_roll + block_skill
      roll_string = str(block_roll) + " (" + str(raw_block_roll) + "+" + str(block_skill) + ")"
      prompt(player.name + " rolls a " + roll_string + " to block.")

    # Attack blocked
    if will_block and block_roll >= attack_roll:
      prompt(player.name + " blocks the attack from " + enemy.name)

    # Attack hits
    elif attack_roll > defense_skill:
      dmg = enemy.damage
      if critical_hit: # Confirm with Jay if enemies can score critical hits.
        prompt("Critical hit! +1 damage.")
        dmg += 1
      player.apply_damage(dmg)
      prompt(enemy.name + " hits " + player.name + ", dealing " + str(dmg) + " damage. " + player.name + ": " + player.get_health_string())
      self.update_state()

    # Attack misses
    else:
      prompt(enemy.name + " misses " + player.name)

  def do_enemy_turn(self, enemy, players):
    # Randomly choose a player to attack
    player_count = len(players)
    if (player_count == 1):
      target = players[0]
    else:
      choice = random.randint(0, player_count)
      target = players[choice]

    if enemy.location == target.location:
      self.do_enemy_attack_player(enemy, target)

  def do_look(self, player, args):
    prefix = ""
    msg = ""
    if len(args) == 0:
      target_tile = player.location
      prefix = "This room"
    else:
      direction = args[0].strip().lower()
      target_tile = self.get_neighbor(player.location, direction)
      prefix = f"The room to the {direction}"

    target_tile_enemies = target_tile.get_enemy_names()
    target_tile_open_doors = target_tile.get_open_doors()
    msg = f"{prefix} has doors to the {target_tile_open_doors}"
    if len(target_tile_enemies) > 0:
      msg += f"\n{prefix} contains {target_tile_enemies}"
    else:
      msg += f"\n{prefix} is clear of enemies."

    print(msg)

  def do_move(self, player, args):
    if len(args) == 0:
      return

    target = args[0].lower().strip()
    if target in player.location.get_open_doors():
      self.move_entity(player, player.location, target)
      player.actions -= 1

  def do_player_attack_enemy(self, player, enemy, chosen_skill=""):
    print(player.name + " attacks " + enemy.name)

    # Choose attack skill and get attack/defense skill values
    if chosen_skill != "":
      attack_skill_name = chosen_skill
    else:
      attack_skill_name = self.menu_choose_attack_skill(player)

    attack_skill = player.skills[attack_skill_name].value
    defense_skill = enemy.skills["defense"].value

    # Perform rolls, determine critical hits
    raw_attack_roll = roll()
    critical_hit = raw_attack_roll >= player.critical_hit_roll
    attack_roll = raw_attack_roll + attack_skill
    roll_string = str(attack_roll) + " (" + str(raw_attack_roll) + "+" + str(attack_skill) + ")"
    prompt(player.name + " rolls a " + roll_string + " to hit")

    # Attack hits
    if attack_roll > defense_skill:
      dmg = player.damage
      if critical_hit:
        prompt("Critical hit! +1 damage.")
        dmg += 1
      enemy.apply_damage(dmg)
      prompt(player.name + " hits " + enemy.name + ", dealing " + str(dmg) + " damage. " + enemy.name + ": " + enemy.get_health_string())
      self.stats.total_damage_dealt += dmg
      self.update_state()

    # Attack misses
    else:
      prompt(player.name + " misses " + enemy.name)

  def do_player_turn(self, player):
    while player.actions > 0:
      self.menu_player_turn(player)

      # Check win/fail conditions
      if(not player.alive):
        prompt("   " + player.name + " has DIED.")
        quit()
      if (self.check_win_condition()):
        prompt("You win the game! ")
        quit()

  def do_round(self):
    prompt("--- Round " + str(self.round_count+1) + " begins. ---")

    # Complete all turns
    self.next_turn()
    while self.current_turn_id != None:
      current_entity = self.entities[self.current_turn_id]
      if len(self.completed_turns)-1 == 0: # TODO better detection logic
        prompt("--- Starting Player Turns ---")
      elif len(self.completed_turns)-1 == 1:
        prompt("--- Starting Enemy Turns ---")
      self.do_turn(current_entity)
      self.next_turn()

    # Reset
    for player in self.get_players():
      player.round_reset()
    self.available_turns = self.completed_turns.copy()
    self.completed_turns.clear()
    self.round_count += 1

  def do_search(self, args):
    if len(args) == 0:
      return

    results = ""
    term = args[0].strip().lower()
    
    if term == "*":
      card_list = ""
      for monster in monster_bestiary.values():
        card_list += monster.get_stat_card() + "\n\n"
      for boss in boss_bestiary.values():
        card_list += boss.get_stat_card() + "\n\n"
      results = card_list

    elif term == "boss":
      card_list = ""
      for boss in boss_bestiary.values():
        card_list += boss.get_stat_card() + "\n\n"
      results = card_list

    elif term == "monster":
      card_list = ""
      for monster in monster_bestiary.values():
        card_list += monster.get_stat_card() + "\n\n"
      results = card_list

    elif term == "trap":
      card_list = ""
      for trap in trap_bestiary.values():
        card_list += trap.get_stat_card() + "\n\n"
      results = card_list

    else:
      # Check monsters
      monster = monster_bestiary.get(term)
      if monster != None:
        results = monster.get_stat_card()

      # Check bosses
      boss = boss_bestiary.get(term)
      if boss != None:
        results = boss.get_stat_card()
      
      # Check traps
      trap = trap_bestiary.get(term)
      if trap != None:
        results = trap.get_stat_card()

      # Found nothing
      if results == "":
        results = "Found nothing"

    print(results)

  def do_trap(self, trap, revealing_tile):
    prompt("A " + trap.name + " is triggered as you open the door to the next room.")
    # Every player in the initiating room must pass the trap score
    for pid, player in revealing_tile.players.items():
      raw_roll = roll()
      trap_bonus = player.get_skill_value("trap")
      trap_roll = raw_roll + trap_bonus
      prompt(f"{player.name} rolls a {str(trap_roll)} ({str(raw_roll)}+{trap_bonus}) to evade")
      if trap_roll >= trap.trap:
        prompt(f"{player.name} evades {trap.name}")
        player.level_up()
        self.menu_player_skill_interrupt(player)
      else:
        player.apply_damage(trap.damage)
        prompt(f"{trap.name} deals {trap.damage} damage to {player.name} {player.health}/{player.max_health}")
        self.update_state()

  def do_turn(self, entity):
    prompt(entity.name + " located at (" + str(entity.location.x) + ", " + str(entity.location.y) + ") takes their turn.")
    if(isinstance(entity, Player)):
      self.do_player_turn(entity)
    else:
      self.do_enemy_turn(entity, self.get_players())

  def does_action_cost_action(self, choice):
    # TODO Create Action class with cost property
    if choice.startswith("applyskill"):
      return False
    elif choice.startswith("bestiary"):
      return False
    return True

  def get_game_stats(self):
    msg  = f"Bosses Slain: {self.stats.number_slain_bosses}\n"
    msg += f"Monsters Slain: {self.stats.number_slain_monsters}\n"
    msg += f"Damage Dealt: {self.stats.total_damage_dealt}\n"
    msg += f"Rooms Cleared: \n"
    return msg

  def get_help(self):
    menu  = "  ?                          List available commands\n"
    menu += "  search <term>              Search for information about <term>\n"
    menu += "  move <direction>           Move player in <direction>\n"
    menu += "  look                       Get information about the room you are standing in\n"
    menu += "  look <direction>           Get information about the room in <direction>\n"
    menu += "  wait                       Spend an action waiting\n"
    menu += "  char                       Display character stat sheet\n"
    menu += "  attack <target>            Attack <target>\n"
    menu += "  skill                      Display current skill values\n"
    menu += "  skill list                 Display current skill values\n"
    menu += "  skill inc <skill> <val>    Increase <skill> by <val>\n"
    menu += "  quit                       Quit the game\n"
    return menu

  def get_intro_text(self):
    players = self.get_players()
    player1 = players[0]
    if self.scenario == 2:
      msg = f"  You, {player1.name}, have been sent to slay the {self.target_boss_name}."
      msg += f"\n  The {self.target_boss_name} is rumored to live in the crypts of a local monastery."
      msg += "\n  Searching through the building, you find a trapdoor hidden in the floor."
      msg += f"\n  Crawling through, you find yourself in a dank crypt."
    else:
      msg = "  You, " + player1.name + ", have fallen through a trap door while exploring."
    msg += "\n  Around you are storage crates, barrels, and cobwebs."
    msg += "\n  This room has a single door leading deeper."
    return msg

  def get_neighbor(self, tile, direction):
    if (direction == "north"):
      return self.tiles.get((tile.x, tile.y - 1))
    elif (direction == "east"):
      return self.tiles.get((tile.x + 1, tile.y))
    elif (direction == "south"):
      return self.tiles.get((tile.x, tile.y + 1))
    elif (direction == "west"):
      return self.tiles.get((tile.x - 1, tile.y))

  def get_players(self):
    players = []
    for eid, entity in self.entities.items():
      if(isinstance(entity, Player)):
        players.append(entity)
    return players

  def move_entity(self, entity, tile, direction):
    neighbor = self.get_neighbor(tile, direction)
    neighbor_passage_open = neighbor.is_passage_open(Tile.get_opposing_direction(direction))
    passage_open = (tile.is_passage_open(direction)) and (neighbor_passage_open)
    if passage_open:
      entity.location.remove_entity(entity)
      entity.previous_location = entity.location
      entity.location = neighbor
      neighbor.add_entity(entity)
      print(entity.name + " moves " + direction)
    else:
      print("The passage is blocked to the " + direction)

  def menu_player_turn(self, player):

    answer = prompt("/>")
    if len(answer) == 0:
      return
    args = answer.split(" ", 1)
    command = args.pop(0)
    command = command.lower()

    if command == "?" or command == "/?" or command == "help":
      print(self.get_help())
      return

    elif command.startswith("look"):
      self.do_look(player, args)
      return

    elif command.startswith("char"):
      print(player.get_stat_card())
      return

    elif command.startswith("skill"):
      self.menu_player_skill(player, args)
      return

    elif command.startswith("search"):
      self.do_search(args)
      return

    elif command.startswith("move"):
      self.do_move(player, args)
      return

    elif command.startswith("attack"):
      self.do_attack(player, args)
      return

    elif command.startswith("wait"):
      player.actions -= 1
      return

    elif command.startswith("quit"):
      quit()

    else:
      print("Invalid command")

  def menu_player_skill_interrupt(self, player):
    print("You may spend skill points before continuing. Type 'continue' when ready.")
    print(player.get_skill_list())
    answer = ""
    while player.skill_points > 0:
      answer = prompt("/>")
      if len(answer) == 0:
        continue
      args = answer.split(" ", 1)
      command = args.pop(0)
      command = command.lower()
      if command.startswith("skill"):
        if len(args) == 0:
          args = [ "list" ]
        self.menu_player_skill(player, args)
        continue
      if command.startswith("continue"):
        return
    prompt("No more points to spend.")

  def menu_player_skill(self, player, args):

    if len(args) == 0:
      args = []
      args.append("list")

    args = args[0].lower().split(" ", 2)

    if args[0] == "list": 
      print(player.get_skill_list())
      return
    elif (args[0] == "inc" and 
          len(args) > 2 and
          args[2].isdigit()):
      skill_name = args[1]
      skill = player.skills.get(skill_name)
      if skill != None:
        increase_value = int(args[2])
        if (increase_value > 0) and (increase_value <= player.skill_points): # Move this check inside player.apply_skill?
          player.apply_skill(skill_name, increase_value)

  def menu_choose_attack_skill(self, player):
    n = 1
    choice_map = {}
    attack_skill_string = ""
    for attack_skill in player.get_attack_skills():
      choice_map[str(n)] = attack_skill.name
      attack_skill_string += f"{str(n)}. {attack_skill.name}[{attack_skill.value}]  "
      n += 1
    print(attack_skill_string)

    while True:
      answer = prompt("What do you attack with?")
      for choice, skill_name in choice_map.items():
        if str(choice) in answer or skill_name in answer:
          return skill_name

  def menu_block(self, player):
    while True:
      answer = prompt(f"Block? {player.block_tries}/{player.max_block_tries} attempts left this round. (y/n)")
      answer = answer.lower()
      if answer.startswith("n"):
        return False
      if answer.startswith("y"):
        return True

  def next_turn(self):
    if (len(self.available_turns) > 0):
      id = self.available_turns.pop(0)
      self.completed_turns.append(id)
    else:
      id = None
    self.current_turn_id = id

  def remove_entity(self, entity):
    location = entity.location
    prompt(entity.name + " at (" + str(location.x) + ", " + str(location.y) + ") is dead.")

    if (isinstance(entity, Player)):
      self.running = False
      quit()

    del self.entities[entity.id]

    if entity.id in self.available_turns:
      self.available_turns.remove(entity.id)

    if entity.id in self.completed_turns:
      self.completed_turns.remove(entity.id)

    location.remove_entity(entity)

    if (isinstance(entity, Monster)):
      self.monster_graveyard.append_card(entity)

    if (isinstance(entity, Boss)):
      self.boss_graveyard.append_card(entity)

    # Win condition should be checked any time an entity is removed
    self.check_win_condition() # TODO should be called at other points in the game

  def reveal_neighbor_tiles(self, tile):
    for direction, open in tile.passages.items():
      cardinal_direction = Tile.int_to_cardinal_direction(direction)
      if (open):
        neighbor = self.get_neighbor(tile, cardinal_direction)
        opposing_direction = Tile.get_opposing_direction(cardinal_direction)
        while not neighbor.is_passage_open(opposing_direction):
          neighbor.rotate_tile()
        if (neighbor != None and
            not neighbor.revealed):
          self.reveal_tile(neighbor, tile)

  def reveal_tile(self, tile, revealing_tile=None):
    tile.revealed = True
    if tile.boss_tile:
      boss = self.boss_deck.draw_card()
      if boss != None:
        tile.enemies[boss.id] = boss
        boss.location = tile
        self.add_entity(boss)
    else:
      for n in range(self.monsters_per_tile):
        card = self.monster_deck.draw_card() # Draw a card
        if card != None:
          if isinstance(card, Trap):     # Traps resolve immediately
            self.do_trap(card, revealing_tile)
            self.monster_graveyard.append_card(card)
          else:                          # Monsters are added to the room
            tile.enemies[card.id] = card # Add monster to room
            card.location = tile         # Set monster location to room
            self.add_entity(card)        # Add monster to game

  def room_clear(self, room):
    prompt("Tile at " + str(room.x) + ", " + str(room.y) + " has been cleared.")
    self.reveal_neighbor_tiles(room)
    return

  def start(self):
    self.running = True
    self.round_count = 0
    start_tile = self.tiles[self.center_pos]
    start_tile.revealed = True

    prompt("\n" + self.get_intro_text())
    print("\n" + self.get_help())

    # Add players to start tile
    # Provide opportunity to spend skill points
    for player in self.get_players():
      player.location = start_tile
      player.location.add_entity(player)
      self.menu_player_skill_interrupt(player)

    # Reveal any nearby tiles
    self.reveal_neighbor_tiles(start_tile)

  def update_state(self):
    self.check_deaths()
    self.check_win_condition()
