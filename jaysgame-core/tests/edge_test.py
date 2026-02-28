x, y = 2, 1

board_size = 5
max_x, max_y = board_size, board_size

def is_edge_tile(x, y):
  if (x == 0 or 
      x == board_size-1 or
      y == 0 or
      y == board_size-1):
    return True