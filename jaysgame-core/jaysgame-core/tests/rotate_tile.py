
passages = {
  0: True,
  1: True,
  2: False,
  3: False
}

def rotate_tile(rotation_direction):
  # rotation_direction should be
  # -1 = counter-clockwise
  #  1 = clockwise
  temp_passages = passages.copy()
  passages.clear()
  for cardinal_direction, open in temp_passages.items():
    new_direction = (cardinal_direction + rotation_direction) % 4
    passages[new_direction] = open

def is_direction_open(cardinal_string):
  if cardinal_string == "north": 
    return passages[0]
  elif cardinal_string == "east":
    return passages[1]
  elif cardinal_string == "south":
    return passages[2]
  elif cardinal_string == "west":
    return passages[3]

def pretty_print_passages():
  img = "--"
  if is_direction_open("north"):
    img += " "
  else:
    img += "-"
  img += "--\n"
  img += "|   |\n"
  if is_direction_open("west"):
    img += "    "
  else:
    img += "|   "
  if is_direction_open("east"):
    img += " \n"
  else:
    img += "|\n"
  img += "|   |\n"
  img += "--"
  if is_direction_open("south"):
    img += " "
  else:
    img += "-"
  img += "--\n"
  print(str(passages))
  print(img)

pretty_print_passages()

for n in range(3):
  rotate_tile(1)
  pretty_print_passages()

for n in range(1):
  rotate_tile(-1)
  pretty_print_passages()