import pygame
import sys
import time
import random

pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

LOG_DELAY = 220

""" Colors of the Fonts being Used """
white = (255, 255, 255)
black = (0, 0, 0)
highlight = (220, 220, 220)

""" Fonts Being Used """
menu_font = pygame.font.SysFont("Consolas", 36)
text_font = pygame.font.SysFont("Courier New", 28)

""" Classes Descriptions """
CLASS_DESCRIPTIONS = {
    "Warrior": [
        "Warrior - Frontline Beserker.",
        "",
        "Permanent Bonuses:",
        "* +25% Attack",
        "* Solid HP & Defense",
        "* Decent Attack Speed",
        "",
        "Passive: Beserker Mode",
        "* Chance to Trigger durring attacks",
        "* +50% Attack Boost",
        "* +35% Attack Speed",
        "* -25% Defense only when activated",
    ],
    "Mage": [
        "Mage - Arcane Intellect Specialist.",
        "",
        "Permanent Bonuses:",
        "* +45% Intelligence",
        "* Boost in Luck",
        "* Lower HP & Defense",
        "",
        "Passive Effects:",
        "* Higher INT = more EXP Gain",
        "* Small Chance to gain +1 Free Luck Stat",
        " on level up"
    ],
    "Priest": [
        "Priest - Divine Support Caster.",
        "",
        "Permanent Bonuses:",
        "* +45% Faith",
        "* Small Defense Boost",
        "* Moderate HP",
        "",
        "Passive Effects:",
        "* Faith Restores HP each Turn",
        "* Chance to gain temporary +25%",
        "  Attack & Defense during battle",
    ]
}

""" Player Class"""
class Player:
    def __init__(self, name, player_class):
        self.name = name
        self.player_class = player_class
        self.level = 1
        self.exp = 0
        self.next_level_exp = 100
        self.stat_points = 0

        self.hp = 100
        self.max_hp = 100
        self.atk = 10
        self.defense = 10
        self.intel = 10
        self.faith = 10
        self.luck = 5
        self.aspd = 10

        self.inventory = []
        self.equipment = {
            "primary": None,
            "secondary": None,
            "helmet": None,
            "chestplate": None,
            "gauntlets": None,
            "legs": None,
            "accessory1": None,
            "accessory2": None
        }

        self.passive = ""
        self.apply_class_bonus(player_class)

    def apply_class_bonus(self, player_class):
        if player_class == "Warrior":
            self.hp += 20
            self.max_hp += 20
            self.atk = int(self.atk * 1.25)
            self.defense += 5
            self.aspd += 3
            self.passive = "Berserker Mode"

        elif player_class == "Mage":
            self.hp -= 20
            self.max_hp -= 20
            self.intel = int(self.intel * 1.45)
            self.faith += 2
            self.luck += 2
            self.defense -= 2
            self.aspd -= 2
            self.passive = "Arcane Mind"

        elif player_class == "Priest":
            self.hp += 10
            self.max_hp += 10
            self.faith = int(self.faith * 1.45)
            self.defense += 3
            self.luck += 1
            self.aspd -= 1
            self.passive = "Divine Blessing"

    def gain_exp(self, amount):
        self.exp += amount

        while self.exp >= self.next_level_exp:
            self.exp -= self.next_level_exp
            self.level += 1
            self.stat_points += 5
            self.next_level_exp = int(self.next_level_exp * 1.35)

            self.max_hp += 10
            self.hp = self.max_hp

    def apply_item_bonuses(self, item):
        for stat, value in item.bonuses.items():
            setattr(self, stat, getattr(self, stat) + value)
    
    def remove_item_bonuses(self, item):
        for stat, value in item.bonuses.items():
            setattr(self, stat, getattr(self, stat) - value)

    def equip_item(self, item):
        slot = item.slot

        if slot == "accessory":
            if 