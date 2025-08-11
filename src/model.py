from enum import Enum
from typing import List, Tuple

from . import constants

class Species(Enum):
    HOLY = 0
    DARK = 1
    DRAGON = 2
    BEAST = 3
    BIRD = 4
    MACHINE = 5
    AQUAN = 6
    INSECTPLANT = 7
    UNKNOWN = 8

class Element(Enum):
    LIGHT = 0
    DARK = 1
    FIRE = 2
    EARTH = 3
    WIND = 4
    STEEL = 5
    WATER = 6
    THUNDER = 7

# keeping these as constant dicts in model.py, setting it in constants.py would require constants.py to import model.py
ELEMENTAL_RESISTANCES = {
    Species.HOLY: Element.LIGHT,
    Species.DARK: Element.DARK,
    Species.DRAGON: Element.FIRE,
    Species.BEAST: Element.EARTH,
    Species.BIRD: Element.WIND,
    Species.MACHINE: Element.STEEL,
    Species.AQUAN: Element.WATER,
    Species.INSECTPLANT: Element.THUNDER
    }

ELEMENTAL_WEAKNESSES = {
    Species.HOLY: Element.DARK,
    Species.DARK: Element.LIGHT,
    Species.DRAGON: Element.EARTH,
    Species.BEAST: Element.FIRE,
    Species.BIRD: Element.THUNDER,
    Species.MACHINE: Element.WATER,
    Species.AQUAN: Element.STEEL,
    Species.INSECTPLANT: Element.WIND
    }

class DigimonType(Enum):
    BALANCE = 0
    ATTACKER = 1
    TANK = 2
    TECHNICAL = 3
    SPEED = 4
    HPTYPE = 5
    MPTYPE = 6


class LvlUpMode(Enum):
    RANDOM = 0
    FIXED_MIN = 1
    FIXED_AVG = 2
    FIXED_MAX = 3


class ItemType(Enum):
    NULL = 0
    FARM_ITEM = 1
    CONSUMABLE = 2
    EQUIPMENT = 3
    DIGIEGG = 4
    KEY_ITEM = 5


class SpriteMapEntry:
    offset: int
    id: int
    unknown_0x4: int
    main_sprite: int
    upperscreen_sprites: int

    def __init__(self, sprite_data: bytearray, offset: int):
        self.offset = offset
        self.id = int.from_bytes(sprite_data[0:4], byteorder="little")
        self.unknown_0x4 = int.from_bytes(sprite_data[4:8], byteorder="little")
        self.main_sprite = int.from_bytes(sprite_data[8:0xc], byteorder="little")
        self.upperscreen_sprites = int.from_bytes(sprite_data[0xc:0x10], byteorder="little")


class BattleStringEntry:
    offset: int
    value: int

    def __init__(self, offset: int, value: int):
        self.offset = offset
        self.value = value



class MoveData:
    offset: int
    id: int
    mp_cost: int
    element: Element
    special_identifier: int
    primary_effect: int
    primary_value: int
    secondary_effect: int
    secondary_value: int
    unknown_0xe: int
    is_consumable: int
    num_hits: int
    move_range: int
    unknown_0x14: int
    unknown_0x16: int
    level_learned: int
    eos_bytes: int

    def __init__(self, move_data: bytearray, offset: int):
        try:
            self.offset = offset
            self.id = int.from_bytes(move_data[0:2], byteorder="little")
            self.mp_cost = int.from_bytes(move_data[2:4], byteorder="little")
            self.element = Element(int.from_bytes(move_data[4], byteorder="little"))
            self.special_identifier = int.from_bytes(move_data[5], byteorder="little")
            self.primary_effect = int.from_bytes(move_data[6:8], byteorder="little")
            self.primary_value = int.from_bytes(move_data[8:0xa], byteorder="little")
            self.secondary_effect = int.from_bytes(move_data[0xa:0xc], byteorder="little")
            self.secondary_value = int.from_bytes(move_data[0xc:0xe], byteorder="little")
            self.unknown_0xe = int.from_bytes(move_data[0xe:0x10], byteorder="little")
            self.is_consumable = int.from_bytes(move_data[0x10:0x12], byteorder="little")
            self.num_hits = int.from_bytes(move_data[0x12], byteorder="little")
            self.move_range = int.from_bytes(move_data[0x13], byteorder="little")
            self.unknown_0x14 = int.from_bytes(move_data[0x14:0x16], byteorder="little")
            self.unknown_0x16 = int.from_bytes(move_data[0x16:0x18], byteorder="little")
            self.level_learned = int.from_bytes(move_data[0x18:0x1a], byteorder="little")
            self.eos_bytes = int.from_bytes(move_data[0x1a:0x1c], byteorder="little")
        except:
            print("Exception on MoveData call")
            return None



