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
            if self.equipment["accessory1"] is None:
                slot = "accessory1"
            elif self.equipment["accessory2"] is None:
                slot = "accessory2"
            else:
                slot = "accessory1"

        if self.equipment.get(slot):
            self.remove_item_bonuses(self.equipment[slot])

        self.equipment[slot] = item
        self.apply_item_bonuses(item)

        if item in self.inventory:
            self.inventory.remove(item)

""" Allocating Stat Points """
def allocate_stats(player, title_surface, border_surface):
    stats = ["HP", "ATK", "DEF", "INT", "FTH", "LCK", "ASPD"]
    index = 0

    stat_map = {
        "HP": "max_hp",
        "ATK": "atk",
        "DEF": "defense",
        "INT": "intel",
        "FTH": "faith",
        "LCK": "luck",
        "ASPD": "aspd"
    }

    stat_gain = {
        "HP": 10,
        "ATK": 5,
        "DEF": 5,
        "INT": 2,
        "FTH": 2,
        "LCK": 1,
        "ASPD": 0.25
    }

    while player.stat_points > 0:
        screen.fill(black)
        screen.blit(title_surface, (0,0))
        screen.blit(border_surface, (0,0))

        title = menu_font.render("Level Up! Distribute Stat Points", True, white)
        screen.blit(title, (80, 330))

        points_txt = text_font.render(
            f"Available Points: {player.stat_points}", True, white
        )
        screen.blit(points_txt, (80, 390))

        y = 450
        for i, stat in enumerate(stats):
            attr = stat_map[stat]
            value = getattr(player, attr)

            if stat == "ASPD":
                display_value = f"{value: .2f}"
            else:
                display_value = str(value)

            color = black if i == index else white
            txt = text_font.render(f"{stat}: {display_value}", True, color)
            rect = txt.get_rect(topleft=(80, y))

            if i == index:
                pygame.draw.rect(screen, highlight, rect.inflate(20, 10))

            screen.blit(txt, rect)
            y += 50

        info = text_font.render(
            "ENTER = Add Point | Arrow Keys = Move", True, white
        )
        screen.blit(info, (80, y + 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % len(stats)
                elif event.key == pygame.K_DOWN:
                    index = (index + 1) % len(stats)
                elif event.key == pygame.K_RETURN:
                    stat_choice = stats[index]
                    attr = stat_map[stat_choice]
                    gain = stat_gain[stat_choice]

                    if stat_choice == "HP":
                        player.max_hp += gain
                        player.hp += gain
                    else:
                        setattr(player, attr, getattr(player, attr) + gain)

                    player.stat_points -= 1

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)

""" GUI """
def create_border_surface():
    border = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    margin = 40
    thickness = 6
    rect = pygame.Rect(
        margin,
        margin,
        screen.get_width() - margin * 2,
        screen.get_height() - margin * 2
    )
    pygame.draw.rect(border, white, rect, thickness)
    return border

""" ASCII Title """
def draw_ascii_title_surface():
    ascii_art = r""" 
_____        ______    ____         ____       _____                 _____          _____         _________________  ____   ____      ______               _____   ____      _____            ______   _________________             _____         _____         ______   
___|\    \   ___|\     \  |    |       |    |  ___|\    \           ____|\    \    ____|\    \       /                 \|    | |    | ___|\     \         ____|\    \ |    | ___|\    \       ___|\     \ /                 \        ___|\    \    ___|\    \    ___|\     \  
|    |\    \ |     \     \ |    |       |    | /    /\    \         /     /\    \  |    | \    \      \______     ______/|    | |    ||     \     \       |    | \    \|    ||    |\    \     |    |\     \\______     ______/       /    /\    \  /    /\    \  |     \     \ 
|    | |    ||     ,_____/||    |       |    ||    |  |    |       /     /  \    \ |    |______/         \( /    /  )/   |    |_|    ||     ,_____/|      |    |______/|    ||    | |    |    |    |/____/|   \( /    /  )/         |    |  |    ||    |  |____| |     ,_____/|
|    |/____/ |     \--'\_|/|    |  ____ |    ||    |  |____|      |     |    |    ||    |----'\           ' |   |   '    |    .-.    ||     \--'\_|/      |    |----'\ |    ||    |/____/  ___|    \|   | |    ' |   |   '          |    |__|    ||    |    ____ |     \--'\_|/
|    |\    \ |     /___/|  |    | |    ||    ||    |   ____       |     |    |    ||    |_____/             |   |        |    | |    ||     /___/|        |    |_____/ |    ||    |\    \ |    \    \___|/       |   |              |    .--.    ||    |   |    ||     /___/|  
|    | |    ||     \____|\ |    | |    ||    ||    |  |    |      |\     \  /    /||    |                  /   //        |    | |    ||     \____|\       |    |       |    ||    | |    ||    |\     \         /   //              |    |  |    ||    |   |_,  ||     \____|\ 
|____| |____||____ '     /||____|/____/||____||\ ___\/    /|      | \_____\/____/ ||____|                 /___//         |____| |____||____ '     /|      |____|       |____||____| |____||\ ___\|_____|       /___//               |____|  |____||\ ___\___/  /||____ '     /|
|    | |    ||    /_____/ ||    |     |||    || |   /____/ |       \ |    ||    | /|    |                |`   |          |    | |    ||    /_____/ |      |    |       |    ||    | |    || |    |     |      |`   |                |    |  |    || |   /____ / ||    /_____/ |
|____| |____||____|     | /|____|_____|/|____| \|___|    | /        \|____||____|/ |____|                |____|          |____| |____||____|     | /      |____|       |____||____| |____| \|____|_____|      |____|                |____|  |____| \|___|    | / |____|     | /
  \(     )/    \( |_____|/   \(    )/     \(     \( |____|/            \(    )/      )/                    \(              \(     )/    \( |_____|/         )/           \(    \(     )/      \(    )/          \(                    \(      )/     \( |____|/    \( |_____|/ 
   '     '      '    )/       '    '       '      '   )/                '    '       '                      '               '     '      '    )/            '             '     '     '        '    '            '                     '      '       '   )/        '    )/    
                     '                                '                                                                                       '                                                                                                           '              
"""

    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    lines = ascii_art.splitlines()

    font_size = 32
    font = pygame.font.SysFont("Courier New", font_size)
    longest_px = max(font.size(line)[0] for line in lines)

    while longest_px > screen.get_width() * 0.90 and font_size > 5:
        font_size -= 1
        font = pygame.font.SysFont("Courier New", font_size)
        longest_px = max(font.size(line)[0] for line in lines)

    y = 80
    for line in lines:
        text = font.render(line, True, white)
        line_w = font.size(line)[0]
        xx = (screen.get_width() - line_w) // 2
        surf.blit(text, (xx, y))
        y += font.get_linesize()

    return surf

""" Class Stat Window """
def get_class_preview_stats(player_class):
    hp = 100
    atk = 10
    defense = 10
    intel = 10
    faith = 10
    luck = 5
    aspd = 10

    if player_class == "Warrior":
        hp += 20
        atk = int(atk * 1.25)
        defense += 5
        aspd += 3

    elif player_class == "Mage":
        hp -= 20
        intel = int(intel * 1.45)
        faith += 2
        luck += 2
        defense -= 2
        aspd -= 2

    elif player_class == "Priest":
        hp += 10
        faith = int(faith * 1.45)
        defense += 3
        luck += 1
        aspd -= 1

    return {
        "HP": hp,
        "ATK": atk,
        "DEF": defense,
        "INT": intel,
        "FTH": faith,
        "LCK": luck,
        "ASPD": aspd
    }

""" Draw Stat Box """
def draw_stat_box(player_class, player_name="???"):
    stats = get_class_preview_stats(player_class)

    box_width = 350
    box_height = 420
    box_x = screen.get_width() - box_width - 80
    box_y = 380

    pygame.draw.rect(screen, white, (box_x, box_y, box_width, box_height), 4)

    name_label = text_font.render(f"Name: {player_name}", True, white)
    lvl_label = text_font.render("Level: 1", True, white)

    screen.blit(name_label, (box_x + 20, box_y + 10))
    screen.blit(lvl_label, (box_x + 20, box_y + 45))

    y = box_y + 100
    for stat_name, value in stats.items():
        line = text_font.render(f"{stat_name}: {value}", True, white)
        screen.blit(line, (box_x + 20, y))
        y += 40

""" Menu Selector """
def menu_selection(options, title_surface, border_surface, 
                   show_descriptions=False, current_name="???"):
    selected_index = 0

    while True:
        screen.fill(black)
        screen.blit(title_surface, (0, 0))
        screen.blit(border_surface, (0,0))

        if show_descriptions:
            selected = options[selected_index]
            desc = CLASS_DESCRIPTIONS.get(selected, [])

            x = 80
            y = 350
            for line in desc:
                txt = text_font.render(line, True, white)
                screen.blit(txt, (x, y))
                y += text_font.get_linesize()

            draw_stat_box(selected, current_name)

        base_y = 550
        for i, option in enumerate(options):
            color = black if i == selected_index else white
            txt = menu_font.render(option, True, color)
            rect = txt.get_rect(center=(screen.get_width() // 2, base_y + i * 80))

            if i == selected_index:
                box = pygame.Rect(rect.x - 20, rect.y - 10, rect.width + 40, rect.height + 20)
                pygame.draw.rect(screen, highlight, box)

            screen.blit(txt, rect)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected_index]
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)

""" Inventory Screen """
def open_inventory(player, title_surface, border_surface):
    running = True
    selected_index = 0

    while running:
        screen.fill(black)
        screen.blit(title_surface, (0, 0))
        screen.blit(border_surface, (0, 0))

        inv_title = menu_font.render("Equipment", True, white)
        screen.blit(inv_title, (80, 320))

        equip_x = 80
        equip_y = 450
        equip_w = 500
        equip_h = 500
        padding = 20

        pygame.draw.rect(screen, white, (equip_x, equip_y, equip_w, equip_h), 4)

        y = equip_y + padding
        max_text_width = equip_w - padding * 2

        for slot, item in player.equipment.items():
            line_text = f"{slot.title()}: {item if item else 'Empty'}"
            draw_wrapped_text(
                screen,
                line_text,
                text_font,
                white,
                equip_x + padding,
                y,
                max_text_width
            )
            y += text_font.get_linesize() * 1.8

        inv_x = screen.get_width() - 500
        inv_y = 450
        inv_w = 420
        inv_h = 500

        pygame.draw.rect(screen, white, (inv_x, inv_y, inv_w, inv_h), 4)

        inv_label = text_font.render(screen, white, (inv_x, inv_y, inv_w, inv_h), 4)
        screen.blit(inv_label, (inv_x + 20, inv_y + 10))

        y = inv_y + 60
        max_inv_width = inv_w - 40

        if not player.inventory:
            draw_wrapped_text(
                screen, 
                "Empty",
                text_font,
                white,
                inv_x + 20,
                y,
                max_inv_width
            )
        else:
            for i, item in enumerate(player.inventory):
                color = highlight if i == selected_index else white

                draw_wrapped_text(
                    screen,
                    str(item),
                    text_font,
                    color,
                    inv_x + 20,
                    y,
                    max_inv_width
                )

                y += text_font.get_linesize() * 1.8
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP and player.inventory:
                    selected_index = (selected_index - 1) % len(player.inventory)
                elif event.key == pygame.K_DOWN and player.inventory:
                    selected_index = (selected_index + 1) % len(player.inventory)
                elif event.key == pygame.K_RETURN and player.inventory:
                    item = player.inventory[selected_index]
                    player.equip_item(item)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
        clock.tick(60)

class Equipment:
    def __init__(self, name, rarity, slot, bonuses):
        self.name = name
        self.rarity = rarity
        self.slot = slot
        self.bonuses = bonuses

    def __str__(self):
        bonus_text = ", ".join([f"+{v} {k.upper()}" for k, v in self.bonuses.items()])
        return f"[{self.rarity}] {self.name} ({bonus_text})"
    
""" Monsters and Descriptions """
class Monster:
    def __init__(self, name, rarity, desc, hp, atk, defense, aspd):
        self.name = name
        self.rarity = rarity
        self.desc = desc
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.defense = defense
        self.aspd = aspd

MONSTER_TEMPLATES = [
    # ======================
    # COMMON – LONGER, SAFE FIGHTS
    # ======================
    {
        "name": "Floating Recon Sphere",
        "rarity": "Common",
        "type": "drone",
        "desc": "A small surveillance drone flickers with blue sensors as it hovers silently.",
        "base_hp": 60,
        "base_atk": 2,
        "base_def": 2,
        "base_aspd": 9,
        "weight": 14
    },
    {
        "name": "Rust-Eaten Service Bot",
        "rarity": "Common",
        "type": "humanoid",
        "desc": "A humanoid maintenance robot limps forward, plating cracked and sparking.",
        "base_hp": 85,
        "base_atk": 3,
        "base_def": 4,
        "base_aspd": 7,
        "weight": 14
    },
    {
        "name": "Auto-Turret Node",
        "rarity": "Common",
        "type": "turret",
        "desc": "A compact wall-mounted turret rotates toward you, its barrel glowing faintly.",
        "base_hp": 95,
        "base_atk": 3,
        "base_def": 3,
        "base_aspd": 8,
        "weight": 13
    },
    {
        "name": "Scrap-Rat Drone",
        "rarity": "Common",
        "type": "beast",
        "desc": "A small scavenger drone skitters across the floor, claws sparking against metal.",
        "base_hp": 70,
        "base_atk": 2,
        "base_def": 2,
        "base_aspd": 11,
        "weight": 14
    },
    {
        "name": "Malfunctioning Loader Unit",
        "rarity": "Common",
        "type": "humanoid",
        "desc": "A heavy cargo robot lurches forward blindly, coolant leaking from its joints.",
        "base_hp": 140,
        "base_atk": 4,
        "base_def": 6,
        "base_aspd": 6,
        "weight": 12
    },
    {
        "name": "Humming Power Core Wisp",
        "rarity": "Common",
        "type": "energy",
        "desc": "A flickering ball of unstable energy drifts silently, crackling softly.",
        "base_hp": 50,
        "base_atk": 1,
        "base_def": 1,
        "base_aspd": 13,
        "weight": 14
    },

    # ======================
    # UNCOMMON – DURABLE, STEADY DAMAGE
    # ======================
    {
        "name": "Shockhound Unit",
        "rarity": "Uncommon",
        "type": "beast",
        "desc": "A quadrupedal hunting machine growls with static electricity dancing along its fangs.",
        "base_hp": 140,
        "base_atk": 6,
        "base_def": 7,
        "base_aspd": 10,
        "weight": 6
    },
    {
        "name": "Sentinel Combat Frame",
        "rarity": "Uncommon",
        "type": "humanoid",
        "desc": "An armored bipedal combat android deploys its forearm shields into position.",
        "base_hp": 160,
        "base_atk": 7,
        "base_def": 10,
        "base_aspd": 9,
        "weight": 6
    },
    {
        "name": "Thermal Sphere Mk II",
        "rarity": "Uncommon",
        "type": "drone",
        "desc": "A floating orb radiates intense heat as vents open across its metal shell.",
        "base_hp": 150,
        "base_atk": 6,
        "base_def": 7,
        "base_aspd": 10,
        "weight": 6
    },

    # ======================
    # RARE – HIGH ENDURANCE DUELS
    # ======================
    {
        "name": "Ionblade Executioner",
        "rarity": "Rare",
        "type": "humanoid",
        "desc": "Ion-charged blades extend from its arms, illuminating the hallway with blue-white arcs.",
        "base_hp": 240,
        "base_atk": 9,
        "base_def": 13,
        "base_aspd": 10,
        "weight": 2
    },
    {
        "name": "Shockmaw Rex",
        "rarity": "Rare",
        "type": "beast",
        "desc": "A towering wolf-shaped machine snarls, hydraulic jaws bright with crackling charge.",
        "base_hp": 280,
        "base_atk": 10,
        "base_def": 14,
        "base_aspd": 9,
        "weight": 2
    },

    # ======================
    # LEGENDARY – LONG MINIBOSS FIGHTS
    # ======================
    {
        "name": "VX-77 Siege Mech",
        "rarity": "Legendary",
        "type": "mech",
        "desc": "A heavy war mech stomps forward, missile racks opening while a central laser cannon spins up.",
        "base_hp": 420,
        "base_atk": 12,
        "base_def": 20,
        "base_aspd": 8,
        "weight": 1
    },
    {
        "name": "Phase Turret Array",
        "rarity": "Legendary",
        "type": "turret",
        "desc": "Several autonomous turrets rise from the floor in a synchronized firing lattice.",
        "base_hp": 390,
        "base_atk": 11,
        "base_def": 18,
        "base_aspd": 9,
        "weight": 1
    },

    # ======================
    # MYTHICAL – TRUE WAR OF ATTRITION
    # ======================
    {
        "name": "Prototype DR-A-GN",
        "rarity": "Mythical",
        "type": "dragon",
        "desc": "A colossal serpentine war-machine unfolds, metal wings humming with reactor heat.",
        "base_hp": 650,
        "base_atk": 14,
        "base_def": 25,
        "base_aspd": 9,
        "weight": 1
    },
    {
        "name": "Singularity Core Titan",
        "rarity": "Mythical",
        "type": "titan",
        "desc": "A monolithic construct hums with gravity-distorting energy, pulling debris toward itself.",
        "base_hp": 720,
        "base_atk": 13,
        "base_def": 28,
        "base_aspd": 8,
        "weight": 1
    },
]

RARITY_MULTIPLIER = {
    "Common": 1.0,
    "Uncommon": 1.2,
    "Rare": 1.5,
    "Legendary": 1.9,
    "Mythical": 2.3,
}
RARITY_EXP = {
    "Common": 110,
    "Uncommon": 430,
    "Rare": 1120,
    "Legendary": 5000,
    "Mythical": 10000,
}

LOOT_RARITY = ["Common", "Uncommon", "Rare", "Legendary", "Mythical", "MasterCraft"]

LOOT_COLORS = {
    "Common": (200, 200, 200),
    "Uncommon": (0, 255, 0),
    "Rare": (0, 180, 255),
    "Legendary": (255, 255, 0),
    "Mythical": (255, 144, 0),
    "MasterCraft": (255, 0, 0)
}

LOOT_CHANCE = {
    "Common": 0.60,
    "Uncommon": 0.25,
    "Rare": 0.10,
    "Legendary": 0.04,
    "Mythical": 0.009,
    "MasterCraft": 0.001
}

def generate_monster(floor_num=1):
    weights = [t["weight"] for t in MONSTER_TEMPLATES]
    template = random.choices(MONSTER_TEMPLATES, weights=weights, k=1)[0]

    rarity = template["rarity"]
    mult = RARITY_MULTIPLIER[rarity]

    hp = int((template["base_hp"] + floor_num * 8) * mult)
    atk = int((template["base_atk"] + floor_num * 2) * mult)
    defense = int((template["base_def"] + floor_num * 1.5) * mult)
    aspd = int((template["base_aspd"] + floor_num * 0.3))

    return Monster(
        name=template["name"],
        rarity=rarity,
        desc=template["desc"],
        hp=hp,
        atk=atk,
        defense=defense,
        aspd=aspd
    )

def roll_loot_rarity():
    roll = random.random()
    cumulative = 0

    for rarity, chance in LOOT_CHANCE.items():
        cumulative += chance
        if roll <= cumulative:
            return rarity
        
    return "Common"

def generate_loot():
    rarity = roll_loot_rarity()

    gear_slots = ["helmet", "chestplate", "gauntlets", "legs", "primary", "secondary", "accessory"]
    slot = random.choice(gear_slots)

    base_name = {
        "helmet": "Helm",
        "chestplate": "Armor",
        "gauntlets": "Gauntlets",
        "legs": "Greaves",
        "primary": "Weapon",
        "secondary": "Offhand",
        "accessory": "Relic"
    }[slot]

    name = f"{rarity} {base_name}"

    rarity_scaling = {
        "Common": 1,
        "Uncommon": 2,
        "Rare": 4,
        "Legendary": 6,
        "Mythical": 9,
        "MasterCraft": 14
    }

    stat_pool = ["atk", "defense", "intel", "faith", "luck", "aspd", "max_hp"]
    chosen_stat = random.choice(stat_pool)

    bonus_value = rarity_scaling[rarity] * random.randint(1, 3)
    bonuses = {chosen_stat: bonus_value}

    return Equipment(name, rarity, slot, bonuses)

def draw_lootwrapped_text(surface, text, font, color, x, y, max_width, rarity=None):
    words = text.split(" ")
    line = ""
    y_offset = 0

    draw_color = LOOT_COLORS.get(rarity, color) if rarity else color

    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            rendered = font.render(line, True, draw_color)
            surface.blit(rendered, (x, y + y_offset))
            y_offset += font.get_linesize() + 2
            line = word + " "

    if line:
        rendered = font.render(line, True, draw_color)
        surface.blit(rendered, (x, y + y_offset))

def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_spacing=4):
    words = text.split(" ")
    line = ""
    y_offset = 0

    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y + y_offset))
            y_offset += font.get_linesize() + line_spacing

    if line:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y + y_offset))

