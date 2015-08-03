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


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class LevelError(Error):
    """a specific Exception subclass handling level design errors"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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
        for z in ["knife", "sword", "shield", "armor"]:
            if random.random() < 0.1:  # 10% Chance
                self.inventory[z] = 1

class Boss(Monster):
    def __init__(self, x, y, hp=0):
        Monster.__init__(self, x, y, hp)

class Statue(Monster):
    def __init__(self, x, y, hp=0):
        Monster.__init__(self, x, y, hp)
        
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

    # class attribute
    LEGEND = {
    "#": "wall",
    "D": "door",
    ".": "floor",
    "<": "stair up",
    ">": "stair down",
    "T": "trap",
    "M": "monster",
    "B": "Boss",
    "S": "Statue",
    "L": "loot",
    "k": "key"
    }

    @staticmethod
    def load_level(filename):
        """load a text file and return a list of non-empty lines without newline characters"""
        lines = []
        with open(filename, "r") as f:
            for line in f:
                if line.strip() != "":
                   lines.append(line[:-1])  # exclude newline char
        return lines

    @staticmethod
    def check_level(filename):
        """check for level layout errors and returns list of lines and dict of level warning signs"""
        lines = Level.load_level(filename)
        if len(lines) == 0:
            raise LevelError("{}: level has no lines".format(filename))
        width = len(lines[0])  # length of first line of level
        line_number = 1
        has_stairs_up = False
        warning_signs = {}
        good_lines = []
        for line in lines:
            if line[0] in "0123456789":
                if line[1:].strip() == "":
                    raise LevelError("{}: warning sign {} definition without text".format(filename, line[0]) +
                                     " in line number {}".format(line_number))
                warning_signs[line[0]] = line[1:].strip()
        # read all lines again from start, because we have now a functional warning_signs dictionary
        for line in lines:
            if line[0] in "0123456789":
                continue  # warning sign definition text, ignore this line
            if len(line) != width:
                raise LevelError("{}: bad line length".format(filename) +
                                 " in line number {}".format(line_number))
            x = 1
            for char in line:
                if char == "<":
                    has_stairs_up = True
                elif char in "0123456789":
                    if char not in warning_signs:
                        raise LevelError("{}: warning sign symbol {} without definition".format(filename, char) +
                                         " in line number {}".format(line_number))
                elif char not in Level.LEGEND:
                    raise LevelError("{}: line {} pos {}:".format(filename, line_number, x) +
                                     "char {} is not in Level.LEGEND".format(char)+
                                     "\n allowed Symbols are numbers for warning signs and:\n"+
                                     str(Level.LEGEND.keys()))
                x += 1
            good_lines.append(line)
            line_number += 1
        if not has_stairs_up:
            raise LevelError("{}: level has no stair up sign (<)".format(
                             filename))
        return good_lines, warning_signs

    @staticmethod
    def check_levels(*args):
        """load level file names (comma separated) from disk,
           display errors and return list of error free Level() objects"""
        # args are the level names, like "level1.txt". Use os.path.join() to access a file in a specific folder
        levels = []
        for name in args:
            good_lines = False
            try:
                good_lines, warning_signs = Level.check_level(name)
            except IOError:
                print('Error: cannot open', name)
            except LevelError as e:
                print("sadly, there were errors while loading level(s):")
                print(e)
            if good_lines:
                levels.append(Level(good_lines, warning_signs))
        print("{} level(s) were successfully added to the game".format(len(levels)))
        print("{} level(s) were not loaded because of errors".format(len(args)-len(levels)))
        if len(levels) > 0:
            wait("press [Enter] to start the game")
        else:
            sys.exit("no levels loaded - game can not start")
        return levels

    def __init__(self, source_lines, warning_signs):
        """liest den filenamen ein und erzeugt ein Level-Object"""
        self.source_lines = source_lines
        self.lines = []
        self.layout = []
        self.warning_signs = warning_signs       # schildnummer: schildtext
        self.monsters = []

        #self.sight_radius = 10

        y = 0
        for line in self.source_lines:
            good_line = ""
            x = 0
            for char in line:
                if char == "M":
                    self.monsters.append(Monster(x, y))
                    good_line += "."
                elif char == "B":
                    self.monsters.append(Boss(x,y))
                    good_line += "."
                elif char == "S":
                    self.monsters.append(Statue(x,y))
                    good_line += "."
                else:
                   good_line += char
                x += 1
            self.lines.append(good_line)
            y += 1

        print("level init: lines:")
        print(self.lines)
    
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
            new_pos = self.lines[y+dy][x+dx]
            if new_pos in "#TD":
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


def game(levels, playerx=1, playery=1, playerhp=50, playername="Rambo"):
    levels = levels
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
                status = "a sign says: " + level.warning_signs[player_pos]
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
    level_list = Level.check_levels("level1demo.txt","level2demo.txt") # load  level1demo.txt and level2demo.txt
    game(level_list, 1, 1, 50, "Rambo") # player "Rambo" starts at x1,x2 with 50 hitpoints
