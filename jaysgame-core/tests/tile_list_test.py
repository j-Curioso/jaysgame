from tile import Tile
from player import Player

def is_entity_on_location(entity, tile):
  return entity.location is tile

def move_player(player, tile, direction):
  if direction in tile.neighbors:
    player.location = tile.neighbors[direction]
    print("Player moves " + direction)
  else:
    print("There is no path to the " + direction)

player = Player("Sol", 1, 10, 1, 0, 0)
tiles = []

for x in range(5):
  tiles.append(Tile())

start_tile = tiles[0]
start_tile.set_neighbor(tiles[1], "north")
start_tile.set_neighbor(tiles[2], "east")
start_tile.set_neighbor(tiles[3], "south")
start_tile.set_neighbor(tiles[4], "west")

player.location = start_tile

print("Is the player on the start tile? " + str(is_entity_on_location(player, start_tile)))
move_player(player, start_tile, "north")
print("Is the player on the start tile? " + str(is_entity_on_location(player, start_tile)))
print("Is the player on the north tile? " + str(is_entity_on_location(player, start_tile.neighbors["north"])))