class BaseDataDigimon:
    offset: int
    id: int
    level: int
    species: Species
    hp: int
    mp: int
    attack: int
    defense: int
    spirit: int
    speed: int
    unknown_0x12: int
    aptitude: int
    light_res: int
    dark_res: int
    fire_res: int
    earth_res: int
    wind_res: int
    steel_res: int
    water_res: int
    thunder_res: int
    unknown_0x26: int
    trait_1: int
    trait_2: int
    trait_3: int
    trait_4: int
    support_trait: int
    digimon_type: DigimonType
    move_signature: int
    move_1: int
    move_2: int
    move_3: int
    move_4: int
    unknown_0x38: int
    unknown_0x3A: int
    exp_curve: int

    def __init__(self, digimon_data: bytearray, offset: int):
        try:
            self.offset = offset
            self.id = int.from_bytes(digimon_data[0:2], byteorder="little")
            self.level = digimon_data[2]
            self.species = digimon_data[3]
            self.hp = int.from_bytes(digimon_data[4:6], byteorder="little")
            self.mp = int.from_bytes(digimon_data[8:0xa], byteorder="little")
            self.attack = int.from_bytes(digimon_data[0xa:0xc], byteorder="little")
            self.defense = int.from_bytes(digimon_data[0xc:0xe], byteorder="little")
            self.spirit = int.from_bytes(digimon_data[0xe:0x10], byteorder="little")
            self.speed = int.from_bytes(digimon_data[0x10:0x12], byteorder="little")
            self.unknown_0x12 = int.from_bytes(digimon_data[0x12:0x14], byteorder="little")
            self.aptitude = int.from_bytes(digimon_data[0x14:0x16], byteorder="little")
            self.light_res = int.from_bytes(digimon_data[0x16:0x18], byteorder="little")
            self.dark_res = int.from_bytes(digimon_data[0x18:0x1a], byteorder="little")
            self.fire_res = int.from_bytes(digimon_data[0x1a:0x1c], byteorder="little")
            self.earth_res = int.from_bytes(digimon_data[0x1c:0x1e], byteorder="little")
            self.wind_res = int.from_bytes(digimon_data[0x1e:0x20], byteorder="little")
            self.steel_res = int.from_bytes(digimon_data[0x20:0x22], byteorder="little")
            self.water_res = int.from_bytes(digimon_data[0x22:0x24], byteorder="little")
            self.thunder_res = int.from_bytes(digimon_data[0x24:0x26], byteorder="little")
            self.unknown_0x26 = int.from_bytes(digimon_data[0x26:0x28], byteorder="little")
            self.trait_1 = digimon_data[0x28]
            self.trait_2 = digimon_data[0x29]
            self.trait_3 = digimon_data[0x2a]
            self.trait_4 = digimon_data[0x2b]
            self.support_trait = digimon_data[0x2c]
            self.digimon_type = digimon_data[0x2d]
            self.move_signature = int.from_bytes(digimon_data[0x2e:0x30], byteorder="little")
            self.move_1 = int.from_bytes(digimon_data[0x30:0x32], byteorder="little")
            self.move_2 = int.from_bytes(digimon_data[0x32:0x34], byteorder="little")
            self.move_3 = int.from_bytes(digimon_data[0x34:0x36], byteorder="little")
            self.move_4 = int.from_bytes(digimon_data[0x36:0x38], byteorder="little")
            self.unknown_0x38 = int.from_bytes(digimon_data[0x38:0x3a], byteorder="little")
            self.unknown_0x3A = int.from_bytes(digimon_data[0x3a:0x3c], byteorder="little")
            self.exp_curve = int.from_bytes(digimon_data[0x3c:0x40], byteorder="little")             # this is 0 by default for all digimon, can also be 1 or 2 logically
        except:
            print("Exception on BaseDataDigimon call")
            return None
        

    def getBaseStats(self):
        return [self.hp,
                self.mp,
                self.attack,
                self.defense,
                self.spirit,
                self.speed,
                self.aptitude]
    
    def setBaseStats(self, stats_array: List[int]):
        # check if stats_array has exactly 7 values
        if(len(stats_array) != 7):
            print(f"Resistance array {stats_array} does not have exactly 7 values; skipping operation")
            return
        
        stat_attrs = ["hp", "mp", "attack", "defense", "spirit", "speed", "aptitude"]
        for i, attr in enumerate(stat_attrs):
            # skip value if -1: this is used to skip certain base stat values that are already set
            if(stat_attrs[i] == -1):
                continue
            setattr(self, attr, stat_attrs[i])





    # same order as Element class
    def getResistanceValues(self):
        return [self.light_res, 
                self.dark_res, 
                self.fire_res, 
                self.earth_res,
                self.wind_res, 
                self.steel_res, 
                self.water_res, 
                self.thunder_res]
    
    def setResistanceValues(self, resistance_array: List[int]):
        # check if resistance_array has exactly 8 values
        if(len(resistance_array) != 8):
            print(f"Resistance array {resistance_array} does not have exactly 8 values; skipping operation")
            return
        resistance_attrs = ["light_res", "dark_res", "fire_res", "earth_res", "wind_res", "steel_res", "water_res", "thunder_res"]
        for i, attr in enumerate(resistance_attrs):
            # skip value if -1: this is used to skip certain resistance values that are already set
            if(resistance_array[i] == -1):
                continue
            setattr(self, attr, resistance_array[i])

        


