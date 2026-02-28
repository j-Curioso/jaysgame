import config
from util import prompt
from game import Game
from player import Player

print("Welcome to Jay's Game.")
name = prompt("What is your name?", config.default_player_name)
# color = prompt("What is your favorite color?")
my_game = Game(config.board_size)
my_game.add_entity(Player(name))
my_game.start()
while(my_game.running):
  my_game.do_round()