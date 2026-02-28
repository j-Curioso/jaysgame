
class TilePixel():
  def __init__(self, x, y, value=" "):
    self.x = x
    self.y = y
    self.value = value

class Tile():
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.pixels = {}
    self.tile_width = 9
    self.n_pixels = self.tile_width * self.tile_width

    # output = {}
    width, height = self.tile_width, self.tile_width
    for y in range(height):
      for x in range(width):
        val = " "
        if y == 0 or y == self.tile_width-1:
          val = "|"
        elif x == 0 or x == self.tile_width-1:
          val = "-"
        tile = TilePixel(x, y, val)
        self.pixels[(x, y)] = tile
    
  def player_on_tile(self, on_tile=False):
    if on_tile:
      self.pixels((4, 4)).value = "x"
    else:
      self.pixels((4, 4)).value = " "

  def open_close_door(self, direction, open=False):
    pixel_coords = (-1, -1)
    if direction == "north":
      pixel_coords = (5, 0)
    elif direction == "south":
      pixel_coords = (5, self.tile_width)
    elif direction == "east":
      pixel_coords = (self.tile_width, 5)
    elif direction == "west":
      pixel_coords = (0, 5)
    
    if open:
      val = " "
    else:
      if direction == "north" or direction == "south":
        val = "-"
      else:
        val = "|"

    pixel = self.pixels.get(pixel_coords)
    if pixel != None:
      pixel.value = val

# Create board
tile_array = {}
board_width = 5
width, height = board_width
for y in range(height):
  for x in range(width):
    tile_array[(x, y)] = Tile(x, y)


# Draw board
# Create a concept of the total number of pixel rows and columns
# Then iterate through tile collection, check if that tile has the pixel
# we are seeking, draw value
num_col = board_width * 9
num_row = board_width * 9

for y in range(num_col):
  for x in range(num_row):
    