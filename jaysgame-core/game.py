import random
import math

from deck import Deck
from player import Player
from monster import Monster
from boss import Boss
from trap import Trap
from tile import Tile
from util import *
import config

# TODO
#  - Print basic map (either room or whole board)
#  - Attack skills
#    - melee
#    - ranged
#    - fire
#    - water
#    - wind
#    - earth
#  - Defense skills
#    - defense
#    - block
#  - Utility skills
#    - loot
#    - sneak
#    - lockpick
#    - trap
#  - Items
#  - Aggro
#  - Sneak
#  - Treasure chests
#  - Game statistics
#  - Generalize menus and help menus.
#  - Return some clear indication when a command was not valid for all commands.
#  - Standardize naming, e.g. tiles should be called rooms everywhere. Passages should be doors.

# Questions/Notes
#  - Players can leave a tile if it still has monsters on it, but they may not enter and leave it on the same turn (forced to fight).
#  - Check if tile is clear after every removal? IDK this may be tricky.

# Bugs
#  - Cleared message should come before revealing other tiles
#  - Player should have chance to apply skills before opening door
#  - Log should say what direction the trap was triggered in
#  - Win condition not checked soon enough after character dies. Try checking win condition after every damage application.
#  - Entity exists in self.current_turn_id, but not self.entities. Not sure exact conditions to reproduce.