class EnemyDataDigimon:
    offset: int
    id: int
    level: int
    species: Species
    hp: int
    mp: int
    attack: int
    defense: int
    spirit: int
    speed: int
    unknown_0x12: int
    light_res: int
    dark_res: int
    fire_res: int
    earth_res: int
    wind_res: int
    steel_res: int
    water_res: int
    thunder_res: int
    unknown_0x24: int
    trait_1: int
    trait_2: int
    trait_3: int
    trait_4: int
    move_signature: int
    move_1: int
    move_2: int
    move_3: int
    move_4: int
    unknown_0x38: int
    unknown_0x39: int
    unknown_0x3A: int
    unknown_0x3B: int
    holy_exp: int
    dark_exp: int
    dragon_exp: int
    beast_exp: int
    bird_exp: int
    machine_exp: int
    aquan_exp: int
    insectplant_exp: int
    unknown_0x5C: int
    unknown_0x60: int
    unknown_0x64: int
    unknown_0x68: int


    def __init__(self, digimon_data: bytearray, offset: int):
        try:
            self.offset = offset
            self.id = int.from_bytes(digimon_data[0:2], byteorder="little")
            self.level = digimon_data[2]
            self.species = digimon_data[3]
            self.hp = int.from_bytes(digimon_data[4:6], byteorder="little")
            self.mp = int.from_bytes(digimon_data[8:0xa], byteorder="little")
            self.attack = int.from_bytes(digimon_data[0xa:0xc], byteorder="little")
            self.defense = int.from_bytes(digimon_data[0xc:0xe], byteorder="little")
            self.spirit = int.from_bytes(digimon_data[0xe:0x10], byteorder="little")
            self.speed = int.from_bytes(digimon_data[0x10:0x12], byteorder="little")
            self.unknown_0x12 = int.from_bytes(digimon_data[0x12:0x14], byteorder="little")
            self.light_res = int.from_bytes(digimon_data[0x14:0x16], byteorder="little")
            self.dark_res = int.from_bytes(digimon_data[0x16:0x18], byteorder="little")
            self.fire_res = int.from_bytes(digimon_data[0x18:0x1a], byteorder="little")
            self.earth_res = int.from_bytes(digimon_data[0x1a:0x1c], byteorder="little")
            self.wind_res = int.from_bytes(digimon_data[0x1c:0x1e], byteorder="little")
            self.steel_res = int.from_bytes(digimon_data[0x1e:0x20], byteorder="little")
            self.water_res = int.from_bytes(digimon_data[0x20:0x22], byteorder="little")
            self.thunder_res = int.from_bytes(digimon_data[0x22:0x24], byteorder="little")
            self.unknown_0x24 = int.from_bytes(digimon_data[0x24:0x26], byteorder="little")
            self.trait_1 = int.from_bytes(digimon_data[0x26:0x28], byteorder="little")
            self.trait_2 = int.from_bytes(digimon_data[0x28:0x2a], byteorder="little")
            self.trait_3 = int.from_bytes(digimon_data[0x2a:0x2c], byteorder="little")
            self.trait_4 = int.from_bytes(digimon_data[0x2c:0x2e], byteorder="little")
            self.move_signature = int.from_bytes(digimon_data[0x2e:0x30], byteorder="little")
            self.move_1 = int.from_bytes(digimon_data[0x30:0x32], byteorder="little")
            self.move_2 = int.from_bytes(digimon_data[0x32:0x34], byteorder="little")
            self.move_3 = int.from_bytes(digimon_data[0x34:0x36], byteorder="little")
            self.move_4 = int.from_bytes(digimon_data[0x36:0x38], byteorder="little")
            self.unknown_0x38 = digimon_data[0x38]
            self.unknown_0x39 = digimon_data[0x39]
            self.unknown_0x3A = digimon_data[0x3a]
            self.unknown_0x3B = digimon_data[0x3b]
            self.holy_exp = int.from_bytes(digimon_data[0x3c:0x40], byteorder="little")
            self.dark_exp = int.from_bytes(digimon_data[0x40:0x44], byteorder="little")
            self.dragon_exp = int.from_bytes(digimon_data[0x44:0x48], byteorder="little")
            self.beast_exp = int.from_bytes(digimon_data[0x48:0x4c], byteorder="little")
            self.bird_exp = int.from_bytes(digimon_data[0x4c:0x50], byteorder="little")
            self.machine_exp = int.from_bytes(digimon_data[0x50:0x54], byteorder="little")
            self.aquan_exp = int.from_bytes(digimon_data[0x54:0x58], byteorder="little")
            self.insectplant_exp = int.from_bytes(digimon_data[0x58:0x5c], byteorder="little")
            self.unknown_0x5C = int.from_bytes(digimon_data[0x5c:0x60], byteorder="little")
            self.unknown_0x60 = int.from_bytes(digimon_data[0x60:0x64], byteorder="little")
            self.unknown_0x64 = int.from_bytes(digimon_data[0x64:0x68], byteorder="little")
            self.unknown_0x68 = int.from_bytes(digimon_data[0x68:0x6c], byteorder="little")

        except:
            print("Exception on EnemyDataDigimon call")
            return None

    def getTotalExp(self):
        return self.holy_exp + self.dark_exp + self.dragon_exp + self.beast_exp + self.bird_exp + self.machine_exp + self.aquan_exp + self.insectplant_exp
    
    # this assumes that only the corresponding species exp is supposed to be updated
    def updateExpYield(self, exp_yield):
        for exp_species in ["holy_exp", "dark_exp", "dragon_exp", "beast_exp", "bird_exp", "machine_exp", "aquan_exp", "insectplant_exp"]:
            if getattr(self, exp_species) > 0:
                setattr(self, exp_species, exp_yield)

    def setResistanceValues(self, resistance_array: List[int]):
        # check if resistance_array has exactly 8 values
        if(len(resistance_array) != 8):
            print(f"Resistance array {resistance_array} does not have exactly 8 values; skipping operation")
            return
        resistance_attrs = ["light_res", "dark_res", "fire_res", "earth_res", "wind_res", "steel_res", "water_res", "thunder_res"]
        for i, attr in enumerate(resistance_attrs):
            # skip value if -1: this is used to skip certain resistance values that are already set
            if(resistance_array[i] == -1):
                continue
            setattr(self, attr, resistance_array[i])



