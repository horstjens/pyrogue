#!/usr/bin/env python
# -*- coding: utf-8 -*-                # only necessary for python version2
from __future__ import print_function  # only necessary for python version2
from __future__ import division        # only necessary for python version2
try:                                   # only necessary for python version2
    input = raw_input                  # only necessary for python version2
except NameError:                      # only necessary for python version2
    pass                               # only necessary for python version2

"""
name:        pygamerogue
URL:         https://github.com/horstjens/pyrogue
Author:      Horst JENS
Email:       horstjens@gmail.com
Licence:     gpl, see http://www.gnu.org/licenses/gpl.html
Description: a rogue game using python + pygame. graphics from dungeon crawl stone soup
             and sound and graphics from battle of Wesnoth. please see readme.txt and
             LICENSE for license details.
"""

import pygame
import random
import os
import sys


def re_roll(sides=6, number=1):
    """roll 'number' of die and re-roll if the highest side was rolled.
       A six sided dice if rolling a 6 count as 5 and can roll again
       this makes possible very high numbers with a very low chance"""
    dsum = 0  # sum is already a python keyword
    for _ in range(number):
        while True:
            roll = random.randint(1, sides)
            if roll < sides:
                dsum += roll
                break
            dsum += roll-1
    return dsum


def write(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
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
        pygame.time.wait(50)  # waits 50 millisekunden?
        # event = pygame.event.poll()
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
                continue  # return "village idiot"
            elif event.key <= 127:
                text += chr(event.key)
        line = write(question + ": " + text)
        screen.fill((0, 0, 0))
        screen.blit(line, (x, y))
        if image:
            if not center:
                screen.blit(image, (imagex, imagey))
            else:
                screen.blit(image, (PygView.width // 2 - image.get_rect().width // 2, 50))
        pygame.display.flip()


def display_textlines(lines, screen, color=(0, 0, 255), image=None, center=True, imagex=0, imagey=0):
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
            line = write(textline, color, 24)
            screen.blit(line, (20, offset + 14 * y))
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


def combat_round(attacker, defender, level):
    """simulates one attack in a combat between monsters/player. Weapon and armor in the if/elif block 
       should be ordered by best effect to smallest effect.
       returns lines of text"""
    txt = []
    attackername = type(attacker).__name__
    defendername = type(defender).__name__
    if attacker.hitpoints > 0 and defender.hitpoints > 0:
        PygView.macesound.play()
        txt.append("combat: {} ({} hp) swings at {} ({} hp)".format( attackername,
                   attacker.hitpoints, defendername, defender.hitpoints))
        #          stats: [0]:min-damage,
        #                 [1]:max-damage,
        #                 [2]:chance_for_double_damage,
        #                 [3]:chance_for_destroy_weapon
        stats = {"sword": (2, 5, 0.1,  0.01),
                 "knife": (2, 3, 0.05, 0.01),
                 "fangs": (1, 3, 0.15, 0.00),
                 "fist":  (1, 2, 0.01, 0.00)}
        # order weapons here from best to worst. fist must be last item in list
        for weapon in ["sword", "knife", "fangs", "fist"]:
            if weapon in attacker.inventory:
                damage = random.randint(stats[weapon][0], stats[weapon][1])
                #if weapon == "fangs":
                #    damage = random.choice((0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4, 5))  # special damage for wolf, can be zero
                #  chance for double damage?
                if random.random() < stats[weapon][2]:
                    txt.append("{} makes double damage!".format(weapon))
                    damage *= 2
                # chance to destroy weapon? note that fist and fangs can not be destroyed (chance=0.00%)
                if random.random() < stats[weapon][3]:
                    txt.append("{} is destroyed!".format(weapon))
                    attacker.inventory[weapon] -= 1  # remove weapon
                    attacker.update_inventory()      # remove entrys with 0
                damage += attacker.level
                txt.append("{} attacks {} with {} for {} raw damage".format(
                           attackername, defendername, weapon, damage))
                break
        blocked_damage = 0
        #           stats: [0]: block_chance,
        #                  [1]: block_value,
        #                  [2]: chance_to_destroy
        stats = {"armor":  (0.75, 1, 0.01),
                 "shield": (0.5,  2, 0.04),
                 "helm":   (0.3,  1, 0.01)}
        for piece in ["armor", "shield", "helm"]:
            if piece in defender.inventory:
                # chance to block?
                if random.random() < stats[piece][0]:
                    blocked_damage += stats[piece][1]
                    txt.append("{} of {} blocks {} damage".format(piece, defendername, stats[piece][1]))
                # chance to destroy armor?
                if random.random() < stats[piece][2]:
                    txt.append("{} is shattered!")
                    defender.inventory[piece] -= 1  # remove armor piece
                    defender.update_inventory()

        damage -= blocked_damage
        damage = max(0, damage)  # damage can not be negative
        fly_dx, fly_dy = 0, -30
        if defender.x > attacker.x:
            fly_dx = 50
        elif defender.x < attacker.x:
            fly_dx = -50
        if defender.y > attacker.y:
            fly_dy = 50
        elif defender.y < attacker.y:
            fly_dy = -50
        Flytext(defender.x, defender.y, "dmg: {}".format(damage), dx=fly_dx, dy=fly_dy)  # Text fly's away from opponent
        if blocked_damage > 0:
            Flytext(defender.x, defender.y+1, "blocked: {}".format(blocked_damage), (0, 255, 0), dx=fly_dx)
        if damage > 0:
            defender.hitpoints -= damage
            defender.damaged = True
            txt.append("combat: {} looses {} hitpoints ({} hp left)".format(defendername, damage,
                                                                            defender.hitpoints))
            if defender.hitpoints < 1:
                # ---------- defender is dead  ----------------
                exp = random.randint(7, 10)
                attacker.xp += exp
                attacker.kills += 1
                victim = defendername
                if victim in attacker.killdict:
                    attacker.killdict[victim] += 1
                else:
                    attacker.killdict[victim] = 1
                txt.append("combat: {} has {} hp left, {} gains {} Xp".format(defendername, defender.hitpoints,
                           attackername, exp))
                line = attacker.check_levelup()
                if line:
                    txt.append(line)
                if random.random() < 0.5:    # 50% Chance to drop edibles
                    level.loot.append(Loot(defender.x, defender.y, "meat"))
        else:
            txt.append("combat: {} is not harmed".format(defendername))
    attacker.hunger += 1
    defender.hunger += 1
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
        print('Warning, unable to load,', file)
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

    def image_at(self, rectangle, colorkey=None):
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
    def images_at(self, rects, colorkey=None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey=None):
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
        self.hunger = 0
        self.level = level   # each monster starts with level 1, may progress into higher levels
        self.rank = ""
        self.damaged = False  # to calculate the full hitpoints. each monster start at full health
        if hp == 0:
            self.hitpoints = random.randint(10, 20)
        else:
            self.hitpoints = hp
        self.hpmax = self.hitpoints  # maximum amount of hitpoints, will be auto-generated
        if picture == "":
            self.picture = PygView.MONSTERPICTURE
        else:
            self.picture = picture
        #self.name = random.choice(("Frank", "Dilbert", "Bob", "Alice"))
        self.strength = random.randint(1, 6)
        self.dexterity = random.randint(1, 6)
        self.intelligence = random.randint(1, 6)
        self.inventory = {"fist": 1}  # each monster has a fist as backup weapon
        self.sight_radius = 2  # distance where the monster starts hunting the player
        for z in ["knife", "sword", "shield", "armor"]:
            if random.random() < 0.1:  # each Item has a 10% Chance 
                self.inventory[z] = 1

    def update_inventory(self):
        """remove all items from the inventory with value less than 1"""
        zeroitems = [k for k, v in self.inventory.items() if v < 1]
        for key in zeroitems:
            del self.inventory[key]

    def check_levelup(self):
        return ""

    def ai(self, player):
        """returns a random dx, dy: where the monster wants to go (cardinal direction only)"""
        # dirs = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
        # return random.choice(dirs)   # return dx, xy
        if abs(player.x - self.x) < self.sight_radius and abs(player.y - self.y) < self.sight_radius:
            dx, dy = 0, 0
            if self.x < player.x:
                dx = 1
            elif self.x > player.x:
                dx = -1
            if self.y < player.y:
                dy = 1
            elif self.y > player.y:
                dy = -1
            if dx != 0 and dy != 0:  # do not move diagonal, choose one valid direction instead
                dx, dy = random.choice([(dx, 0), (0, dy)])
        else:
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])  # roaming around
        return dx, dy


class Boss(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """a monster that moves toward the player"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        self.sight_radius = 7  # boss can see farther to hunt player


class Statue(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """a stationary monster that only defends it self"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        self.picture = PygView.STATUE1
        self.hitpoints = 50

    def ai(self, player):
        return 0, 0  # statue is immobile and will never attack player, only defend it self


class Goblin(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """example of a weak monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        # self.picture = random.choice((PygView.GOBLIN1, PygView.GOBLIN2, PygView.GOBLIN3))
        self.picture = PygView.GOBLIN1
        self.strength = random.randint(3, 9)
        self.hitpoints = random.randint(20, 25)
        # -- give something into inventory
        # self.inventory["goblin amulet"] = 1


class Wolf(Monster):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """another weak monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        # self.picture = random.choice((PygView.WOLF1, PygView.WOLF2, PygView.WOLF3))
        self.picture = PygView.WOLF1
        self.strength = random.randint(3, 4)
        self.hitpoints = random.randint(15, 20)
        # self.dexterity = random.randint(5,8)
        # a wolf can not have shield, armor etc
        self.inventory = {"fangs": 1}  # overwriting inventory from Monster, a wolf can not have other weapons


class EliteWarrior(Boss):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        """example for a boss monster"""
        Monster.__init__(self, x, y, xp, level, hp, picture)
        # ------- put your own code here: ----
        self.hitpoints = 32
        # self.picture = random.choice((PygView.WARRIOR1, PygView.WARRIOR2, PygView.WARRIOR3))
        self.picture = PygView.WARRIOR1
        # self.strength = random.randint(12,24)   # more strength
        self.inventory["sword"] = 1             # 100% chance to start with good equipment
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
        self.rank = "unworthy"
        self.name = "anonymous"  # will be overwritten by main loop
        self.inventory = {"shield": 1, "fist": 1}  # player start with shield and fist only
        self.z = 0
        self.keys = []
        self.story1 = False  # for story missions
        self.story2 = False  # for story missions
        self.story3 = False  # for story missions
        # self.hunger = 0   # already defined in class Monster, because combat makes hungry
        self.mana = 0
        if hp == 0:
            self.hitpoints = random.randint(5, 10)
        else:
            self.hitpoints = hp
        self.hpmax = self.hitpoints
        if picture == "":
            self.picture = PygView.PLAYERPICTURE
        else:
            self.picture = picture

    def detect(self):
        """rolls a test to detect a hidden trap, with bonus for intelligence (2/3) and dexterity (1/3)"""
        return random.gauss(0.5 + self.intelligence * 0.066 + self.dexterity * 0.033, 0.2)

    def evade(self):
        """rolls a test for half damage, with bonus for high dexterity"""
        return random.gauss(0.5 + self.dexterity * 0.1, 0.2)

    def levelup(self, new_rank="Nobody"):
        self.level += 1
        self.hitpoints += self.level * 2 + random.randint(1, 6)
        self.rank = new_rank
        improve = random.choice(("strength", "dexterity", "intelligence"))
        self.__setattr__(improve, self.__getattribute__(improve)+1)  # +=1 for selected attribute
        Flytext(self.x, self.y, "LevelUp: +1 {}".format(improve), (0, 0, 255))
        self.hpmax *= 2  # auto-heal at levelup
        self.hp = self.hpmax
        self.damaged = False
        # TODO: level-up sound effect

    def check_levelup(self):
        if self.xp >= 15 and self.level == 1:
            self.levelup("page")  # level += 1
        elif self.xp >= 30 and self.level == 2:
            self.levelup("squire")
        elif self.xp >= 60 and self.level == 3:
            self.levelup("knight")
        elif self.xp >= 120 and self.level == 4:
            self.levelup("lord")
        elif self.xp >= 240 and self.level == 5:
            self.levelup("duke")
        elif self.xp >= 480 and self.level == 6:
            self.levelup("arch duke")
        elif self.xp >= 960 and self.level == 7:
            self.levelup("prince")
        elif self.xp >= 1920 and self.level == 8:
            self.levelup("king")
        else:
            return ""  # add your own code here
        return "{} gains Level {}: {}".format(type(self).__name__, self.level, self.rank)

    def ai(self, player=None):
        return 0, 0  # overwriting ai from Monster calss. Player get his own AI code from mainloop

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
        self.xp += 1  # TODO: got item sound effect
        
        
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
        self.target = (0, 0, 0)  # x,y,z


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
        self.level = random.randint(1, 6)
        self.hitpoints = self.level * 2
        self.picture = PygView.TRAP
        self.visible = False                # overwriting default from class Item()
        # self.had_detecting_check = False  # the player has only one chance (per rank) to detect traps

    def detect(self):
        """rolls a die to see if the player is experienced enough to see the trap
           checks against players intelligence (2/3) and dexterity (1/3)"""
        # gives something mostly between 0 and 1, centered around 0.5
        return random.gauss(0.5 + self.level * 0.1, 0.2)

    def damage(self):
        """rolls one die per level of trap to calculate the damage to the player."""
        damage = 0
        for _ in range(self.level):
            damage += random.randint(1, 6)
        return damage


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
        good_levels = []
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
                # levels.append(Level(good_lines, warning_signs))
                good_levels.append((good_lines, warning_signs))
        fails = len(list_of_levelsourcefilenames) - len(good_levels)
        print("{} level(s) were successfully added to the game".format(len(good_levels)))
        if len(good_levels) < 1:
            sys.exit("no levels loaded - game can not start")
        elif fails > 0:
            print("{} level(s) were not loaded because of errors".format(fails))
            input("press [Enter] to start the game anyway")
        return good_levels

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
        y = 0
        for line in self.lines:
            x = 0
            for char in line:
                # if not overwritten later by a Wall() object etc., each tile is a Floor()
                self.layout[(x, y)] = Floor()
                if char == "M":
                    self.monsters.append(random.choice([Goblin(x, y), Wolf(x, y)]))  # insert your own Monsters here
                elif char == "B":
                    # insert your own boss monsters here
                    self.monsters.append(random.choice([EliteWarrior(x, y), Golem(x, y)]))
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
                    self.layout[(x, y)] = Wall()           # overwrite Wall() instead of Floor()
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

# this sprite class was not useable because Monsters were created to soon, by Level.__init__, causing problems
# class Healthbar(pygame.sprite.Sprite):
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
    def __init__(self, x, y, text="hallo", rgb=(255, 0, 0), blockxy = True,
                 dx=0, dy=-50, duration=2, acceleration_factor = 0.96):
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
        self.image = write(self.text, (self.r, self.g, self.b), 22)  # font 22
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

    def __init__(self, checked_list_of_levels, width=640, height=400, x=1, y=1, xp=0, level=1, hp=50, fullscreen=False):
        if fullscreen:
            winstyle = pygame.FULLSCREEN
        else:
            winstyle = 0
        # pygame.mixer.pre_init(44100, -16, 2, 2048)  # setup mixer to avoid sound lag
        pygame.init()
        self.clock = pygame.time.Clock()
        # ----------- pictureschirm einrichten --------
        PygView.width = width   #
        PygView.height = height
        # self.screenrect = pygame.Rect(0, 0, self.width, self.height)
        # bestdepth = pygame.display.mode_ok(self.screenrect.size, winstyle, 32)
        # self.screen = pygame.display.set_mode(self.screenrect.size, winstyle, bestdepth)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.fps = 30  # frames per second
        pygame.display.set_caption("Press ESC to quit")
        self.gui_height = 100  # height in pixel of bottom gui area
        self.gui_width = 150   # width in pixel of right side gui area
        self.map = pygame.Surface((self.gui_width, self.gui_height))
        self.mapzoom = 3
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
        PygView.TRAP = PygView.FEAT.image_at((30, 128, 32, 32), (0, 0, 0))  # the extra (0,0,0) makes sprite transparent
        PygView.PLAYERPICTURE = PygView.FIGUREN.image_at((111, 1215, 32, 32), (0, 0, 0))
        PygView.STAIRDOWN = PygView.FEAT.image_at((32*4, 32*5, 32, 32))
        PygView.STAIRUP = PygView.FEAT.image_at((32*5, 32*5, 32, 32), (0, 0, 0))
        PygView.MONSTERPICTURE = PygView.FIGUREN.image_at((0, 0, 32, 32), (0, 0, 0))
        PygView.STATUE1 = PygView.FIGUREN.image_at((650, 960, 28, 32), (0, 0, 0))  # Sprite is less than 32 pixel width
        PygView.GOBLIN1 = PygView.FIGUREN.image_at((659, 990, 32, 32), (0, 0, 0))
        PygView.WOLF1 = PygView.FIGUREN.image_at((667, 607, 32, 32), (0, 0, 0))
        PygView.WARRIOR1 = PygView.FIGUREN.image_at((405, 989, 32, 32), (0, 0, 0))
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
        self.player.name = ask("Your name [Enter]? >>", self.screen, PygView.DRUID)
        self.player.name = self.player.name[0].upper() + self.player.name[1:].lower()
        self.levels = []
        for lines, signs in checked_list_of_levels:     # checked by Level.check_levels()
            self.levels.append(Level(lines, signs))
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
        # self.bargroup = pygame.sprite.Group()
        self.allgroup = pygame.sprite.LayeredUpdates()  # sprite group with layers
        # --------- attach Sprites to Sprite groups ---
        Flytext.groups = self.flytextgroup, self.allgroup
        # Healthbar.groups = self.bargroup, self.allgroup
        # ---------- sound and music ----------
        # sounds are in folder "sounds", music is in folder "music"
        PygView.bowsound = load_sound("bow.ogg")
        PygView.macesound = load_sound("mace.wav")
        load_music("the_king_is_dead.ogg")  # music loop
        # pygame.mixer.music.play()  # start background music
        # pygame.mixer.music.stop()
        # pygame.mixer.music.pause()
        # pygame.mixer.music.unpause()
        # PygView.macesound.play()   # soundeffect start
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

    def paint_map(self):
        self.map.fill((20, 20, 20))  # fill with dark grey
        scrollx = self.gui_width / 2 - self.player.x * self.mapzoom
        scrolly = self.gui_height / 2 - self.player.y * self.mapzoom
        y = 0
        for line in self.level.lines:
            x = 0
            for char in line:
                if char == "#":  # wall
                    pygame.draw.rect(self.map, (150, 150, 150), (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                     self.mapzoom, self.mapzoom))
                elif char == "<":  # stair up
                    pygame.draw.rect(self.map, (255, 150, 150), (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                     self.mapzoom, self.mapzoom))
                elif char == ">":  # stair down
                    pygame.draw.rect(self.map, (150, 255, 150), (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                     self.mapzoom, self.mapzoom))
                else:
                    pygame.draw.rect(self.map, (50, 50, 50),    (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                     self.mapzoom, self.mapzoom))
                # player pixel
                pygame.draw.rect(self.map, (255, 0, 0), (self.player.x * self.mapzoom + scrollx,
                                 self.player.y * self.mapzoom + scrolly, self.mapzoom, self.mapzoom))
                x += 1
            y += 1

        #self.screen.blit(self.map, (self.width - self.gui_width + scrollx, 0 + scrolly))
        line = write("zoom = {} press + or -".format(self.mapzoom), (0, 0, 255), 18)
        self.map.blit(line, (0, self.gui_height-12))

    def paint(self):
        """paint level and GUI"""
        # ----- GUI for text messages below playing area
        for y in range(self.level.depth):
            for x in range(self.level.width):
                self.background.blit(self.level.layout[(x, y)].picture, (x * 32, y * 32))
                for sign in [s for s in self.level.signs if s.x == x and s.y == y]:
                    self.background.blit(sign.picture, (x * 32, y * 32))
                for trap in [t for t in self.level.traps if t.x == x and t.y == y and t.hitpoints > 0
                             and t.visible]:
                    self.background.blit(trap.picture, (x * 32, y * 32))
                for door in [d for d in self.level.doors if d.x == x and d.y == y and d.closed]:
                    self.background.blit(door.picture, (x * 32, y * 32))
                for loot in [l for l in self.level.loot if l.x == x and l.y == y and not l.carried]:
                    self.background.blit(loot.picture, (x * 32, y * 32))
                for key in [k for k in self.level.keys if k.x == x and k.y == y and not k.carried]:
                    self.background.blit(key.picture, (x * 32, y * 32))
        # Scrolling: paint the player in the middle of the screen # TODO: improve gui layout
        PygView.scrollx = (self.width - self.gui_width) / 2 - self.player.x * 32
        PygView.scrolly = (self.height - self.gui_height) / 2 - self.player.y * 32
        self.screen.fill((0, 0, 0))  # make all black
        self.screen.blit(self.background, (PygView.scrollx, PygView.scrolly))

        # ---- paint monsters ---
        for monster in self.level.monsters:
            self.screen.blit(monster.picture, (PygView.scrollx + monster.x * 32, PygView.scrolly + monster.y * 32))
            # ------- draw healthbar  ----------
            # first, calculate if the monster has full hitpoints
            if not monster.damaged:
                monster.hpmax = monster.hitpoints
            # calculate health percentage, 100% = 32 pixel
            health = round(((monster.hitpoints / (monster.hpmax / 100)) / 100) * 32,0)
            # shows a maximum of 31 hitpoints as full green health-bar, with red from the right if less healthy
            # pygame.draw.rect(self.screen, (255,255,255), (PygView.scrollx + monster.x * 32,
            #    PygView.scrolly + monster.y * 32 - 15,32,4))
            # red full bar
            pygame.draw.rect(self.screen, (255, 0, 0), (PygView.scrollx + monster.x * 32,
                             PygView.scrolly + monster.y * 32 - 15, 32, 5))
            # overwrite with green health bar
            pygame.draw.rect(self.screen, (0, 255, 0), (PygView.scrollx + monster.x * 32,
                             PygView.scrolly + monster.y * 32 - 15, health, 5))
        # ---- paint player -----
        self.screen.blit(self.player.picture, (PygView.scrollx + self.player.x * 32, PygView.scrolly +self.player.y*32))
        # ----- paint the GUI ---------
        # ---- right area GUI ----
        # --- paint minimap 150x150 ---
        pygame.draw.rect(self.screen, (0, 0, 0), (self.width - self.gui_width, 0, self.gui_width, self.height))
        self.paint_map()
        self.screen.blit(self.map, (self.width - self.gui_width, 0))
        # ---- hp-bar, below minimap:
        line = write("HP: {}".format(self.player.hitpoints), (0, 255, 0), 18)
        y = self.gui_height + 5  # the height of the minimap
        self.screen.blit(line, (self.width - self.gui_width, y))
        # pygame.draw.rect(self.screen, (255, 0, 0), (self.width - self.gui_width, y, self.gui_width, 10))  # red
        # green hp bar
        pygame.draw.rect(self.screen, (0, 255, 0), (self.width - self.gui_width + 50, y, self.player.hitpoints, 10))
        #  ---- mana-bar
        y += 15
        line = write("MP: {:.0f}".format(self.player.mana), (0, 0, 255), 18)
        self.screen.blit(line, (self.width - self.gui_width, y))
        pygame.draw.rect(self.screen, (0, 0, 255), (self.width - self.gui_width + 50, y, self.player.mana, 10))
        #  ---- hunger-bar
        y += 15
        line = write("Hu: {:.0f}".format(self.player.hunger), (255, 255, 0), 18)
        self.screen.blit(line, (self.width - self.gui_width, y))
        pygame.draw.rect(self.screen, (255, 255, 0), (self.width - self.gui_width + 50, y, self.player.hunger, 10))
        # ---- bottom area GUI
        # ---- clean text are by painting it black ---
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.height - self.gui_height, self.width, self.gui_height))
        # ---- player status ----
        line = write("{}: hp:{} keys:{}".format(self.player.name,
                     self.player.hitpoints, len(self.player.keys)), (0, 255, 0), 24)  # fontsize = 24
        self.screen.blit(line, (self.width / 2, self.height - self.gui_height))
        line = write("turn:{} x:{} y:{} dungeon-level:{}".format(self.turns, self.player.x, self.player.y,
                     self.player.z),   (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - self.gui_height + 16))
        line = write("Exp: {} Level:{}".format(self.player.xp, self.player.level), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - self.gui_height + 16*2))
        line = write("# Monsters in level: {} in dungeon: {}".format(self.mo1, self.mo2), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - self.gui_height + 16*3))
        line = write("Hunger: {}".format(self.player.hunger), (0, 255, 0), 24)
        self.screen.blit(line, (self.width / 2, self.height - self.gui_height + 16*4))
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
                    # ---- handle keys that do not count as a game turn (user interface etc.)
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    elif event.key == pygame.K_i:
                        # ----------- show inventory (inventory) -----------------
                        display_textlines(self.player.show_inventory(), self.screen, image=PygView.TRADER)
                        continue  # do not move monsters etc., wait for next keyboard command
                    elif event.key == pygame.K_PLUS:
                        # ----- zoom in minimap
                        self.mapzoom += 1
                        continue  # do not move monsters etc., wait for next keyboard command
                    elif event.key == pygame.K_MINUS:
                        # ----- zoom out minimap
                        self.mapzoom -= 1
                        self.mapzoom = max(2, self.mapzoom)  # can not be less than 2
                        continue  # do not move monsters etc., wait for next keyboard command
                    # ---- handle keys that do count as a game turn (player action, movement etc.)
                    self.turns += 1
                    if self.player.mana < 32:
                        self.player.mana += 0.1
                    self.player.hunger += 0.25
                    if self.player.hunger > 100:
                        self.player.hitpoints -= 1
                        self.player.damaged = True
                        Flytext(self.player.x, self.player.y, "Hunger: dmg 1")
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

                    elif event.key == pygame.K_LESS or event.key == pygame.K_GREATER:     # < or > 
                        if type(where).__name__ == "Stair":
                            if not where.down and self.player.z == 0:
                                lines = ["Game OVer",
                                         "you leave the dungeon and return to the surface..",
                                         "...alive!"]
                                display_textlines(lines, self.screen, (255, 255, 255))
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
                            if ("healing potion" in self.player.inventory and
                                    self.player.inventory["healing potion"] > 0):
                                self.player.inventory["healing potion"] -= 1
                                effect = re_roll()
                                self.player.hitpoints += effect
                                self.status.append("{}: You drink the healing potion und gain {} hitpoints".format(
                                                   self.turns, effect))
                                Flytext(self.player.x, self.player.y, "gulp, gulp, gulp: +{} hp".format(effect),
                                        (0, 0, 255))
                                self.player.hitpoints = min(self.player.hpmax, self.player.hitpoints)  # limit healing
                                if self.player.hitpoints == self.player.hpmax:
                                    self.player.damaged = False
                                else:
                                    self.player.damaged = True
                            else:
                                self.status.append("{}: You have no healing potion. Gather more loot!".format(
                                                   self.turns))
                    elif event.key == pygame.K_e:
                        food = [i for i in self.player.inventory if (i == "bread" or i == "meat") and
                                self.player.inventory[i] > 0]
                        if len(food) > 0:  # TODO: eating sound effect
                            self.player.inventory[food[0]] -= 1
                            Flytext(self.player.x, self.player.y, "Yummy {}".format(food[0]), (0, 200, 0))
                            self.player.hunger -= random.randint(5, 30)
                            self.player.hunger = max(0, self.player.hunger)  # hunger can not become < 0
                        else:
                            self.status.append("You have nothing edible in your inventory. Fight and find loot!")
                            Flytext(self.player.x, self.player.y, "no food")  # TODO: no food sound effect
                    # --------------- player goes to a new location ----------
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
                        self.player.damaged = True
                        Flytext(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")
                        self.player.dx, self.player.dy = 0, 0
                    # ----- testing if player runs into door
                    for door in [d for d in self.level.doors if d.x == self.player.x+self.player.dx and
                                 d.y == self.player.y + self.player.dy and d.closed]:
                        if len(self.player.keys) > 0:
                            mykey = self.player.keys.pop()
                            door.closed = False  # unlocked !
                            self.status.append("{}: door unlocked! 1 key used up)".format(self.turns))
                        else:
                            self.player.dx, self.player.dy = 0, 0
                            self.status.append("{}: Ouch! You bump into a door".format(self.turns))
                            self.player.hitpoints -= 1
                            self.player.damaged = True
                            Flytext(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")
                    # ----------------- Finally the player is arrived at a new position --------
                    self.player.x += self.player.dx
                    self.player.y += self.player.dy
                    # --------------- player is at a new location ----------
                    where = self.level.layout[(self.player.x, self.player.y)]
                    # --------------------------- Story Missions ---------------------
                    # ----------------------------------------------------------------
                    # --------- Story 1: visit the druids ---------------
                    if self.player.x == 5 and self.player.y == 5 and self.player.z == 0 and not self.player.story1:
                        # at position x5, y5 in first level (z0)
                        lines = ["I welcome you, wandering hero!",
                                 "Please liberate us",
                                 "the peaceful druids",
                                 "from those dangerous, evil monsters.",
                                 "Slay them all!"]
                        display_textlines(lines, self.screen, (0, 255, 255), PygView.DRUID)
                        self.player.story1 = True
                    # ------------- Story 2:  all monsters killed, druid mission complete ---------
                    if self.mo2 == 0 and self.player.druid_visited and not self.player.story2:
                        lines = ["Congratulation, o hero",
                                 "You have liberated us druids",
                                 "and slayed all the evil monsters",
                                 "Thanks from us all, o fantastic {}!".format(self.player.name)]
                        display_textlines(lines, self.screen, (0,255,255), PygView.DRUID)
                        self.player.inventory["reward: half a kingdom"] = 1
                        self.player.inventory["reward: friendship of the druids"] = 1
                        self.player.story2 = True
                        #running = False
                    # ---------- Story 3: Player destroys statue and goes to position of statue (18,14) in level2 (z=1)
                    if self.player.z == 1 and self.player.x == 14 and self.player.y == 18 and not self.player.story3:
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
                        self.player.story3 = True
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
                    # ---- detect traps around player
                    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                    for (dx, dy) in dirs:
                        traps = [t for t in self.level.traps if t.x == self.player.x + dx and t.y == self.player.y + dy
                                 and not t.visible]
                        for t in traps:
                            if self.player.detect() > t.detect():
                                t.visible = True
                                self.status.append("Trap spotted")
                    # ---------- player is inside a trap ? ---------------------------
                    traps = [t for t in self.level.traps if t.x == self.player.x and t.y == self.player.y]
                    for t in traps:
                        damage = t.damage()
                        # player can roll an evade check (dexterity) against trap detect check for half damage
                        self.status.append("You step into a trap!")
                        if self.player.evade() > t.detect():
                            damage *= 0.5
                            damage = round(damage, 0)
                            self.status.append("Your high dexterity allows you to take only half the damage")
                        self.status.append("The trap is hurting you for {} damage!".format(self.turns, damage))
                        self.player.hitpoints -= damage
                        self.player.damaged = True
                        Flytext(self.player.x, self.player.y, "A trap! Dmg: {}".format(damage))
                        t.hitpoints -= random.randint(0, 4)  # damage to trap
                        if t.hitpoints < 1:
                            self.status.append("{}: trap destroyed!".format(self.turns))
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
            # pressedkeys = pygame.key.get_pressed()
            # if pygame.K_x in pressedkeys:
            #      print("x key is pressed")
            # ------------ redraw screen, blit the sprites --------------
            pygame.display.set_caption("  press Esc to quit. Fps: %.2f (%i x %i)" % (
                                       self.clock.get_fps(), self.width, self.height))
            self.paint() # paint this level
            #  ------- draw the sprites ------
            # self.allgroup.clear(self.screen, self.background)
            self.allgroup.update(self.seconds)
            self.allgroup.draw(self.screen)
            # ---- proceed to next pygame screen
            pygame.display.flip()
        # --------------------------- Game Over ----------------------
        lines = ["**** Game Over *******",
                 "Hitpoints: {}".format(self.player.hitpoints),
                 "Level: {}".format(self.player.level),
                 "Rank: {}".format(self.player.rank),
                 "Victories: {}".format(self.player.kills)]
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
        display_textlines(lines, self.screen,  (255, 255, 255), PygView.GAMEOVER)
        # ------------ game over -----------------
        pygame.mixer.music.stop()
        for line in lines:
            print(line)
        pygame.quit()    # end  pygame  # TODO: game sometimes hangs here. PYthon3+pygame bug?
        sys.exit()      # end python


if __name__ == '__main__':
    # add your own level files here. use os.path.join() for other folders
    sourcefilenames = ["level1demo.txt", "level2demo.txt"]
    levels = Level.check_levels(sourcefilenames)         # testing level for design errors
    # 800 x 600 pixel, Player start at x=1, y=1, in level 0 (the first level) with 0 xp, has level 1 and 50 hit points
    PygView(levels, 800, 600, 1, 1, 0, 1, 50).run()
