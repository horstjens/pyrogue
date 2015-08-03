# -*- coding: utf-8 -*-                # only necessary for python2
from __future__ import print_function  # only necessary for python2
from __future__ import division        # only necessary for python2 
try:                                   # only necessary for python2
    input = raw_input                  # only necessary for python2
except NameError:                      # only necessary for python2
    pass                               # only necessary for python2

import random    # 


def wait(msg="press ENTER"):
    a = input(msg)
    return a


def loot():
    """create an item"""
    zeugs = ["trash", "bone", "coin", "knife", "rags",
             "fork", "toy", "splayer_posrd", "armor",
             "gem", "healing potion", "shield"]
    return random.choice(zeugs)   


def hilfe():
    """show help text, waits for ENTER key"""
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("commands:")
    print("[w] [a] [s] [d]......player movement")
    print("[<] [>]..............go up / go down (at stairs)")
    print("[i]..................inventory")
    print("[quit] [exit] [Q]....quit the game")        
    print("[?] [help]...........show this help text")
    print("[q]..................quaff healing potion")
    print("[Enter]..............wait one turn")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("symbols:")
    print("[#]..................wall")
    print("[.]..................floor")
    print("[M],[B],[S]..........monster, boss, statue")
    print("[k]..................key")
    print("[L]..................loot")
    print("[D]..................door (closed)")
    print("[!]..................warning sign")
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    wait()


def combat_round(m1, m2):
    txt = []         # 
    if m1.hitpoints > 0 and m2.hitpoints > 0:
        txt.append("{} ({} hp) swings at {} ({} hp)".format(m1.name, m1.hitpoints, m2.name, m2.hitpoints))
        if "splayer_posrd" in m1.inventory:      # and inventory["weapon"] >0:
            damage = random.randint(1, 4)
            weapon = "splayer_posrd"
        elif "knife" in m1.inventory: 
            damage = random.randint(1, 3)
            weapon = "knife"
        else:
            damage = random.randint(1, 2)
            weapon = "fist"
        txt.append("{} attacks {} with {} for {} raw damage".format(
              m1.name, m2.name, weapon, damage))
        if "armor" in m2.inventory: 
            damage -= 1
            txt.append("armor of {} absorbs 1 point of damage ".format(m2.name))
        if "shield" in m2.inventory:
            damage -= 1
            txt.append("Schield of {} absorbs 1 point of damage ".format(m2.name))
        if damage > 0:
            m2.hitpoints -= damage
            txt.append("{} looses {} hitpoints ({} hp left)".format(m2.name, damage, m2.hitpoints))
        else:
            txt.append("{} stays unharmed".format(m2.name))
    #return txt
    for line in txt:
        print(line)
    wait()


class Monster(object):
    def __init__(self, x, y, hp=0):
        if hp == 0:
            self.hitpoints = random.randint(5, 10)
        else:
            self.hitpoints = hp
        self.x = x
        self.y = y
        self.name = "Monster"
        self.inventory = {}
        for z in ["knife", "splayer_posrd", "shield", "armor"]:
            if random.random() < 0.1:  # 10% Chance
                self.inventory[z] = 1
        
        
class Player(Monster):
    def __init__(self, x, y, hp=25, name="Player"):
        Monster.__init__(self, x, y, hp)
        self.name = name
        self.keys = 0
        self.z = 0        # z=0 is the first dungeon, z=2 is the second dungeon level etc.

    def show_inventory(self):
        """Zeigt Anzahl und Art von Gegenständen im inventory"""
        print("you carry with you those items:")
        if len(self.inventory) == 0:
            print("your inventory is empty")
        else:
            print("amount, description")
            print("==================")
            for thing in self.inventory:
                print(self.inventory[thing], thing)
                
    def take(self, thing):
        """increase amount of a specific thing in the inventory"""
        if thing in self.inventory:
            self.inventory[thing] += 1
        else:
            self.inventory[thing] = 1


class Level(object):
    def __init__(self, filename):
        """liest den filenamen ein und erzeugt ein Level-Object"""
        self.lines = []
        self.signs = {}       # schildnummer: schildtext
        self.monsters = []
        #self.sight_radius = 10
        with open(filename) as f:
            y = 0
            for line in f:
                goodline = ""
                if line[0] in "123456789":
                    self.signs[line[0]] = line[1:-1] # strip the first and last char
                    continue
                elif line.strip() == "":
                    continue
                else: 
                    x = 0
                    for char in line[:-1]:
                        if char == "M" or char =="B" or char == "S":  # monster, boss, statue    
                            self.monsters.append(Monster(x, y))
                            goodline += "."
                        else:
                            goodline += char
                        x += 1
                self.lines.append(goodline)
                y += 1
    
    def update(self):
        """remove all monsters with fewer than 1 hitpoints from level"""
        self.monsters = [m for m in self.monsters if m.hitpoints > 0]
                    
    def replace_line(self, x, y, new="."):
        """replace a char in  a line with another one
           do not confuse with the in-buildt string method .replace()"""
        self.lines[y] = self.lines[y][:x]+new+self.lines[y][x+1:] 
    
    def is_monster(self, x, y):
        """testing if a monster is at a specific position"""
        for monster in self.monsters:
            if monster.hitpoints > 0 and monster.x == x and monster.y == y:
                return monster  # every value other than 0 or False is  True
        return False
        
    def move_monster(self, player):
        """moves monster in a random direction (or not at all)"""
        for monster in self.monsters:
            x, y = monster.x, monster.y
            dirs = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
            dx, dy = random.choice(dirs)
            if self.is_monster(x + dx, y + dy):
                continue
            if x+dx == player.x and y+dy == player.y:
                combat_round(monster, player)
                combat_round(player, monster)
                continue     # monster should not run into player
            player_poshin = self.lines[y+dy][x+dx]
            if player_poshin in "#TD":
                continue     # monster should not run into Traps, Doors or Walls
            monster.x += dx
            monster.y += dy 
    
    def paint(self, px, py):
        """print out the actual level with monsters and player"""
        y = 0
        for line in self.lines:
            x = 0
            for char in line:
                if x == px and y == py:
                    print("@", end="")
                elif self.is_monster(x, y):
                    print("M", end="")
                elif char in "123456789":
                    print("!", end="")  # warning sign
                else:
                    print(char, end="") 
                x += 1
            print()  # print line ending
            y += 1