class FarmTerrain:
    offset: int
    id: int
    unknown_0x2: int
    farm_digimon_limit: int
    unknown_0x6: int
    unknown_0x8: int
    unknown_0xA: int
    unknown_0xC: int
    unknown_0xE: int
    unknown_0x10: int
    unknown_0x12: int
    unknown_0x14: int
    unknown_0x16: int
    unknown_0x18: int
    unknown_0x1A: int
    unknown_0x1C: int
    unknown_0x1E: int
    unknown_0x20: int
    unknown_0x22: int
    unknown_0x24: int
    unknown_0x26: int
    unknown_0x28: int
    unknown_0x2A: int
    unknown_0x2C: int
    unknown_0x2E: int
    unknown_0x30: int
    unknown_0x32: int
    unknown_0x34: int
    unknown_0x36: int
    unknown_0x38: int
    unknown_0x3A: int
    unknown_0x3C: int
    unknown_0x3E: int
    unknown_0x40: int
    unknown_0x42: int
    unknown_0x44: int
    unknown_0x46: int
    unknown_0x48: int
    unknown_0x4A: int
    holy_exp: int
    dark_exp: int
    dragon_exp: int
    beast_exp: int
    bird_exp: int
    machine_exp: int
    aquan_exp: int
    insectplant_exp: int

    def __init__(self, digimon_data: bytearray, offset: int):
        try:
            self.offset = offset
            self.id = int.from_bytes(digimon_data[0:2], byteorder="little")
            self.unknown_0x2 = int.from_bytes(digimon_data[2:0x4], byteorder="little")
            self.farm_digimon_limit = int.from_bytes(digimon_data[4:6], byteorder="little")
            self.unknown_0x6 = int.from_bytes(digimon_data[6:0x8], byteorder="little")
            self.unknown_0x8 = int.from_bytes(digimon_data[8:0xa], byteorder="little")
            self.unknown_0xA = int.from_bytes(digimon_data[0xa:0xc], byteorder="little")
            self.unknown_0xC = int.from_bytes(digimon_data[0xc:0xe], byteorder="little")
            self.unknown_0xE = int.from_bytes(digimon_data[0xe:0x10], byteorder="little")
            self.unknown_0x10 = int.from_bytes(digimon_data[0x10:0x12], byteorder="little")
            self.unknown_0x12 = int.from_bytes(digimon_data[0x12:0x14], byteorder="little")
            self.unknown_0x14 = int.from_bytes(digimon_data[0x14:0x16], byteorder="little")
            self.unknown_0x16 = int.from_bytes(digimon_data[0x16:0x18], byteorder="little")
            self.unknown_0x18 = int.from_bytes(digimon_data[0x18:0x1a], byteorder="little")
            self.unknown_0x1A = int.from_bytes(digimon_data[0x1a:0x1c], byteorder="little")
            self.unknown_0x1C = int.from_bytes(digimon_data[0x1c:0x1e], byteorder="little")
            self.unknown_0x1E = int.from_bytes(digimon_data[0x1e:0x20], byteorder="little")
            self.unknown_0x20 = int.from_bytes(digimon_data[0x20:0x22], byteorder="little")
            self.unknown_0x22 = int.from_bytes(digimon_data[0x22:0x24], byteorder="little")
            self.unknown_0x24 = int.from_bytes(digimon_data[0x24:0x26], byteorder="little")
            self.unknown_0x26 = int.from_bytes(digimon_data[0x26:0x28], byteorder="little")
            self.unknown_0x28 = int.from_bytes(digimon_data[0x28:0x2a], byteorder="little")
            self.unknown_0x2A = int.from_bytes(digimon_data[0x2a:0x2c], byteorder="little")
            self.unknown_0x2C = int.from_bytes(digimon_data[0x2c:0x2e], byteorder="little")
            self.unknown_0x2E = int.from_bytes(digimon_data[0x2e:0x30], byteorder="little")
            self.unknown_0x30 = int.from_bytes(digimon_data[0x30:0x32], byteorder="little")
            self.unknown_0x32 = int.from_bytes(digimon_data[0x32:0x34], byteorder="little")
            self.unknown_0x34 = int.from_bytes(digimon_data[0x34:0x36], byteorder="little")
            self.unknown_0x36 = int.from_bytes(digimon_data[0x36:0x38], byteorder="little")
            self.unknown_0x38 = int.from_bytes(digimon_data[0x38:0x3A], byteorder="little")
            self.unknown_0x3A = int.from_bytes(digimon_data[0x3A:0x3C], byteorder="little")
            self.unknown_0x3C = int.from_bytes(digimon_data[0x3C:0x3E], byteorder="little")
            self.unknown_0x3E = int.from_bytes(digimon_data[0x3E:0x40], byteorder="little")
            self.unknown_0x40 = int.from_bytes(digimon_data[0x40:0x42], byteorder="little")
            self.unknown_0x42 = int.from_bytes(digimon_data[0x42:0x44], byteorder="little")
            self.unknown_0x44 = int.from_bytes(digimon_data[0x44:0x46], byteorder="little")
            self.unknown_0x46 = int.from_bytes(digimon_data[0x46:0x48], byteorder="little")
            self.unknown_0x48 = int.from_bytes(digimon_data[0x48:0x4A], byteorder="little")
            self.unknown_0x4A = int.from_bytes(digimon_data[0x4A:0x4C], byteorder="little")
            self.holy_exp = int.from_bytes(digimon_data[0x4C:0x4E], byteorder="little")
            self.dark_exp = int.from_bytes(digimon_data[0x4E:0x50], byteorder="little")
            self.dragon_exp = int.from_bytes(digimon_data[0x50:0x52], byteorder="little")
            self.beast_exp = int.from_bytes(digimon_data[0x52:0x54], byteorder="little")
            self.bird_exp = int.from_bytes(digimon_data[0x54:0x56], byteorder="little")
            self.machine_exp = int.from_bytes(digimon_data[0x56:0x58], byteorder="little")
            self.aquan_exp = int.from_bytes(digimon_data[0x58:0x5A], byteorder="little")
            self.insectplant_exp = int.from_bytes(digimon_data[0x5A:0x5c], byteorder="little")

        except:
            print("Exception on FarmTerrain call")
            return None



