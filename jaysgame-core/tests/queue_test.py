def next_turn():
  print("next turn!")
  temp = queue.pop(0)
  queue.append(temp)

def whose_turn():
  return queue[0]

def print_queue():
  for x in range(len(queue)):
    print(str(x) + " " + queue[x])

queue = []
queue.append("Sol")
queue.append("Zombie")
queue.append("Witch")

print_queue()
next_turn()
print_queue()
