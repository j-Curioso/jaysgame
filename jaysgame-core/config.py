# GUI Configs
window_width = 600
window_height = 400
window_size = (window_width, window_height)

# Core Configs
scenario = 2

default_player_name = "Norbert"
player_start_level = 1
player_start_skill_points = 2
player_start_life = 10
player_start_damage = 1
player_start_melee = 0
player_start_ranged = 0
player_start_defense = 0
player_start_block = 0
player_start_block_tries = 1
player_start_trap = 0
player_max_level = 20
player_max_skill_level = 10
player_start_critical = 20

monsters_per_tile = 2
number_slain_to_win = 10
board_size = 7

tile_rotation_direction = 1 # 1=clockwise, -1=counter-clockwise
open_passage_chance = 5 # 0-20. If roll() is higher than this value, the passage is open

monster_cards_file = 'data/monster_cards.json'
trap_cards_file = 'data/trap_cards.json'
boss_cards_file = 'data/boss_cards.json'
item_cards_file = 'data/item_cards.json'