def game(levels , playerx=1, playery=1, playerhp=50, playername="Rambo"):
    p = Player(playerx, playery, playerhp, playername)          # player begins with 50 hitpoints at x:1,y:1
    status = ""
    while p.hitpoints > 0 and p.z >= 0:            # run this loop as long as the player is alive
        level = levels[p.z]
        level.paint(p.x, p.y)
        print(status)                 
        dx, dy = 0, 0
        status = ""                    # ----------- ask ----------------------  
        a = input("what now? hp:{} keys:{} >".format(p.hitpoints, p.keys))
        if a == "exit" or a == "quit" or a == "Q":  # ----- quit ------
            break    
        elif a == "i":                 # --------- inventory --------
            p.show_inventory()
            wait()
            continue                   # do not move monsters etc when inspecting inventory
        elif a == "?" or a == "help":  # ---- help -------
            hilfe()
            continue
        if a == "a":                   # ------------- move the player ---------
            dx -= 1
        elif a == "d":
            dx += 1
        elif a == "w":
            dy -= 1
        elif a == "s":
            dy += 1
        elif a == "<":                 # ------ move level up ---------
            if level.lines[p.y][p.x] != "<":
                status = "You need to find a stair upwards [<]"
                continue
            elif p.z == 0:
                print("You leave the dungeon and return to the surface world.")
                break
            p.z -= 1
            continue
        elif a == ">":                 # ------ move level down ------
            if level.lines[p.y][p.x] != ">":
                status = "You need to find a stair downwards [>]"
                continue
            p.z += 1
            continue
        elif a == "q":                  # --------- healing potion ------------
            if "healing potion" in p.inventory and p.inventory["healing potion"] > 0:
                p.inventory["healing potion"] -= 1
                effekt = random.randint(2, 5)
                p.hitpoints += effekt
                status = "you drink one healing potion and win back {} hitpoints".format(effekt)
            else:
                status = "you have no healing potion. Gather more loot!"
        player_poshin = level.lines[p.y+dy][p.x+dx] # ----- player runs into door, trap wall? ----
        monster = level.is_monster(p.x+dx, p.y+dy)
        if monster:
            combat_round(p, monster)
            combat_round(monster, p)
        elif player_poshin == "#":         # running into walls?
            status = "Ouch, don't run into walls please!"
            p.hitpoints -= 1
        elif player_poshin == "D":
            if p.keys > 0:
                p.keys -= 1
                status = "used 1 key to open door"
                level.replace_line(p.x+dx, p.y+dy, ".") 
            else:
                status = "Ouch! This door was closed. Find a key."
                p.hitpoints -= 1
        else:
            p.x += dx
            p.y += dy   # ----------------- player is at a new position --------
        player_pos = level.lines[p.y][p.x]                # where am i now
        if player_pos in "123456789":
                status = "a sign says: " + level.signs[player_pos]
        elif player_pos == "T":                           # run into trap?
            damage = random.randint(1, 4)
            status = "Ouch, that was a trap! {} damage!".format(damage)
            p.hitpoints -= damage
            if random.random() < 0.5:             # 50% Chance to destroy trap?
                level.replace_line(p.x, p.y, ".")
                status += "the trap is destroyed!"
        elif player_pos == "k":                           # found key?
            status = "i found a key!"
            p.keys += 1
            level.replace_line(p.x, p.y, ".")
        elif player_pos == "L":                           # found loot?
            p.take(loot())
            level.replace_line(p.x, p.y, ".")
        elif player_pos == "<":
            status = "stair upwards. press [<] and [Enter] to climb up"
        elif player_pos == ">":
            status = "stair downwards. press [>] and [Enter] to climb down"
        level.update()                             # remove dead monsters
        level.move_monster(p)                      # move around alive monsters
    print("Game Over. Hitpoints: {}".format(p.hitpoints))
    if p.hitpoints < 1:
        print("You are dead.")
    p.show_inventory()

if __name__ == "__main__":
    # start a dungeon with level1demo.txt and level2demo.txt, player "Rambo" starts at x1,x2 with 50 hitpoints
    game([Level("level1demo.txt"), Level("level2demo.txt")], 1, 1, 50, "Rambo")