class StandardDigivolution:
    offset: int
    digimon_id: int

    # declare any other local properties before the ROM properties, otherwise this will mess up the load w/ __annotations__
    degen_evo_id: int
    evolution_1_id: int
    evolution_2_id: int
    evolution_3_id: int
    degen_condition_id_1: int
    degen_condition_value_1: int
    degen_condition_id_2: int
    degen_condition_value_2: int
    degen_condition_id_3: int
    degen_condition_value_3: int
    evo_1_condition_id_1: int
    evo_1_condition_value_1: int
    evo_1_condition_id_2: int
    evo_1_condition_value_2: int
    evo_1_condition_id_3: int
    evo_1_condition_value_3: int
    evo_2_condition_id_1: int
    evo_2_condition_value_1: int
    evo_2_condition_id_2: int
    evo_2_condition_value_2: int
    evo_2_condition_id_3: int
    evo_2_condition_value_3: int
    evo_3_condition_id_1: int
    evo_3_condition_value_1: int
    evo_3_condition_id_2: int
    evo_3_condition_value_2: int
    evo_3_condition_id_3: int
    evo_3_condition_value_3: int
    
    def __init__(self, digivolution_data: bytearray, offset: int, digimon_id: int):
        self.offset = offset
        self.digimon_id = digimon_id

    	# have this in order to skip offset
        local_properties = ["offset"]

        # we can do this since self.__annotations__ maintains the order of the properties
        property_names = [x for x in self.__annotations__ if x not in local_properties]


        # every attr from digivolution_data corresponds to 4 bytes
        for i, prop_name in enumerate(property_names):
            setattr(self, prop_name, int.from_bytes(digivolution_data[i*4:(i*4)+4], byteorder="little"))

        '''
        # keeping this for clarity, might replace the setattr iterator if it makes sense
        # old load was done like this:

        self.degen_evo_id = int.from_bytes(digivolution_data[0:4], byteorder="little")
        self.evolution_1_id = int.from_bytes(digivolution_data[4:8], byteorder="little")
        self.evolution_2_id = int.from_bytes(digivolution_data[8:0xc], byteorder="little")
        self.evolution_3_id = int.from_bytes(digivolution_data[0xc:0x10], byteorder="little")
        self.degen_condition_id_1 = int.from_bytes(digivolution_data[0x10:0x14], byteorder="little")
        self.degen_condition_value_1 = int.from_bytes(digivolution_data[0x14:0x18], byteorder="little")
        self.degen_condition_id_2 = int.from_bytes(digivolution_data[0x18:0x1c], byteorder="little")
        self.degen_condition_value_2 = int.from_bytes(digivolution_data[0x1c:0x20], byteorder="little")
        self.degen_condition_id_3 = int.from_bytes(digivolution_data[0x20:0x24], byteorder="little")
        self.degen_condition_value_3 = int.from_bytes(digivolution_data[0x24:0x28], byteorder="little")
        self.evo_1_condition_id_1 = int.from_bytes(digivolution_data[0x28:0x2c], byteorder="little")
        self.evo_1_condition_value_1 = int.from_bytes(digivolution_data[0x2c:0x30], byteorder="little")
        self.evo_1_condition_id_2 = int.from_bytes(digivolution_data[0x30:0x34], byteorder="little")
        self.evo_1_condition_value_2 = int.from_bytes(digivolution_data[0x34:0x38], byteorder="little")
        self.evo_1_condition_id_3 = int.from_bytes(digivolution_data[0x38:0x3c], byteorder="little")
        self.evo_1_condition_value_3 = int.from_bytes(digivolution_data[0x3c:0x40], byteorder="little")
        self.evo_2_condition_id_1 = int.from_bytes(digivolution_data[0x40:0x44], byteorder="little")
        self.evo_2_condition_value_1 = int.from_bytes(digivolution_data[0x44:0x48], byteorder="little")
        self.evo_2_condition_id_2 = int.from_bytes(digivolution_data[0x48:0x4c], byteorder="little")
        self.evo_2_condition_value_2 = int.from_bytes(digivolution_data[0x4c:0x50], byteorder="little")
        self.evo_2_condition_id_3 = int.from_bytes(digivolution_data[0x50:0x54], byteorder="little")
        self.evo_2_condition_value_3 = int.from_bytes(digivolution_data[0x54:0x58], byteorder="little")
        self.evo_3_condition_id_1 = int.from_bytes(digivolution_data[0x58:0x5c], byteorder="little")
        self.evo_3_condition_value_1 = int.from_bytes(digivolution_data[0x5c:0x60], byteorder="little")
        self.evo_3_condition_id_2 = int.from_bytes(digivolution_data[0x60:0x64], byteorder="little")
        self.evo_3_condition_value_2 = int.from_bytes(digivolution_data[0x64:0x68], byteorder="little")
        self.evo_3_condition_id_3 = int.from_bytes(digivolution_data[0x68:0x6c], byteorder="little")
        self.evo_3_condition_value_3 = int.from_bytes(digivolution_data[0x6c:0x70], byteorder="little")
        '''



