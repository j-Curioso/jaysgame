# Jay's Game

Jay's Game (the video game) is based on Jay's Game (the board game). It is a turn-based, rogue-like RPG. You play as a character who has unfortunately fallen through a trap door into the middle of a dungeon made of several rooms. This is represented by a board made of tiles, with one tile representing one room. 

## Interacting with the Game

The game will display a message when an event occurs (e.g., a monster attacking you). Hit enter to continue to the next message. When player interaction is required, a terminal prompt is presented. At any point type '?' to receive a list of available commands. Type any available command to proceed.

## The Board

The board is setup up as a square with a certain number of rooms. Each room may have 1-4 open passages going in some cardinal direction. The player starts in room in the center of the board. Nothing starts in this room besides the player. When another room is revealed two cards are drawn from the monster deck and placed in that room. The rooms on the very edges of the board are special -- when revealed one card is drawn from the boss deck and placed instead of drawing from the monster deck.

## Decks

There are 3 decks in the game: a monster deck, a boss deck, and an item deck. The monster deck may contain monsters, traps, and several other special things. Whenever a monster or boss is defeated it is placed in the monster graveyard or boss graveyard. Whenever a consumable item is used or any item is destroyed, it is placed in the item graveyard.

## Players

Players start at level 1 with no points in any skills and 10 max life. If a player defeats a creature, that player gains 1 level and 2 skill points. Skill points may be applied immediately or saved. Skills can be increased to a maximum of 10. A player may achieve a maximum level of 20. That is 38 skills points to spend for you min/max'ers.

### Experience

| Action | Gained Levels | Gained Skill Points |
| --- | --- | --- |
| Defeat monster | 1 | 2 |
| Defeat trap    | 1 | 2 |
| Defeat boss    | 2 | 4 |
| Unlock Treasure Chest | 0 | 0 |
| Exist on tile when boss is defeated AND hit boss at least once | 1 | 2 |

### Movement

Players may spend an action to move to an adjacent tile, assuming there is a door open in that direction. A room must be cleared of enemies before closed doors may be opened.

### Skills

There are 12 skills across 3 categories.

#### Offense Skills

- melee
- ranged
- fire
- water
- wind
- earth

#### Defense skills
- defense
- block
- trap

#### Utility skills
- loot
- sneak
- lockpick

## Monsters

When a player defeats a monster, that player gains 1 level and 2 skill points.

## Bosses

When a player defeats a boss, that player gains 2 levels and 4 skill points. Any other players in the same room gain 1 level and 2 skill points.

## Items

## Treasure

## Stat Card

### Example Stat Card
```
lvl     hp      dmg     atk     def     blk     sp      act     loc     scr     
1       10/10   1       0       0       0       0       1       1,2     0/10  
```

```
lvl = Current level.
hp  = Health.
dmg = Damage applied per successful hit.
atk = Bonus added to roll to hit.
def = Bonus added to defense score.
blk = Bonus added to roll to block.
sp  = Number of unspent skill points.
act = Number of actions left this turn.
loc = Location on board. Rooms are numbers as (x,y) with 0,0 being the most Northwest room.
scr = Player score. Number of monsters slain out of total in dungeon.
```

## Gameplay

The game is broken up into rounds, which are further broken up into turns. Each entity on the board takes a single turn per round, in order.

Every turn a player has 2 actions. Monsters have 1 action. Turns are over when an entity has no more actions. Below is a table of actions and their cost.

| Action             | Cost |
| --------           | ------- |
| Move               | 1 |
| Attack             | 1 |
| Wait               | 1 |
| View Bestiary      | 0 |
| Apply Skill Points | 0 |
| Equip Item         | 1 |

Currently monsters may only spend their action to attack a player on the same tile. They do not move. Sometimes they have been known to view the bestiary.

## Scenarios

| Scenario     | Number | Description |
| ---          | ---    | --- |
| KillCount    | 0      | Defeat 10 monsters. |
| Boss         | 1      | Defeat any boss |
| SpecificBoss | 2      | Defeat a randomly chosen boss. You may encounter other bosses before finding your target. |

## Combat

Any time one entity attacks another, they enter combat. The attacker will roll and add their attack score to the roll. If this roll is higher than or equal to the defenders defense score, then the attack hits. Each entity will have a damage score, which is applied to the defenders health on a successful hit.

Some entities, including all players, have the ability to block incoming attacks. This is controlled by both their block score as well as the total number of block attempts they get per round. When an attack is initiated the defender may choose to block. If they do then they roll, adding their block score. The attack roll must be higher than the block roll to hit. If the block is unsuccessful, then the attack roll must still beat or match the defenders defense score.
