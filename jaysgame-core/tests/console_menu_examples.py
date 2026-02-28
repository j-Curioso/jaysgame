  
def search_menu():
  print("Type any name to bring up that creature's stat card. When finished type 'done'.")
  answer = ""
  while answer != "done":
    answer = prompt(">>")

    creature = monster_bestiary.get(answer)
    if creature != None:
      print(creature.get_stat_card())

    creature = boss_bestiary.get(answer)
    if creature != None:
      print(creature.get_stat_card())

def choice_menu(player):
    n = 1
    choice_map = {}
    for skill_name, skill_value in player.attack_skills.items():
      choice_map[str(n)] = skill_name
      print(str(n) + ". " + skill_name + ": " + str(skill_value))
      n += 1

    while True:
      answer = prompt("What do you attack with?")
      for choice, skill_name in choice_map.items():
        if str(choice) in answer or skill_name in answer:
          return skill_name