class ArmorDigivolution:
    offset: int
    digimon_id: int
    item_id: int
    evolution_id: int
    condition_id_1: int
    condition_value_1: int
    condition_id_2: int
    condition_value_2: int
    condition_id_3: int
    condition_value_3: int
    degen_condition_id: int
    degen_condition_value: int
    
    def __init__(self, digivolution_data: bytearray, offset: int):
        self.offset = offset
        self.digimon_id = int.from_bytes(digivolution_data[0:4], byteorder="little")
        self.item_id = int.from_bytes(digivolution_data[4:8], byteorder="little")
        self.evolution_id = int.from_bytes(digivolution_data[8:0xc], byteorder="little")
        self.condition_id_1 = int.from_bytes(digivolution_data[0xc:0x10], byteorder="little")
        self.condition_value_1 = int.from_bytes(digivolution_data[0x10:0x14], byteorder="little")
        self.condition_id_2 = int.from_bytes(digivolution_data[0x14:0x18], byteorder="little")
        self.condition_value_2 = int.from_bytes(digivolution_data[0x18:0x1c], byteorder="little")
        self.condition_id_3 = int.from_bytes(digivolution_data[0x1c:0x20], byteorder="little")
        self.condition_value_3 = int.from_bytes(digivolution_data[0x20:0x24], byteorder="little")
        self.degen_condition_id = int.from_bytes(digivolution_data[0x24:0x28], byteorder="little")
        self.degen_condition_value = int.from_bytes(digivolution_data[0x28:0x2c], byteorder="little")