""" Combat System and Log """
def add_log(log, message, max_lines=6):
    log.append(message)
    if len(log) > max_lines:
        log.pop(0)

    pygame.time.delay(LOG_DELAY)

def calc_damage(attacker_atk, defender_def):
    dmg = attacker_atk - int(defender_def * 0.5)
    return max(1, dmg)

def combat(player, monster, title_surface, border_surface):
    player_meter = 0.0
    enemy_meter = 0.0
    waiting_for_player = False
    run_active = False
    auto_attack = False

    actions = ["Start Run", "Inventory", "Attack", "Run", "Quit"]
    action_index = 0

    combat_log = []
    add_log(combat_log, f"A {monster.rarity} {monster.name} appears!")
    add_log(combat_log, f'"{monster.desc}"')

    running = True

    while running:
        screen.fill(black)
        screen.blit(title_surface, (0, 0))
        screen.blit(border_surface, (0, 0))

        left_x = 80
        top_y = 260

        screen.blit(text_font.render("ENEMY", True, white), (left_x, top_y))
        screen.blit(text_font.render(f"{monster.name} ({monster.rarity})", True, white), (left_x, top_y + 40))
        screen.blit(text_font.render(f"HP: {monster.hp} / {monster.max_hp}", True, white), (left_x, top_y +80))

        right_x = screen.get_width() - 620

        screen.blit(text_font.render("PLAYER", True, white), (right_x, top_y))
        screen.blit(text_font.render (
            f"{player.name} - Lv {player.level} - {player.player_class}", True, white
        ), (right_x, top_y + 40))

        screen.blit(text_font.render(f"HP: {player.hp} / {player.max_hp}", True, white), (right_x, top_y + 80))
        screen.blit(text_font.render(
            f"ATK:{player.atk} DEF:{player.defense}    INT:{player.intel}", True, white
        ), (right_x, top_y + 120))
        screen.blit(text_font.render(
            f"FTH:{player.faith}  LCK:{player.luck}  ASPD:{player.aspd}", True, white
        ), (right_x, top_y + 160))
        screen.blit(text_font.render(f"Passive: {player.passive}", True, white), (right_x, top_y + 200))

        if auto_attack:
            screen.blit(text_font.render("AUTO-ATTACK: ON", True, white), (right_x, top_y + 240))

        log_x = 80
        log_y = screen.get_height() - 600
        max_log_width = screen.get_width() // 2 -140

        screen.blit(text_font.render("Combat Log:", True, white), (log_x, log_y))

        y = log_y + 40
        for entry in combat_log:
            if isinstance(entry, tuple):
                text, rarity = entry
                draw_lootwrapped_text(screen, text, text_font, white, log_x, y, max_log_width, rarity)
            else:
                draw_wrapped_text(screen, entry, text_font, white, log_x, y, max_log_width)

            y += text_font.get_linesize() * 1.4

            y += text_font.get_linesize() * 1.4

        actions_y = screen.get_height() - 340
        actions_x = screen.get_width() - 420

        for i, base_label in enumerate(actions):
            label = "Pause Run" if i == 0 and run_active else base_label
            color = black if i == action_index else white
            txt = menu_font.render(label, True, color)
            rect = txt.get_rect(center=(actions_x, actions_y + i * 50))

            if i == action_index:
                box = pygame.Rect(rect.x - 20, rect.y - 10, rect.width + 40, rect.height + 20)
                pygame.draw.rect(screen, highlight, box)

            screen.blit(txt, rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action_index = (action_index - 1) % len(actions)
                elif event.key == pygame.K_DOWN:
                    action_index = (action_index + 1) % len(actions)
                elif event.key == pygame.K_RETURN:
                    choice_idx = action_index

                    if choice_idx == 0:
                        run_active = not run_active
                        add_log(combat_log, "Run Started." if run_active else "Run Paused.")

                    elif choice_idx == 1:
                        open_inventory(player, title_surface, border_surface)
                        add_log(combat_log, "You Close your Inventory.")

                    elif choice_idx == 2:
                        if not run_active:
                            add_log(combat_log, "The Run is Paused.")
                        else:
                            auto_attack = not auto_attack
                            add_log(combat_log, f"Auto-Attack {'engaged' if auto_attack else 'disabled'}.")

                    elif choice_idx == 3:
                        if not run_active or not waiting_for_player:
                            add_log(combat_log, "You can't Flee Yet.")
                        else:
                            escape_chance = 0.4 + (player.luck * 0.01)
                            if random.random() < escape_chance:
                                add_log(combat_log, "You Escaped!")
                                time.sleep(1)
                                return "escaped"
                            else:
                                add_log(combat_log, "Escaped Failed!")
                                waiting_for_player = False

                    elif choice_idx == 4:
                        add_log(combat_log, "You Abandoned the Run.")
                        time.sleep(1)
                        return "quit_run"
                    
        if run_active and not waiting_for_player:
            player_meter += player.aspd
            enemy_meter += monster.aspd

        while enemy_meter >= 100 and player.hp > 0:
            dmg = calc_damage(monster.atk, player.defense)
            player.hp -= dmg
            add_log(combat_log, f"{monster.name} hits you for {dmg}!")
            enemy_meter -= 100

            if player.hp <= 0:
                add_log(combat_log, "You are Destroyed. . .")
                time.sleep(1.5)
                return "player_dead"
            
        if player_meter >= 100 and player.hp > 0:
            waiting_for_player = True

            if auto_attack:
                pygame.time.delay(220)

                atk_mult = 1.0

                if player.player_class == "Warrior" and random.random() < 0.20:
                    atk_mult = 1.5
                    add_log(combat_log, "Berserker Mode Activates!")

                if player.player_class == "Priest":
                    regen = max(1, int(player.faith * 0.25))
                    player.hp = min(player.max_hp, player.hp + regen)
                    add_log(combat_log, f"Divine Energy Restores {regen} HP.")

                dmg = calc_damage(int(player.atk * atk_mult), monster.defense)
                monster.hp -= dmg
                add_log(combat_log, f"You Strike {monster.name} for {dmg} Damage.")

                if monster.hp <= 0:
                    add_log(combat_log, f"{monster.name} is Destoryed!")

                    if player.player_class == "Mage" and random.random() < 0.10:
                        player.luck += 1
                        add_log(combat_log, "Arcane Insight! Luck Increased.")

                    exp_gained = RARITY_EXP.get(monster.rarity, 25)
                    player.gain_exp(exp_gained)
                    add_log(combat_log, f"You Gained {exp_gained} EXP!")

                    if random.random() < 0.55:
                        loot = generate_loot()
                        player.inventory.append(loot)

                        add_log(
                            combat_log,
                            f"LOOT DROPPED: {loot.name}",
                        )

                        combat_log.append(("LOOT", loot.rarity))

                    pygame.time.delay(600)
                    return "Victory"
                
                player_meter -= 100
                waiting_for_player = False
            
        clock.tick(60)

""" Dungeon Run System """
def start_dungeon_run(player, title_surface, border_surface):
    floor_num = 1

    while True:
        monster = generate_monster(floor_num)
        result = combat(player, monster, title_surface, border_surface)

        if player.stat_points > 0:
            allocate_stats(player, title_surface, border_surface)

        if result == "player_dead":
            screen.fill(black)
            screen.blit(title_surface, (0, 0))
            screen.blit(border_surface, (0, 0))

            over = menu_font.render("Game Over", True, white)
            screen.blit(over, (screen.get_width() // 2 - 120, 400))

            info = text_font.render("Press ENTER to return to Main Menu.", True, white)
            screen.blit(info, (screen.get_width() // 2 - 260, 400))

            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        return
                clock.tick(60)

        if result in ["quit_run", "escaped"]:
            return
        
        if result == "victory":
            floor_num += 1

""" Name Input """
def ask_player_name(title_surface, border_surface):
    name = ""
    active = True

    while active:
        screen.fill(black)
        screen.blit(title_surface, (0, 0))
        screen.blit(border_surface, (0, 0))

        prompt = menu_font.render("Enter Your Name:", True, white)
        screen.blit(prompt, (80, 300))

        name_txt = menu_font.render(name, True, highlight)
        screen.blit(name_txt, (80, 360))

        info = text_font.render("Press Enter to Confirm", True, white)
        screen.blit(info, (80, 420))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 16 and event.unicode.isprintable():
                        name += event.unicode

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)

""" New Game System """
def new_game(title_surface, border_surface):
    player_name = ask_player_name(title_surface, border_surface)

    class_choice = menu_selection(
        ["Warrior", "Mage", "Priest"],
        title_surface,
        border_surface,
        show_descriptions=True,
        current_name=player_name
    )

    player = Player(player_name, class_choice)
    start_dungeon_run(player, title_surface, border_surface)

""" Main Loop """
def main():
    title_surface = draw_ascii_title_surface()
    border_surface = create_border_surface()

    while True:
        choice = menu_selection(["New Game", "Quit"], title_surface, border_surface)

        if choice == "New Game":
            new_game(title_surface, border_surface)
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()