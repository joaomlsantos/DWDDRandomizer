from enum import Enum

class Species(Enum):
    HOLY = 0
    DARK = 1
    DRAGON = 2
    BEAST = 3
    BIRD = 4
    MACHINE = 5
    AQUAN = 6
    INSECTPLANT = 7


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
    unknown_0x3C: int

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
            self.unknown_0x3C = int.from_bytes(digimon_data[0x3c:0x40], byteorder="little")
        except:
            print("Exception on BaseDataDigimon call")
            return None

        


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
