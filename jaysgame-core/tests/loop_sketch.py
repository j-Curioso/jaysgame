running = True

while(running):

  while(current_tile.clear()): # all player options
  cmd = get_user_cmd()
    if(cmd == equip_item):
      # equip item
    elif(cmd == apply_skill):
      # apply skill point
    elif(cmd == move_to_tile):
      # move to tile

  while(not current_tile.clear()): # fight a monster or try to flee
    if(isinstance(current_tile.active_entity) == Player):
      # player menu
      cmd = get_user_cmd()
      if(cmd == fight_monster):
        # fight a monster
        
      elif(cmd == flee):
        # try to flee
    else:
      # monster attacks a player
    current_tile.next_turn()