#!/usr/bin/env python
# -*- cothing: utf-8 -*-                # nur wichtig für python version2
from __future__ import print_function  # nur wichtig für python version2
from __future__ import division        # nur wichtig für python version2
try:                                   # nur wichtig für python version2
    input = raw_input                  # nur wichtig für python version2
except NameError:                      # nur wichtig für python version2
    pass                               # nur wichtig für python version2

"""
name: pygamerogue
URL: https://github.com/horstjens/spielend-programmieren/tree/master/pyrogue
Author:  Horst JENS
Email: horstjens@gmail.com
Licence: gpl, see http://www.gnu.org/licenses/gpl.html
descr: a rogue game using python + pygame. graphics from dungeon crawl stone soup
and sound and graphics from battle of Wesnoth. please see readme.txt for license
details. 
"""

import pygame
import random
import os
import sys


def write(msg="pygame is cool", fontcolor=(255,0,255), fontsize=42, font=None):
    """returns pygame surface with text"""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext


def ask(question, screen,  image=None, x=-1, y=-1, center=True,  imagex=0, imagey=0):   # from pygame newsgroup
    """pygame version of input(). returns answer text string"""
    pygame.font.init()
    text = ""
    line = write(question)
    screen.blit(line, (x, y))
    pygame.display.flip()
    if x == -1:
        x = PygView.width // 3
    if y == -1:
        y = 0
    while True:
        pygame.time.wait(50) # wartet 50 millisekunden?
        #event = pygame.event.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type != pygame.KEYDOWN:
                continue
            elif event.key == pygame.K_BACKSPACE:
                text = text[0:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if text == "":
                    continue
                return text
            elif event.key == pygame.K_ESCAPE:
                continue
                #return "Dorftrottel"
            elif event.key <= 127:
                text += chr(event.key)
        line = write(question + ": " + text)
        screen.fill((0,0,0))
        screen.blit(line, (x, y))
        if image:
            if not center:
                screen.blit(image, (imagex, imagey))
            else:
                screen.blit(image, (PygView.width // 2 - image.get_rect().width // 2, 50))
        pygame.display.flip()


def display_textlines(lines, screen, color=(0,0,255), image=None, center=True, imagex=0, imagey=0):
    """pygame version of printing several lines"""
    offset = 0
    pygame.display.set_caption("Press ENTER to ext, UP / DOWN to scroll")
    lines.extend(("", "", "", "press [Enter] to continue"))
    while True:
        screen.fill((0, 0, 0))
        if image:
            if not center:
                screen.blit(image, (imagex, imagey))
            else:
                screen.blit(image, (PygView.width // 2 - image.get_rect().width //2,
                                    PygView.height // 2 - image.get_rect().height // 2))
        y = 0
        for textline in lines:
            line = write(textline, color, 24 )
            screen.blit(line,(20, offset + 14 * y ))
            y += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type != pygame.KEYDOWN:
                continue
            elif event.key == pygame.K_DOWN:
                offset -= 14
            elif event.key == pygame.K_UP:
                offset += 14
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                return
        pygame.display.flip()


def combat_round(m1, m2, level):
    """simulates one attack in a combat between monsters/player. Weapon and armor in the if/elif block 
       should be ordered by best effect to smallest effect.
       returns lines of text"""
    txt = []
    if m1.hitpoints > 0 and m2.hitpoints > 0:
        PygView.macesound.play()
        txt.append("combat: {} ({}, {} hp) swings at {} ({}, {} hp)".format(m1.name, type(m1).__name__, m1.hitpoints,
                                                                      m2.name, type(m2).__name__, m2.hitpoints))
        damage = m1.level
        if "sword" in m1.inventory and m1.inventory["sword"] > 0:
            damage = random.randint(damage, damage+3)
            weapon = "sword"
        elif "knife" in m1.inventory and m1.inventory["knife"] >0:
            damage = random.randint(damage+1, damage+2)
            weapon = "knife"
        else:
            damage = random.randint(damage, damage+1)
            weapon = "fist"
        txt.append("combat: {} attacks {} with {} for {} damage".format(
            m1.name, m2.name, weapon, damage))
        blocked_damage = 0
        if "armor" in m2.inventory:
            damage -= damage+1
            blocked_damage += 1
            txt.append("combat: armor of {} absorbs one point of damage".format(m2.name))
        if "shield" in m2.inventory:
            damage -= (damage-1)+1
            blocked_damage += 1
            txt.append("combat: shield of {} absorbs one point of damage".format(m2.name))
        fly_dx, fly_dy = 0, -30
        if m2.x > m1.x:
            fly_dx = 50
        elif m2.x < m1.x:
            fly_dx = -50
        if m2.y > m1.y:
            fly_dy = 50
        elif m2.y < m1.y:
            fly_dy = -50
        Flytext(m2.x, m2.y, "dmg: {}".format(damage), dx=fly_dx, dy=fly_dy)  # Text fly's away from opponent
        if blocked_damage > 0:
            Flytext(m2.x, m2.y+1, "blocked: {}".format(blocked_damage), (0,255,0), dx=fly_dx)
        if damage > 0:
            m2.hitpoints -= damage
            txt.append("combat: {} looses {} hitpoints ({} hp left)".format(m2.name, damage, m2.hitpoints))
            if m2.hitpoints < 1:
                # ---------- m2 is dead  ----------------
                exp = random.randint(7, 10)
                m1.xp += exp
                m1.kills += 1
                victim = type(m2).__name__    
                if victim in m1.killdict:
                    m1.killdict[victim] += 1
                else:
                    m1.killdict[victim] = 1
                txt.append("combat: {} has no hit points left, {} gains {} Xp".format(m2.name, m1.name, exp))
                line = m1.check_levelup()
                if line:
                    txt.append(line)
                if random.random() < 0.25:    # 25% Chance to drop edibles
                    level.loot.append(Loot(m2.x, m2.y, "meat"))
        else:
            txt.append("combat: {} is not harmed".format(m2.name))
    return txt


def load_sound(file):
    if not pygame.mixer:
        return NoSound()
    file = os.path.join("sounds", file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print('Warning, unable to load,', file)
    return NoSound()


def load_music(file):
    if not pygame.mixer:
        return NoSound()
    file = os.path.join("music", file)
    try:
        music = pygame.mixer.music.load(file)
        return music
    except pygame.error:
        print('Warning, unable to load,',file)
    return NoSound()


class NoSound(object):
    """dummy sound class so that the game works even if sound does not work"""
    def play(self):
        pass


class Spritesheet(object):
    """ from pygame.org
    #import spritesheet
    #...
    #ss = spritesheet.spriteshee('somespritesheet.png')
    ## Sprite is 16x16 pixels at location 0,0 in the file...
    #image = ss.image_at((0, 0, 16, 16))
    #images = []
    ## Load two images into an array, their transparent bit is (255, 255, 255)
    #images = ss.images_at((0, 0, 16, 16),(17, 0, 16,16), colorkey=(255, 255, 255))
    #...
    """
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(os.path.join("images", filename)).convert()
        except pygame.error:
            print('Unable to load spritesheet image:'), filename
            raise  # SystemExit, message
    # Load a specific image from a specific rectangle

    def image_at(self, rectangle, colorkey = None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        """Loads a strip of images and returns them as a list"""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class Monster(object):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        self.x = x
        self.y = y
        self.xp = xp
        self.kills = 0
        self.killdict = {}
        self.level = level   # each monster starts with level 1, may progress into higher levels
        self.rank = ""
        if hp == 0:
            self.hitpoints = random.randint(10, 20)
        else:
            self.hitpoints = hp
        if picture == "":
            self.picture = PygView.MONSTERPICTURE
        else:
            self.picture = picture
        self.name = random.choice(("Frank", "Dilbert", "Bob", "Alice"))
        self.strength = random.randint(1,10)
        self.dexterity = random.randint(1,10)
        self.intelligence = random.randint(1,10)
        self.inventory = {}
        for z in ["knife", "sword", "shield", "armor"]:
            if random.random() < 0.1:  # each Item has a 10% Chance 
                self.inventory[z] = 1

    def check_levelup(self, rank="nobody"):
        return ""

    def ai(self, player):
        """returns a random dx, dy: where the monster wants to go"""
        dirs = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
        return random.choice(dirs)   # return dx, xy


class Boss(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """a monster that moves toward the player"""
        Monster.__init__(self, x, y, xp, level, hp, picture)

    def ai(self, player):
        dx, dy = 0, 0
        if self.x > player.x:
            dx = -1
        elif self.x < player.x:
            dx = 1
        if self.y > player.y:
            dy = -1
        elif self.y < player.y:
            dy = 1
        return dx, dy


class Statue(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """a stationary monster that only defends it self"""
        Monster.__init__(self, x, y, xp, level, hp, picture)

    def ai(self, player):
        return 0, 0


class Goblin(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """example of a weak monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        #self.picture = random.choice((PygView.GOBLIN1, PygView.GOBLIN2, PygView.GOBLIN3))
        # self.strength = random.randint(1,6)
        # -- give something into inventory
        #self.inventory["goblin amulet"] = 1


class Wolf(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """another weak monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        # self.picture = random.choice((PygView.WOLF1, PygView.WOLF2, PygView.WOLF3))
        # self.strength = random.randint(3,4)
        # self.dexterity = random.randint(5,8)
        # self.inventory["fangs"] = 1 # modify combat_round and code damage for "fangs"


class EliteWarrior(Boss):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """example for a boss monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        # self.hitpoints = 100
        # self.picture = random.choice((PygView.WARRIOR1, PygView.WARRIOR2, PygView.WARRIOR3))
        # self.strength = random.randint(12,24)   # more strength
        # self.inventory["sword"] = 1             # 100% change to start with good equipment
        # self.inventory["shield"] = 1


class Golem(Boss):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """example for a boss monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        # self.picture = random.choice((PygView.GOLEM1, PygView.GOLEM2, PygView.GOLEM3))
        # self.strength = random.randint(20,30)   # overwrite Monster() strength


class Player(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        Monster.__init__(self, x, y, xp, level, hp, picture)
        self.name = "Player"
        self.rank = "unworthy"
        self.inventory = {}
        self.z = 0
        self.keys = []
        self.druid_visited = False
        self.hunger = 0
        self.mana = 0
        if hp == 0:
            self.hitpoints = random.randint(5,10)
        else:
            self.hitpoints = hp
        if picture == "":
           self.picture = PygView.PLAYERPICTURE
        else:
            self.picture = picture

    def levelup(self, rank="Nobody"):
        self.level += 1
        self.hitpoints += self.level* 2 + random.randint(1,6)
        self.rank = rank

    def check_levelup(self):
        if self.xp >= 100 and self.level == 1:
            self.levelup("page")  # level wird 2
        elif self.xp >= 200 and self.level == 2:
            self.levelup("squire")
        elif self.xp >= 400 and self.level == 3:
            self.levelup("knight")
        else:
            return ""  # add your own code here
        return "{} gains Level {}: {}".format(self.name, self.level, self.rank)

    def ai(self):
        return (0,0)

    def show_inventory(self):
        """show inventory, return lines of text"""
        lines = ["you carry this stuff with you:"]
        if len(self.inventory) == 0:
            lines.append("you carry nothing")
        else:
            lines.append("amount, description")
            lines.append("===================")
            for thing in self.inventory:
                lines.append(str(self.inventory[thing]) + ".........." + str(thing))
        return lines

    def take(self, item):
        """increase amount of a item in the inventory"""
        if item in self.inventory:
            self.inventory[item] += 1
        else:
            self.inventory[item] = 1
        
        
class Block(object):
    def __init__(self):
        self.visible = True
        self.bloody = False


class Floor(Block):
    def __init__(self):
        Block.__init__(self)
        self.picture = random.choice((PygView.FLOOR, PygView.FLOOR1))


class Wall(Block):
    def __init__(self):
        Block.__init__(self)
        self.picture = random.choice((PygView.WALL, PygView.WALL1, PygView.WALL2))


class Stair(Block):
    def __init__(self, direction):
        Block.__init__(self)
        if direction == "down":
            self.down = True
            self.picture = PygView.STAIRDOWN
        else:
            self.down = False
            self.picture = pygame.Surface((32, 32))
            self.picture.blit(PygView.FLOOR, (0, 0))  # blit stairup over the picture of floor, for better looks
            self.picture.blit(PygView.STAIRUP, (0, 0))
            self.picture.convert_alpha()
        self.target = (0, 0, 0) # x,y,z


class Item(object):
    def __init__(self, x, y):
        """a moveable thing laying on the floor in the dungeon
           it can also be carried around by the player"""
        self.x = x
        self.y = y
        self.visible = True
        self.hitpoints = 1
        self.picture = PygView.LOOT  # the subclass will overwrite it in most cases
        self.carried = False         # in someone's inventory?


class Sign(Item):
    def __init__(self, x, y, char):
        """a warning sign giving the player hints. see readme_leveldesign.txt for information how to create signs"""
        Item.__init__(self, x, y)
        self.picture = PygView.SIGN
        self.char = char    # number from level source code
        self.text = ""      # the long text of the sign


class Trap(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.level = random.randint(1, 5)
        self.hitpoints = self.level * 2
        self.picture = PygView.TRAP


class Key(Item):
    def __init__(self, x, y, color="dull"):
        Item.__init__(self, x, y)
        self.color = color
        self.picture = PygView.KEY


class Door(Item):
    def __init__(self, x, y, color="dull"):
        Item.__init__(self, x, y)
        self.locked = True
        self.closed = True
        self.picture = PygView.DOOR
        self.color = color


class Loot(Item):
    def __init__(self, x, y, descr=""):
        Item.__init__(self, x, y)
        if descr == "":
            self.text = random.choice(["trash", "meat", "coin", "knife", "rags",
                                       "spoon", "stone", "sword", "armor", "gem",
                                       "healing potion", "shield", "bread"])
        else:
            self.text = descr


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class LevelError(Error):
    """a specific Exception subclass handling level design errors"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Level(object):
    """a game level"""

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
                                     "char {} is not in Level.LEGEND".format(char) +
                                     "\n allowed Symbols are numbers for warning signs and:\n" +
                                     str(Level.LEGEND.keys()))
                x += 1
            good_lines.append(line)
            line_number += 1
        if not has_stairs_up:
            raise LevelError("{}: level has no stair up sign (<)".format(
                             filename))
        return good_lines, warning_signs

    @staticmethod
    def check_levels(list_of_levelsourcefilenames):
        """load level file names (comma separated) from disk,
           display errors and return list of error free Level() objects"""
        # args are the level names, like "level1.txt". Use os.path.join() to access a file in a specific folder
        levels = []
        for name in list_of_levelsourcefilenames:
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
        fails = len(list_of_levelsourcefilenames) - len(levels)
        print("{} level(s) were successfully added to the game".format(len(levels)))
        if len(levels) < 1:
            sys.exit("no levels loaded - game can not start")
        elif fails > 0:
            print("{} level(s) were not loaded because of errors".format(fails))
            wait("press [Enter] to start the game anyway")
        return levels

    def __init__(self, lines, signsdict):
        """create a new Level object, prepared from check_level"""
        self.lines = lines
        self.layout = {}                 # lines of non-movable stuff
        self.signsdict = signsdict       # {"number": "text"}
        self.monsters = []
        self.signs = []
        self.traps = []
        self.doors = []
        self.loot = []
        self.keys = []
        self.width = 0
        self.depth = 0
        #self.sichtweite = 10
        #with open(dateiname) as f:
        y = 0
        for line in self.lines:
            x = 0
            for char in line:
                self.layout[(x, y)] = Floor()  # if not overwritten later by a Wall() object etc., each tile is a Floor()
                if char == "M":
                    self.monsters.append(random.choice([Goblin(x, y), Wolf(x,y)]))  # insert your own Monsters here
                elif char == "B":
                    self.monsters.append(random.choice([EliteWarrior(x, y), Golem(x,y)]))  # insert your own boss monsters here
                elif char == "S":
                    self.monsters.append(Statue(x, y))  # stationary Monster
                elif char == "T":
                    self.traps.append(Trap(x, y))       # object on top of Floor()
                elif char == "D":
                    self.doors.append(Door(x, y))       # object on top of Floor()
                elif char == "L":
                    self.loot.append(Loot(x, y))        # object on top of Floor()
                elif char == "k":
                    self.keys.append(Key(x, y))         # object on top of Floor()
                elif char == "<":
                    self.layout[(x, y)] = Stair("up")     # overwrite Floor() with Stair()
                elif char == ">":
                    self.layout[(x, y)] = Stair("down")
                elif char == ".":
                    pass  # self.layout[(x,y)] = Floor()  # do nothing, as this tile already is a Floor()
                elif char in "123456789":
                    self.signs.append(Sign(x, y, char))   # the char is the key of self.signsdict
                elif char == "#":
                    self.layout[(x,y)] = Wall()           # overwrite Wall() instead of Floor()
                x += 1
            y += 1
            self.width = max(self.width, x)
            self.depth = max(self.depth, y)

        # now it is possible to assign the values from signdict to the signs
        for sign in self.signs:
            sign.text = self.signsdict[sign.char]

    def update(self):
        """only keep monster, traps etc. with hit points. only keep items not carried by player"""
        self.monsters = [m for m in self.monsters if m.hitpoints > 0]
        self.traps = [t for t in self.traps if t.hitpoints > 0]
        self.keys = [k for k in self.keys if not k.carried]
        self.loot = [i for i in self.loot if not i.carried]
        self.doors = [d for d in self.doors if d.closed]  # opened doors disappear

    def is_monster(self, x, y):
        """testing if a monster lurks at a coordinate """
        for monster in self.monsters:
            if monster.hitpoints > 0 and monster.x == x and monster.y == y:
                return monster
        return False

## this sprite class was not useable because Monsters were created to soon, by Level.__init__, causing problems
#class Healthbar(pygame.sprite.Sprite):
#    def __init__(self, boss):
#        """a healthbar hovering over a monster"""
#        self._layer = 6
#        self.boss = boss
#        pygame.sprite.Sprite.__init__(self, self.groups)
#        self.image = pygame.Surface((32,4))
#        self.rect = self.image.get_rect()
#        self.update(0)
#
#    def update(self, seconds):
#        self.x, self.y = PygView.scrollx + self.boss.x * 32, PygView.scrolly + self.boss.y * 32
#        pygame.draw.rect(self.image, (255,255,255), (0,0,32,4))
#        pygame.draw.rect(self.image, (255,0,0    ), (1,1,31,3))
#        pygame.draw.rect(self.image, (0,0,255    ), (1,1,max(31, boss.hitpoints),3)) # zeigt maximal 31 hitpoints an
#        self.image.convert()
#        self.rect.center = (PygView.scrollx + self.boss.x * 32, PygView.scrolly + self.boss.y * 32)
#        if self.boss.hitpoints < 1:
#            self.kill()


class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", rgb=(255,0,0), blockxy = True,
                  dx=0, dy=-50, duration=2, acceleration_factor = 0.96 ):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = rgb[0], rgb[1], rgb[2]
        self.dx = dx
        self.dy = dy
        if blockxy:
            self.x, self.y = PygView.scrollx + x * 32, PygView.scrolly + y * 32
        else:
            self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster. 
        self.image = write(self.text, (self.r, self.g, self.b), 22) # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0

    def update(self, seconds):
        self.y += self.dy * seconds
        self.x += self.dx * seconds
        self.dy *= self.acc  # slower and slower
        self.dx *= self.acc
        self.rect.center = (self.x, self.y)
        self.time += seconds
        if self.time > self.duration:
            self.kill()      # remove Sprite from screen and from groups


class PygView(object):
    scrollx = 0  # class variables, can be read from everywhere
    scrolly = 0

    def __init__(self, level_sourcefilenames, width=640, height=400, x=1, y=1, xp=0, level=1, hp=50, fullscreen=False):
        if fullscreen:
            winstyle = pygame.FULLSCREEN
        else:
            winstyle = 0
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.init()
        # ----------- pictureschirm einrichten --------
        PygView.width = width   #
        PygView.height = height
        #self.screenrect = pygame.Rect(0, 0, self.width, self.height)
        #bestdepth = pygame.display.mode_ok(self.screenrect.size, winstyle, 32)
        #self.screen = pygame.display.set_mode(self.screenrect.size, winstyle, bestdepth)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.fps = 30  # frames per second
        pygame.display.set_caption("Press ESC to quit")

        # ------- load Resources as class attirbutes (global access) 
        # ----- all pictures are in folder "images" ---------
        PygView.WALLS = Spritesheet("wall.png")     # 32 x 39
        PygView.FLOORS = Spritesheet("floor.png")   # 32 x 29
        PygView.FIGUREN = Spritesheet("player-keanu.png") # 32 x 57
        PygView.GUI = Spritesheet("gui.png")        # 32 x 17
        PygView.FEAT = Spritesheet("feat-keanu.png")      # 32 x 16
        PygView.MAIN = Spritesheet("main-keanu.png")      # 32 x 29
        # ------ get a single picture using image_at(x upperleft corner, y upperleft corner, width, height)
        PygView.WALL = PygView.WALLS.image_at((0, 0, 34, 32))  
        PygView.WALL1 = PygView.WALLS.image_at((34, 0, 32, 32))
        PygView.WALL2 = PygView.WALLS.image_at((68, 0, 32, 32))
        # PygView.SIGN  = PygView.GUI.image_at((32*6,0,32,32))
        PygView.FLOOR = PygView.FLOORS.image_at((160, 32*2, 32, 32))
        PygView.FLOOR1 = PygView.FLOORS.image_at((192, 160, 32, 32))
        PygView.TRAP = PygView.FEAT.image_at((30, 128, 32, 32), (0, 0, 0))
        PygView.PLAYERPICTURE = PygView.FIGUREN.image_at((111, 1215, 32, 32), (0, 0, 0))
        PygView.STAIRDOWN = PygView.FEAT.image_at((32*4, 32*5, 32, 32))
        PygView.STAIRUP = PygView.FEAT.image_at((32*5, 32*5, 32, 32), (0, 0, 0))
        PygView.MONSTERPICTURE = PygView.FIGUREN.image_at((0, 0, 32, 32), (0, 0, 0))
        PygView.DOOR = PygView.FEAT.image_at((32*2, 32, 32, 32))
        PygView.LOOT = PygView.MAIN.image_at((155, 672, 32, 32), (0, 0, 0))
        PygView.KEY = PygView.FIGUREN.image_at((54, 1682, 32, 32), (0, 0, 0))
        PygView.SIGN = PygView.GUI.image_at((197, 0, 32, 32), (0, 0, 0))
        # ------- portraits -----
        PygView.TRADER = pygame.image.load(os.path.join("images", "hakim.png"))
        PygView.DRUID = pygame.image.load(os.path.join("images", "druid.png"))
        PygView.GAMEOVER = pygame.image.load(os.path.join("images", "gameover.jpg"))
        # --------- create player instance --------------
        self.player = Player(x, y, xp, level, hp)
        # ---- ask player to enter his name --------
        self.player.name = ask("Your name [Enter]? >>", self.screen, PygView.DRUID )
        self.player.name = self.player.name[0].upper() + self.player.name[1:].lower()
        self.levels = Level.check_levels(level_sourcefilenames)  # checked by Level.check_levels()
        self.status = [""]
        self.level = self.levels[0]
        self.seconds = 0
        self.turns = 0
        self.mo1 = 0  # amount of monsters in this level , will be auto-calculated
        self.mo2 = 0  # amount of monster in all levels, will be auto-calculated
        self.level = self.levels[self.player.z]   # player.z = 0 is the first level
        self.background = pygame.Surface((self.level.width*32, self.level.depth*32))
        # ------------ Sprite Groups -----------
        self.flytextgroup = pygame.sprite.Group()
        #self.bargroup = pygame.sprite.Group()
        self.allgroup = pygame.sprite.LayeredUpdates()  # sprite group with layers
        # --------- attach Sprites to Sprite groups ---
        Flytext.groups = self.flytextgroup, self.allgroup
        #Healthbar.groups = self.bargroup, self.allgroup
        # ---------- sound and music ----------
        # sounds are in folder "sounds", music is in folder "music"
        PygView.bowsound = load_sound("bow.ogg")
        PygView.macesound = load_sound("mace.wav")
        load_music("the_king_is_dead.ogg")  # music loop
        #pygame.mixer.music.play()  # start background music
        #pygame.mixer.music.stop()
        #pygame.mixer.music.pause()
        #pygame.mixer.music.unpause()
        #PygView.macesound.play()   # soundeffect start
        # -------- helptext ------
        self.hilftextlines = []
        self.hilftextlines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self.hilftextlines.append("commands:")
        self.hilftextlines.append("[w] [a] [s] [d]......move player up/left/down/right")
        self.hilftextlines.append("[<] oder [>].........climb stair up/down")
        self.hilftextlines.append("[i]..................show inventory")
        self.hilftextlines.append("[Esc]................exit game")
        self.hilftextlines.append("[h]..................show help, (this text)")
        self.hilftextlines.append("[q]..................quaff healing potion")
        self.hilftextlines.append("[e]..................eat")
        self.hilftextlines.append("[Enter]..............wait an turn (monsters move!)")
        self.hilftextlines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    def paint(self):
        """paint level and GUI"""
        for y in range(self.level.depth):
            for x in range(self.level.width):
                self.background.blit(self.level.layout[(x,y)].picture, (x * 32, y * 32))
                for sign in [s for s in self.level.signs if s.x == x and s.y ==y]:
                    self.background.blit(sign.picture, (x * 32, y * 32))
                for trap in [t for t in self.level.traps if t.x == x and t.y == y and t.hitpoints >0
                             and t.visible]:
                    self.background.blit(trap.picture, (x * 32, y * 32))
                for door in [d for d in self.level.doors if d.x == x and d.y == y and d.closed]:
                    self.background.blit(door.picture, (x * 32, y * 32))
                for loot in [l for l in self.level.loot if l.x == x and l.y == y and not l.carried]:
                    self.background.blit(loot.picture, (x * 32, y * 32))
                for key in [k for k in self.level.keys if k.x == x and k.y == y and not k.carried]:
                    self.background.blit(key.picture, (x * 32, y * 32))
        # Scrolling: paint the player in the middle of the screen # TODO: improve gui layout
        PygView.scrollx = self.width / 2 - self.player.x * 32
        PygView.scrolly = self.height / 2 - self.player.y * 32
        self.screen.fill((0, 0, 0))  # make all black
        self.screen.blit(self.background, (PygView.scrollx, PygView.scrolly))
        # ----- GUI for text messages below playing area
        gui_height = 100
        # ---- paint monsters ---
        for monster in self.level.monsters:
            self.screen.blit(monster.picture, (PygView.scrollx + monster.x * 32, PygView.scrolly + monster.y * 32))
            # ------- draw healthbar  ----------
            # shows a maximum of 31 hitpoints as full green health-bar, with red from the right if less healthy
            #pygame.draw.rect(self.screen, (255,255,255), (PygView.scrollx + monster.x * 32,
            #    PygView.scrolly + monster.y * 32 - 15,32,4))
            pygame.draw.rect(self.screen, (255, 0, 0), (PygView.scrollx + monster.x * 32,
                             PygView.scrolly + monster.y * 32 - 15, 32, 5))  
            pygame.draw.rect(self.screen, (0, 255, 0), (PygView.scrollx + monster.x * 32,
                             PygView.scrolly + monster.y * 32 - 15, min(32, monster.hitpoints), 5))
        # ---- paint player -----
        self.screen.blit(self.player.picture, (PygView.scrollx + self.player.x * 32, PygView.scrolly +self.player.y*32))
        # ---- clean text are by painting it black ---
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.height - gui_height, self.width, gui_height))
        # ---- player status ----
        line = write("{}: hp:{} keys:{}".format(self.player.name,
                     self.player.hitpoints, len(self.player.keys)), (0, 255, 0), 24)  # fontsize = 24
        self.screen.blit(line, (self.width / 2, self.height - gui_height))
        line = write("turn:{} x:{} y:{} dungeon-level:{}".format(self.turns, self.player.x, self.player.y,
                     self.player.z),   (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - gui_height + 16))
        line = write("Exp: {} Level:{}".format(self.player.xp, self.player.level), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - gui_height + 16*2))
        line = write("# Monsters in level: {} in dungeon: {}".format(self.mo1, self.mo2), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - gui_height + 16*3))
        line = write("Hunger: {}".format(self.player.hunger), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - gui_height + 16*4))
        # ---- paint status messages ----- start 200 pixel from screen bottom
        for number in range(-7, 0, 1):
            if self.status[number][:6] == "combat:":
                r, g, b = 255, 0, 255
            else:
                r, g, b = 0, 0, 255
            line = write("{}".format(self.status[number]), (r, g, b+30*number), 24)  # becomes more and more white
            self.screen.blit(line, (0, self.height + number * 14))

    def count_monsters(self):
        self.mo1 = len(self.level.monsters)
        self.mo2 = sum([len(l.monsters) for l in self.levels])

    def run(self):
        """The mainloop---------------------------------------------------"""
        self.clock = pygame.time.Clock() 
        running = True
        self.count_monsters()
        self.status = ["The game begins!", "You enter the dungeon...", "Hint: goto x:5 y:5",
                       "Hint: avoid traps", "Hint: Plunder!", "press ? for help", "good luck!"]
        while running and self.player.hitpoints > 0:
            self.seconds = self.clock.tick(self.fps)/1000.0  # seconds since last frame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    # -------- a key was pressed and released ---------
                    where = self.level.layout[(self.player.x, self.player.y)]
                    self.status.append("Turn {}".format(self.turns))
                    self.turns += 1
                    if self.player.mana < 32:
                        self.player.mana += 1
                    self.player.hunger += 1
                    if self.player.hunger > 100:
                        self.player.hitpoints -= 1
                        Flytext(self.player.x, self.player.y, "Hunger: dmg 1" )
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    self.player.dx = 0
                    self.player.dy = 0
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.dy -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.dy += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.dx -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.dx += 1
                    elif event.key == pygame.K_QUESTION or event.key == pygame.K_h:
                        display_textlines(self.hilftextlines, self.screen)
                        continue
                    elif event.key == pygame.K_PERIOD or event.key == pygame.K_RETURN:
                        pass      # player is idle for one turn
                    elif event.key == pygame.K_i:
                        # ----------- show inventory (inventory) -----------------
                        display_textlines(self.player.show_inventory(), self.screen, image= PygView.TRADER)
                        continue
                    elif event.key == pygame.K_LESS or event.key == pygame.K_GREATER:     # < or > 
                        if type(where).__name__ == "Stair":
                            if not where.down and self.player.z == 0:
                                lines=["Game OVer",
                                       "you leave the dungeon and return to the surface..",
                                       "...alive!"]
                                display_textlines(lines,self.screen, (255, 255, 255) )
                                running = False
                                break
                            elif not where.down:
                                self.player.z -= 1
                            else:
                                self.player.z += 1
                            # ---------- change dungeon level -------------
                            self.level = self.levels[self.player.z]    
                            self.background = pygame.Surface((self.level.width*32, self.level.depth*32))
                        else:
                            self.status.append("{}: you need to find a stair to climb up/down using [<],[>]".format(
                                               self.turns))
                            break
                    elif event.key == pygame.K_q:       # -----(q)uaff potion --------- healing potion ------------
                            if "healing potion" in self.player.inventory and self.player.inventory["healing potion"]>0:
                                self.player.inventory["healing potion"] -= 1
                                effect = random.randint(2, 5)
                                self.player.hitpoints += effect
                                self.status.append("{}: You drink the healing potion und gain {} hitpoints".format(
                                                   self.turns, effect))
                                Flytext(self.player.x, self.player.y,"gulp, gulp, gulp: +{} hp".format(effect),
                                        (0, 0, 255))
                            else:
                                self.status.append("{}: You have no healing potion. Gather more loot!".format(
                                                   self.turns))
                    elif event.key == pygame.K_e:
                        food = [i for i in self.player.inventory if i == "bread" or i == "meat"]
                        if len(food) > 0:
                            self.player.inventory[food[0]]-=1
                            Flytext(self.player.x, self.player.y, "Yummy {}".format(food[0]))
                            self.player.hunger -= random.randint(5, 30)
                        else:
                            self.status.append("You have nothing edible in your inventory. Fight and find loot!")
                    # --------------- new location ----------
                    # whereto: Block (Floor, Wall, Stair)
                    whereto = self.level.layout[(self.player.x+self.player.dx, self.player.y+self.player.dy)]
                    monster = self.level.is_monster(self.player.x+self.player.dx, self.player.y+self.player.dy)
                    if monster:     # ---- combat: player runs into monster -----
                        self.status.extend(combat_round(self.player, monster, self.level))
                        self.status.extend(combat_round(monster, self.player, self.level))
                        self.player.dx, self.player.dy = 0, 0
                        self.count_monsters()
                    # ----- testing if player runs into wall
                    elif type(whereto).__name__ == "Wall":         # in die Wand gelaufen?
                        self.status.append("{}: Please don't run into walls!".format(self.turns))
                        self.player.hitpoints -= 1
                        Flytext(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")
                        self.player.dx, self.player.dy = 0,0
                    # ----- testing if player runs into door
                    for door in [d for d in self.level.doors if d.x == self.player.x+self.player.dx and
                                 d.y == self.player.y + self.player.dy and d.closed]:
                        if len(self.player.keys) > 0:
                            mykey = self.player.keys.pop()
                            door.closed = False  # unlocked !
                            self.status.append("{}: door unlocked! 1 key used up)".format(self.turns))
                        else:
                            self.player.dx, self.player.dy = 0,0
                            self.status.append("{}: Ouch! You bumb into a door".format(self.turns))
                            self.player.hitpoints -= 1
                            Flytext(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")
                    # ----------------- Finally the player is arrived at a new position --------
                    self.player.x += self.player.dx
                    self.player.y += self.player.dy
                    where = self.level.layout[(self.player.x, self.player.y)]               # where am i now
                    # ------------- special Story -------------------
                    #      ---- Story 1: visit the druids
                    if self.player.x == 5 and self.player.y == 5 and self.player.z == 0 and not self.player.druid_visited:
                        # at position x5, y5 in first level (z0)
                        lines = ["I welcome you, wandering hero!",
                                 "Please liberate us",
                                 "the peaceful druids",
                                 "from those dangerous, evil monsters.",
                                 "Slay them all!"]
                        display_textlines(lines, self.screen, (0,255,255), PygView.DRUID)
                        self.player.druid_visited = True
                    #      ----- Story 2:  all monsters killed, druid mission complete
                    if self.mo2 == 0 and self.player.druid_visited:
                        lines = ["Congratulation, o hero",
                                 "You have liberated us druids",
                                 "and slayed all the evil monsters",
                                 "Thanks from us all, o fantastic {}!".format(self.player.name)]
                        display_textlines(lines, self.screen, (0,255,255), PygView.DRUID)
                        self.player.inventory["reward: half a kingdom"] = 1
                        self.player.inventory["reward: friendship of the druids"] = 1
                        running = False
                    #    ------- Story 3: Player destroys statue and goes to oosition of statue (18,14) in level2 (z=1)
                    if self.player.z == 1 and self.player.x == 14 and self.player.y == 18:
                        # if player can reach this place he defeated the statue
                        Flytext(self.player.x, self.player.y, "uh-oh...what happens now?", (255, 255, 255))
                        # replace walls with floor so that imprisoned monsters can hunt player
                        self.level.layout[(7, 17)] = Floor()  # replace the wall on this position with a floor
                        self.level.layout[(7, 18)] = Floor()
                        self.level.layout[(7, 19)] = Floor()
                        self.level.layout[(23, 17)] = Floor()
                        self.level.layout[(23, 18)] = Floor()
                        self.level.layout[(23, 19)] = Floor()
                        self.level.layout[(14, 20)] = Floor()
                        self.level.layout[(14, 11)] = Floor()
                        # place a new Monster at the stairs x:1 y:1 in level 2 (z=1)
                        self.level.monsters.append(Statue(1, 1))
                    # ------------- warning signs ----------
                    for sign in self.level.signs:
                        if sign.x == self.player.x and sign.y == self.player.y:
                            self.status.append("{}: a sign says: {}".format(self.turns, sign.text))
                    if type(where).__name__ == "Stair":
                        if where.down:
                            self.status.append("{}: stair down: press [>] to climb down".format(self.turns))
                        else:
                            self.status.append("{}: stair up: press [<] to climb up".format(self.turns))
                    # --------- is there a trap ? --------------
                    for trap in self.level.traps:
                        if trap.x == self.player.x and trap.y == self.player.y:
                            damage = random.randint(1, 4)
                            self.status.append("{}: Ouch, that hurts! A trap, {} damage!".format(self.turns, damage))
                            self.player.hitpoints -= damage
                            Flytext(self.player.x, self.player.y, "A trap! Dmg: {}".format(damage))
                            if random.random() < 0.5:             # 50% Chance # Falle verschwunden?
                                self.status.append("{}: trap destroyed!".format(self.turns))
                                trap.hitpoints = 0
                    # --------- is there a key ? -------------
                    for key in self.level.keys:
                        if key.x == self.player.x and key.y == self.player.y:
                            key.carried = True
                            self.player.keys.append(key)
                            self.status.append("{} key found".format(self.turns))
                            Flytext(self.player.x, self.player.y, "a key", (0, 200, 0))
                    # --------- is there loot ? --------------
                    for i in self.level.loot:
                        if i.x == self.player.x and i.y == self.player.y and not i.carried:
                            i.carried = True
                            if i.text in self.player.inventory:
                                self.player.inventory[i.text] += 1
                            else:
                                self.player.inventory[i.text] = 1
                            self.status.append("{} Loot found! ({})".format(self.turns, i.text))
                            Flytext(self.player.x, self.player.y, i.text + " found!", (0, 200, 0))
                    # ------------------- level update (remove old traps, doors etc.) ------
                    self.level.update()                                             # tote monster löschen
                    # -------------- move monsters ------------------
                    for monster in self.level.monsters:
                        x, y = monster.x, monster.y
                        dx, dy = monster.ai(self.player)
                        if self.level.is_monster(x + dx, y + dy):
                            continue  # monster should not run into another monster
                        if x+dx == self.player.x and y+dy == self.player.y:
                            self.status.extend(combat_round(monster, self.player, self.level))
                            self.status.extend(combat_round(self.player, monster, self.level))
                            self.count_monsters()
                            continue     # monster should not run into player, it should fight him
                        whereto = self.level.layout[(x+dx, y+dy)]
                        if type(whereto).__name__ == "Wall":
                            continue     # monster should not run into wall. waiting instead
                        if len([t for t in self.level.traps if t.x == x + dx and t.y == y + dy]) > 0:
                            continue     # monster should not run into trap. waiting instead
                        if len([d for d in self.level.doors if d.x == x + dx and d.y == y + dy]) > 0:
                            continue  # monster should not run into door. waiting instead
                        monster.x += dx
                        monster.y += dy
            #pressedkeys = pygame.key.get_pressed()
            # if pygame.K_x in pressedkeys:
            #      print("x key is pressed")
            # ------------ redraw screen, blit the sprites --------------
            pygame.display.set_caption("  press Esc to quit. Fps: %.2f (%i x %i)"%(
                                       self.clock.get_fps(), self.width, self.height))
            self.paint() # paint this level
            #  ------- draw the sprites ------
            #self.allgroup.clear(self.screen, self.background)
            self.allgroup.update(self.seconds)
            self.allgroup.draw(self.screen)
            # ---- proceed to next pygame screen
            pygame.display.flip()
        # --------------------------- Game Over ----------------------
        lines = []
        lines.append("**** Game Over *******")
        lines.append("Hitpoints: {}".format(self.player.hitpoints))
        lines.append("Level: {}".format(self.player.level))
        lines.append("Rank: {}".format(self.player.rank))
        lines.append("Victories: {}".format(self.player.kills))
        if self.player.hitpoints < 1:
            lines.append("You are dead.")
        else:
            lines.append("You survived!")
        lines.append("-------------Your inventory:----------")
        for line in self.player.show_inventory():
            lines.append(line)
        lines.append("------------ You killed: ------------")
        for v in self.player.killdict:
            lines.append("{} {}".format(self.player.killdict[v], v))
        display_textlines(lines, self.screen,  (255,255,255), PygView.GAMEOVER)
        # ------------ game over -----------------
        pygame.mixer.music.stop()
        for line in lines:
            print(line)
        pygame.quit()    # end  pygame  # TODO: game sometimes hangs here. PYthon3+pygame bug?
        sys.exit()      # end python


if __name__ == '__main__':
    level_sourcefilenames = ["level1demo.txt", "level2demo.txt"]  # add your own level files here. use os.path.join() for other folders
    # 1600 x 1000 pixel, Player start at x=1, y=1, in level 0 (the first level) with 0 xp, has level 1 and 50 hit points
    PygView(level_sourcefilenames, 1600, 1000, 1, 1, 0, 1, 50).run()
