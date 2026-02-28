from flask import Flask

import config
from util import prompt
from game import Game
from player import Player

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
@app.route('/hello')
def hello():
   # Render the page
   return "Hello Python!"

@app.route('/jays-game')
def jays_game():
  print("Welcome to Jay's Game.")
  name = prompt("What is your name?", config.default_player_name)
  my_game = Game(config.board_size)
  my_game.add_entity(Player(name, 1, 10, 1, 0, 0, 0))
  my_game.start()
  while(my_game.running):
    my_game.do_round()

if __name__ == '__main__':
   # Run the app server on localhost:4449
   app.run('localhost', 4449)