class DNADigivolution:
    offset: int
    digimon_1_id: int
    digimon_2_id: int
    dna_evolution_id: int
    condition_id_1: int
    condition_value_1: int
    condition_id_2: int
    condition_value_2: int
    condition_id_3: int
    condition_value_3: int
    

    def __init__(self, digivolution_data: bytearray, offset: int):
        self.offset = offset
        self.digimon_1_id = int.from_bytes(digivolution_data[0:4], byteorder="little")
        self.digimon_2_id = int.from_bytes(digivolution_data[4:8], byteorder="little")
        self.dna_evolution_id = int.from_bytes(digivolution_data[8:0xc], byteorder="little")
        self.condition_id_1 = int.from_bytes(digivolution_data[0xc:0x10], byteorder="little")
        self.condition_value_1 = int.from_bytes(digivolution_data[0x10:0x14], byteorder="little")
        self.condition_id_2 = int.from_bytes(digivolution_data[0x14:0x18], byteorder="little")
        self.condition_value_2 = int.from_bytes(digivolution_data[0x18:0x1c], byteorder="little")
        self.condition_id_3 = int.from_bytes(digivolution_data[0x1c:0x20], byteorder="little")
        self.condition_value_3 = int.from_bytes(digivolution_data[0x20:0x24], byteorder="little")


    # this removes the requirements for the given DNA digivolution -> to DNA digivolve, you will only need to select the two required digimon
    def removeRequirements(self):
        self.condition_id_1 = 0x1       # digivolution condition -> level
        self.condition_value_1 = 0x1      # condition value -> level 1
        self.condition_id_2 = 0x0
        self.condition_value_2 = 0x0
        self.condition_id_3 = 0x0
        self.condition_value_3 = 0x0

    def getConditionsArray(self):
        return [[self.condition_id_1, self.condition_value_1], [self.condition_id_2, self.condition_value_2], [self.condition_id_3, self.condition_value_3]]
    
    def setConditionsFromArray(self, conditionsArray: List[Tuple[int,int]]):
        self.condition_id_1 = conditionsArray[0][0]
        self.condition_value_1 = conditionsArray[0][1]
        self.condition_id_2 = conditionsArray[1][0]
        self.condition_value_2 = conditionsArray[1][1]
        self.condition_id_3 = conditionsArray[2][0]
        self.condition_value_3 = conditionsArray[2][1]

    def getDnaDigivolutionLog(self):
        digimon_1_str = constants.DIGIMON_ID_TO_STR[self.digimon_1_id]
        digimon_2_str = constants.DIGIMON_ID_TO_STR[self.digimon_2_id]
        dna_digivolution_str = constants.DIGIMON_ID_TO_STR[self.dna_evolution_id]
        cur_str = f"{dna_digivolution_str} = {digimon_1_str} + {digimon_2_str} ["

        condition_strs = []
        for condition_pair in self.getConditionsArray():
            if(condition_pair[0] != 0):
                cur_condition_str = constants.DIGIVOLUTION_CONDITIONS[condition_pair[0]]
                condition_strs.append(f"{cur_condition_str} {condition_pair[1]}")

        cur_str += ", ".join(condition_strs) + "]"
        return cur_str

    def writeDnaDigivolutionToRom(self, rom_data: bytearray):
        fields = [
            ("digimon_1_id", 0x0),
            ("digimon_2_id", 0x4),
            ("dna_evolution_id", 0x8),
            ("condition_id_1", 0xc),
            ("condition_value_1", 0x10),
            ("condition_id_2", 0x14),
            ("condition_value_2", 0x18),
            ("condition_id_3", 0x1c),
            ("condition_value_3", 0x20)
        ]

        for attr, offset in fields:
            value = getattr(self, attr)
            rom_data[self.offset + offset : self.offset + offset + 4] = value.to_bytes(4, byteorder="little")
        