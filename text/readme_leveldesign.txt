howto design a level

Rules about level design are inspired by Dungeon Crawl Stone Soup.

Levels are made by humans using an text editor.
The first level is closest to the surface and very easy.
The deeper levels are harder and become more and more difficult.
A player enter the next (deeper) level by climbing a stair down.
A player can escape in the previous (upper) level by climbing a stair up.

rules:
  * each level, also the first one, need at least one stair up [<]
  * each level must have an outer perimeter of walls [#] without breaks
  * each level must be a square (each text line need to have the same length)
  * levels can have different size, but:
    * a stair up [<] or down [>] must have a corresponding valid field [.] in the next / previous level (same x, y)

warning signs:
A level designer may place warning signs in his level. Each level can have up to 10 different warning signs.
( represented by the numbers 0 to 9). Each sign can exist several times, but only 10 different signs are possible
per level. Meaning you can have the sign "beware of the traps" 20 times in a level, but you can not have an individual
warning sign text for each of the 20 traps.

warning sign text:
after the last textline of a level can be placed the text lines for the warning signs. Each text line for warning
sign text begins with the number [0-9] of the corresponding warning sign.

This is a short example of a valid level (has stair up and is surrunded by wall [#] with 2 different signs [1],[2].
The first sign is placed two times in the level.

#######
#<1 2.#
#1....#
#######
1 exit this level with the stair up.
2 This warning sign is unique.


legend:

you can use those chars to design your level

[.].....Floor
[#].....Wall
[<].....stair up (previous level or surface)
[>].....stair down (next level)
[M].....Monster (roams randomly)
[B].....Boss (hunts the player)
[S].....Statue (immobile)
[k].....key (can open door)
[L].....Loot
[D].....Door, closed, need key
0-9.....warning sign
[T].....trap

  