class Game():
  def __init__(self, board_size):
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

    if self.scenario == 0:
      self.total_number_of_monsters = self.monster_deck.size()

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

  def get_number_of_slain_monsters(self):
    return self.monster_graveyard.size()

  def check_win_condition(self):
    scenario = self.scenario
    if scenario == 0:
      return self.monster_graveyard.size() >= config.number_slain_to_win
    elif scenario == 1:
      return self.boss_graveyard.size() > 0
    elif scenario == 2:
      return self.boss_graveyard.contains(self.target_boss_name)

  def get_neighbor(self, tile, direction):
    if (direction == "north"):
      return self.tiles.get((tile.x, tile.y - 1))
    elif (direction == "east"):
      return self.tiles.get((tile.x + 1, tile.y))
    elif (direction == "south"):
      return self.tiles.get((tile.x, tile.y + 1))
    elif (direction == "west"):
      return self.tiles.get((tile.x - 1, tile.y))

  # Ok so why did we get no description for the start tile?
  def get_neighbor_description(self, neighbor):
    description = ""
    if neighbor.start_tile:
      description += "(Start Tile) "
    if (len(neighbor.enemies) > 0):
      description += neighbor.get_enemy_names()
      description += " lie in wait."
    return description

  def add_entity(self, entity):
    self.entities[entity.id] = entity
    self.available_turns.append(entity.id)
    if isinstance(entity, Boss):
        entity.do_boss_summon(self) # self should be the game?

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
      # del location.enemies[entity.id]
      self.monster_graveyard.append_card(entity)

    if (isinstance(entity, Boss)):
      # del location.enemies[entity.id]
      self.boss_graveyard.append_card(entity)

    # Win condition should be checked any time an entity is removed
    self.check_win_condition() # TODO should be called at other points in the game

    # room_clear should be called after remove_entity has returned.
    # # Check if location is clear after entity is gone.
    # if location.is_clear():
    #   self.room_clear(location)

  def check_deaths(self):
    to_remove = []
    for entity in self.entities.values():
        if (not entity.alive):
          to_remove.append(entity)
    for entity in to_remove:
        self.remove_entity(entity)

  def get_players(self):
    players = []
    for eid, entity in self.entities.items():
      if(isinstance(entity, Player)):
        players.append(entity)
    return players

  def next_turn(self):
    if (len(self.available_turns) > 0):
      id = self.available_turns.pop(0)
      self.completed_turns.append(id)
    else:
      id = None
    self.current_turn_id = id

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

  def display_intro_text(self):
    players = self.get_players()
    player1 = players[0]
    if self.scenario == 2:
      msg = f"You, {player1.name}, have been sent to slay the {self.target_boss_name}."
    else:
      msg = "You, " + player1.name + ", have fallen through a trap door while exploring."
    msg += "\nAround you are storage crates, barrels, and cobwebs."
    prompt(msg)

  def start(self):
    self.running = True
    self.round_count = 0
    start_tile = self.tiles[self.center_pos]
    start_tile.revealed = True

    self.display_intro_text()
    print("\n" + self.menu_help_player_turn())

    # Add players to start tile
    for player in self.get_players():
      player.location = start_tile
      player.location.add_entity(player)

    # Reveal any nearby tiles
    self.reveal_neighbor_tiles(start_tile)

  def do_round(self):
    print("--- Round " + str(self.round_count+1) + " begins. ---")

    # Complete all turns
    self.next_turn()
    while self.current_turn_id != None:
      current_entity = self.entities[self.current_turn_id]
      if len(self.completed_turns)-1 == 0:
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

  def do_turn(self, entity):
    print(entity.name + " located at (" + str(entity.location.x) + ", " + str(entity.location.y) + ") takes their turn.")
    if(isinstance(entity, Player)):
      self.do_player_turn(entity)
    else:
      self.do_enemy_turn(entity, self.get_players())

  def do_player_turn(self, player):
    while player.actions > 0:
      # Right now this is setup to ask for a choice, then perform the choice.
      # Refactor so action is performed with the choice-ask menu.
      choice = self.menu_player_turn(player)
      if choice != None and len(choice) > 0:
        self.do_player_action(player, choice)

      # Check win/fail conditions
      if(not player.alive):
        prompt("   " + player.name + " has DIED.")
        quit()
      if (self.check_win_condition()):
        prompt("You win the game! ")
        quit()

  # TODO refactor/remove
  def do_player_action(self, player, choice):
    if "_" in choice:
      args = choice.split("_", 1)
      action, target = args[0], args[1]
    else:
      action, target = choice, ""

    if (action == "move"):
      self.move_entity(player, player.location, target)

    elif (action == "attack"):
      # Combat
      enemy = self.entities[target]
      self.do_player_attack_enemy(player, enemy)

      # Check if enemy dead
      if (not enemy.alive):
        self.check_deaths() # TODO refactor how deaths are checked/handled

        player.level_up()
        if (isinstance(enemy, Boss)):
          player.level_up()
        self.menu_player_skill_interrupt(player)

      # Check if room was cleared.
      if (player.location.is_clear()):
        self.room_clear(player.location)

    elif (action == "quit"):
      quit()

    elif (action == "skip"):
      return

    else:
      print("Invalid command")

    # Determine if action should be spent
    if self.does_action_cost_action(choice):
      player.actions -= 1

  def does_action_cost_action(self, choice):
    # TODO Create Action class with cost property
    if choice.startswith("applyskill"):
      return False
    elif choice.startswith("bestiary"):
      return False
    return True

  def do_enemy_turn(self, enemy, players):
    current_tile = enemy.location
    # Randomly choose a player to attack
    player_count = len(players)
    if (player_count == 1):
      target = players[0]
    else:
      choice = random.randint(0, player_count)
      target = players[choice]

    if enemy.location == target.location:
      self.do_enemy_attack_player(enemy, target)

  def do_player_attack_enemy(self, player, enemy):
    prompt(player.name + " attacks " + enemy.name)

    # Choose attack skill and get attack/defense skill values
    attack_skill_name = self.menu_choose_attack_skill(player)
    attack_skill = player.skills[attack_skill_name].value
    defense_skill = enemy.skills["defense"].value

    # Perform rolls, determine critical hits
    raw_attack_roll = roll()
    critical_hit = raw_attack_roll >= player.critical_hit_roll
    attack_roll = raw_attack_roll + attack_skill
    roll_string = str(attack_roll) + " (" + str(raw_attack_roll) + "+" + str(attack_skill) + ")"
    print(player.name + " rolls a " + roll_string + " to hit")

    # Attack hits
    if attack_roll > defense_skill:
      dmg = player.damage
      if critical_hit:
        print("Critical hit! +1 damage.")
        dmg += 1
      enemy.apply_damage(dmg)
      print(player.name + " hits " + enemy.name + ", dealing " + str(dmg) + " damage. " + enemy.name + ": " + enemy.get_health_string())
      self.update_state()

    # Attack misses
    else:
      print(player.name + " misses " + enemy.name)

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
    print(enemy.name + " rolls a " + roll_string + " to hit")

    if will_block:
      # Get total block roll
      player.block_tries -= 1
      raw_block_roll = roll()
      block_skill = player.skills["block"].value
      block_roll = raw_block_roll + block_skill
      roll_string = str(block_roll) + " (" + str(raw_block_roll) + "+" + str(block_skill) + ")"
      print(player.name + " rolls a " + roll_string + " to block.")

    # Attack blocked
    if will_block and block_roll >= attack_roll:
      print(player.name + " blocks the attack from " + enemy.name)

    # Attack hits
    elif attack_roll > defense_skill:
      dmg = enemy.damage
      if critical_hit:
        print("Critical hit! +1 damage.")
        dmg += 1
      player.apply_damage(dmg)
      print(enemy.name + " hits " + player.name + ", dealing " + str(dmg) + " damage. " + player.name + ": " + player.get_health_string())
      self.update_state()

    # Attack misses
    else:
      print(enemy.name + " misses " + player.name)

  def do_trap(self, trap, revealing_tile):
    prompt("A " + trap.name + " is triggered as you open the door to the next room.")
    # Every player in the initiating room must pass the trap score
    for pid, player in revealing_tile.players.items():
      raw_roll = roll()
      trap_bonus = player.get_skill_value("trap")
      trap_roll = raw_roll + trap_bonus
      print(f"{player.name} rolls a {str(trap_roll)} ({str(raw_roll)}+{trap_bonus}) to evade")
      if trap_roll >= trap.trap:
        print(f"{player.name} evades {trap.name}")
        player.level_up()
        self.menu_player_skill_interrupt(player)
      else:
        player.apply_damage(trap.damage)
        print(f"{trap.name} deals {trap.damage} damage to {player.name} {player.health}/{player.max_health}")
        self.update_state()

  def menu_player_turn(self, player):

    # TODO
    # If you move twice in one turn current_tile_open_doors/tile_enemies is not updated.
    # We need some sort of _update_relevant_location_info method.

    # TODO commands to implement
    # equip
    #   list
    # map

    display_current_tile_info = True
    answer = ""
    while player.actions > 0:
    # while True:

      current_tile = player.location

      if display_current_tile_info:
        display_current_tile_info = False
        current_tile_enemies = current_tile.get_enemy_names()
        current_tile_open_doors = current_tile.get_open_doors()
        print(f"This room has open doors to the {current_tile_open_doors}.")
        if len(current_tile_enemies) > 0:
          print(f"This room contains {current_tile_enemies}.")
        else:
          print(f"This room is clear of enemies.")

      answer = prompt("/>")
      if len(answer) == 0:
        continue
      args = answer.split(" ", 1)
      command = args.pop(0)
      command = command.lower()

      if command == "?" or command == "/?" or command == "help":
        print(self.menu_help_player_turn())
        continue

      elif command.startswith("look"):
        if len(args) > 0:
          target = args[0].lower()
          if target in current_tile_open_doors:
            neighbor = self.get_neighbor(current_tile, target)
            enemies = neighbor.get_enemy_names()
            open_doors = neighbor.get_open_doors()
            print(f"The room to the {args[0]} has passages to the {open_doors}.")
            if len(enemies) > 0:
              print(f"The room to the {args[0]} contains {enemies}.")
            else:
              print(f"The room to the {args[0]} is clear of enemies.")
        else:
          print("\"look\" requires a direction. Example: look north")
          continue
        continue

      elif command.startswith("char"):
        print(player.get_stat_card())
        continue

      # TODO update so enter "skill" or "skill list" lists current skills and their values
      elif command.startswith("skill"):
        if len(args) > 0:
          self.menu_player_skill(player, args)
        continue

      elif command.startswith("search"):
        if len(args) > 0:
          print(self.do_search(args[0].lower()))
        continue

      elif command.startswith("move"):
        if len(args) > 0:
          target = args[0].lower()
          if target in current_tile_open_doors:
            self.move_entity(player, player.location, target)
            player.actions -= 1
            display_current_tile_info = True
          else:
            print("Not a valid move")
        continue

      # TODO update to take attack_skill as first argument, then target. 
      #      If no skill is provided, then prompt for skill
      elif command.startswith("attack"):
        if len(args) == 1:
          target_name = args[0].lower()
          target = player.location.get_enemy_by_name(target_name)
          if target != None:
            return f"attack_{target.id}"
        print("Not a valid target")
        # elif len(args) > 2:
          
        continue

      elif command.startswith("wait"):
        player.actions -= 1
        return "skip_action"

      elif command.startswith("quit"):
        quit()

      else:
        print("Invalid command 2")

  def menu_player_skill_interrupt(self, player):
    print("You may spend skill points before continuing. Type 'continue' when ready.")
    answer = ""
    while player.skill_points > 0:
      answer = prompt("/>")
      if len(answer) == 0:
        continue
      args = answer.split(" ", 1)
      command = args.pop(0)
      command = command.lower()
      if command.startswith("skill"):
        if len(args) > 0:
          self.menu_player_skill(player, args)
        continue
      if command.startswith("continue"):
        return
    print("No more points to spend.")

  def menu_player_skill(self, player, args):
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

  def menu_help_player_turn(self):
    menu  = "  ?                          List available commands\n"
    menu += "  search <term>              Search for information about <term>\n"
    menu += "  move <direction>           Move player in <direction>\n"
    menu += "  look <direction>           Get information about the room in <direction>\n"
    menu += "  wait                       Spend an action waiting\n"
    menu += "  char                       Display character stat sheet\n"
    menu += "  attack <target>            Attack <target>\n"
    menu += "  attack <skill> <target>    Attack <target> using <skill>\n"
    menu += "  skill                      Display current skill values\n"
    menu += "  skill list                 Display current skill values\n"
    menu += "  skill inc <skill> <val>    Increase <skill> by <val>\n"
    menu += "  quit                       Quit the game\n"
    return menu

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

  def do_search(self, term):
    if term == "*":
      card_list = ""
      for monster in monster_bestiary.values():
        card_list += monster.get_stat_card() + "\n\n"
      for boss in boss_bestiary.values():
        card_list += boss.get_stat_card() + "\n\n"
      return card_list
    else:
      # Check monsters
      creature = monster_bestiary.get(term)
      if creature != None:
        return (creature.get_stat_card())

      # Check bosses
      creature = boss_bestiary.get(term)
      if creature != None:
        return (creature.get_stat_card())
      
      # Found nothing
      return "Found nothing"

  def update_state(self):
    self.check_deaths()
    self.check_win_condition()

  # triggers
  def room_clear(self, room):
    prompt("Tile at " + str(room.x) + ", " + str(room.y) + " has been cleared.")
    self.reveal_neighbor_tiles(room)
    return