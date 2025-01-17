from typing import List
from . import constants
from . import model
import copy
import random
import numpy as np
from collections import Counter


def getDigimonStage(digimon_id: int):
    if(digimon_id >= 0x41 and digimon_id <= 0x57):
        return "IN-TRAINING"
    if(digimon_id >= 0x61 and digimon_id <= 0x9D):
        return "ROOKIE"
    if(digimon_id >= 0xA8 and digimon_id <= 0x115 and digimon_id != 0xBA):
        return "CHAMPION"
    if(digimon_id >= 0x120 and digimon_id <= 0x188):
        return "ULTIMATE"
    if(digimon_id >= 0x191 and digimon_id <= 0x1F4):
        return "MEGA"
    return ""


def getDigimonStageFromSpriteInfo(sprite_val: int):
    if(sprite_val >= 0x01 and sprite_val <= 0x17):
        return "IN-TRAINING"
    if(sprite_val >= 0x18 and sprite_val <= 0x54):
        return "ROOKIE"
    if(sprite_val >= 0x55 and sprite_val <= 0xC1):
        return "CHAMPION"
    if(sprite_val >= 0xC2 and sprite_val <= 0x12A):
        return "ULTIMATE"
    if(sprite_val >= 0x12B and sprite_val <= 0x18E):
        return "MEGA"
    if(sprite_val == 0x190):
        return "JOINT_SLOT_BOSS"
    if(sprite_val >= 0x18E and sprite_val <= 0x19E):
        return "BATTLE_EXCLUSIVE"
    return ""



def getAllDigimonPairs():
    digimon_pairs = []
    for stage in constants.DIGIMON_IDS.keys():
        digimon_pairs += list(constants.DIGIMON_IDS[stage].items())
        
    return digimon_pairs



def loadBaseDigimonInfo(version: str, 
                        rom_data: bytearray):
    offset_start = constants.BASE_DIGIMON_OFFSETS[version][0]
    offset_end = constants.BASE_DIGIMON_OFFSETS[version][1]

    seek_offset = offset_start

    base_digimon_dict = {}
    
    while(seek_offset <= offset_end):
        cur_offset = seek_offset
        header_skip = int.from_bytes(rom_data[cur_offset:cur_offset+4], byteorder="little")
        cur_offset += header_skip   # skip header
        
        cur_digimon_data = rom_data[cur_offset:cur_offset+0x44]
        cur_digimon_id = int.from_bytes(cur_digimon_data[0:2], byteorder="little")
        
        while(cur_digimon_id != 0xffff and cur_offset < seek_offset + 0x400):
            cur_base_digimon = model.BaseDataDigimon(cur_digimon_data, cur_offset)
            base_digimon_dict[cur_digimon_id] = cur_base_digimon
            cur_offset += 0x44
            cur_digimon_data = rom_data[cur_offset:cur_offset+0x44]
            cur_digimon_id = int.from_bytes(cur_digimon_data[0:2], byteorder="little")

        seek_offset += 0x400    # skip 400 (hex) to reach the next base digimon address

    return base_digimon_dict



def loadEnemyDigimonInfo(version: str, 
                         rom_data: bytearray):
    offset_start = constants.ENEMY_DIGIMON_OFFSETS[version][0]
    offset_end = constants.ENEMY_DIGIMON_OFFSETS[version][1]

    seek_offset = offset_start

    enemy_digimon_dict = {}
    
    while(seek_offset <= offset_end):
        cur_offset = seek_offset
        header_skip = int.from_bytes(rom_data[cur_offset:cur_offset+4], byteorder="little")
        cur_offset += header_skip   # skip header
        
        cur_digimon_data = rom_data[cur_offset:cur_offset+0x6c]
        cur_digimon_id = int.from_bytes(cur_digimon_data[0:2], byteorder="little")
        
        while(cur_digimon_id != 0xffff and cur_offset < seek_offset + 0x400):
            cur_enemy_digimon = model.EnemyDataDigimon(cur_digimon_data, cur_offset)
            enemy_digimon_dict[cur_digimon_id] = cur_enemy_digimon

            cur_offset += 0x6c
            cur_digimon_data = rom_data[cur_offset:cur_offset+0x6c]
            cur_digimon_id = int.from_bytes(cur_digimon_data[0:2], byteorder="little")

        seek_offset += 0x400    # skip 400 (hex) to reach the next base digimon address

    return enemy_digimon_dict



def loadSpriteMapTable(version: str,
                       rom_data: bytearray):
    offset_start = constants.SPRITE_MAPPING_TABLE_OFFSET[version][0]
    offset_end = constants.SPRITE_MAPPING_TABLE_OFFSET[version][1]

    spriteMapTable = []     # this can be an array since it's mapped 1-to-1 sequentially for every digimon id

    seek_offset = offset_start

    while(seek_offset <= offset_end):
        cur_digimon_data = rom_data[seek_offset:seek_offset+0x10]
        cur_sprite_entry = model.SpriteMapEntry(cur_digimon_data, seek_offset)
        spriteMapTable.append(cur_sprite_entry)

        seek_offset += 0x10
    
    return spriteMapTable


def loadBattleStringTable(version: str,
                          rom_data: bytearray):
    offset_start = constants.STRING_BATTLE_TABLE_OFFSET[version][0]
    offset_end = constants.STRING_BATTLE_TABLE_OFFSET[version][1]

    battleStringTable = []     # this can be an array since it's mapped 1-to-1 sequentially for every digimon id
    seek_offset = offset_start

    while(seek_offset <= offset_end):
        cur_strtable_entry = model.BattleStringEntry(seek_offset, int.from_bytes(rom_data[seek_offset:seek_offset+4], byteorder="little"))
        battleStringTable.append(cur_strtable_entry)
        seek_offset += 4

    return battleStringTable


    




def loadLvlupTypeTable(version: str, 
                       rom_data: bytearray):
    offset = constants.LVLUP_TYPE_TABLE_OFFSET[version]
    lvlupTable = []
    cur_offset = offset
    for i in range(7):      # 7 types
        cur_type_array = []
        cur_type_array.append([rom_data[cur_offset], rom_data[cur_offset+1]])       # hp
        cur_type_array.append([rom_data[cur_offset+2], rom_data[cur_offset+3]])     # mp
        cur_type_array.append([rom_data[cur_offset+4], rom_data[cur_offset+5]])     # atk
        cur_type_array.append([rom_data[cur_offset+6], rom_data[cur_offset+7]])     # def
        cur_type_array.append([rom_data[cur_offset+8], rom_data[cur_offset+9]])     # spirit
        cur_type_array.append([rom_data[cur_offset+0xa], rom_data[cur_offset+0xb]])   # speed
        lvlupTable.append(cur_type_array)
        cur_offset += 0xc
    
    return lvlupTable



def generateLvlupStats(lvlupTable: list[list[int, int]], 
                       digimon_data: model.BaseDataDigimon, 
                       target_lvl: int, 
                       mode: model.LvlUpMode=model.LvlUpMode.RANDOM ):
    
    # note: this function is not checking if the aptitude is valid for the given digimon


    lvlupRef = lvlupTable[digimon_data.digimon_type]    # pick specific table for this digimon type
    target_digimon: model.BaseDataDigimon = copy.copy(digimon_data)     # we do not want to change the original ref, thus the copy

    prev_stats = [target_digimon.hp, target_digimon.mp, target_digimon.attack, target_digimon.defense, target_digimon.spirit, target_digimon.speed]

    for i in range(target_digimon.level, target_lvl):
        for stat in range(len(prev_stats)):
            left_operand = -1

            if(mode == model.LvlUpMode.RANDOM):
                left_operand = random.randint(1, lvlupRef[stat][0])
            if(mode == model.LvlUpMode.FIXED_MIN):
                left_operand = 1
            if(mode == model.LvlUpMode.FIXED_AVG):
                left_operand = max(1, (1+lvlupRef[stat][0])//2)     # max() to ensure that it's atleast 1
            if(mode == model.LvlUpMode.FIXED_MAX):
                left_operand = lvlupRef[stat][0]

            prev_stats[stat] += (left_operand + lvlupRef[stat][1]) // 10
    

    target_digimon.level = target_lvl
    target_digimon.hp = prev_stats[0]
    target_digimon.mp = prev_stats[1]
    target_digimon.attack = prev_stats[2]
    target_digimon.defense = prev_stats[3]
    target_digimon.spirit = prev_stats[4]
    target_digimon.speed = prev_stats[5]

    return target_digimon


def generateConditions(s: int):
    
    stage = constants.STAGE_NAMES[s]
    digivolution_conditions_pool = [0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF, 0x12]    # this should be a constant/setting i think
    condition_amount_distribution = constants.DIGIVOLUTION_CONDITION_AMOUNT_DISTRIBUTION[stage]
    condition_amount = np.random.choice(list(range(1,len(condition_amount_distribution)+1)), p=condition_amount_distribution)
    conditions = []
    for c in range(1, condition_amount+1):
        if(c == 1):     # force level
            cur_condition = 0x1
        else:           # choose one of the other conditions randomly
            cur_condition = random.choice(digivolution_conditions_pool)
            digivolution_conditions_pool.remove(cur_condition)

        min_val = constants.DIGIVOLUTION_CONDITIONS_VALUES[cur_condition][s][0]
        max_val = constants.DIGIVOLUTION_CONDITIONS_VALUES[cur_condition][s][1]
        conditions.append([cur_condition, random.randint(min_val, max_val)])
    return conditions



def generateBiasedConditions(stage_id: int, bias: float, species: int):
    '''
    0x2: "DRAGON EXP",                      HOLY = 0
    0x3: "BEAST EXP",                       DARK = 1
    0x4: "AQUAN EXP",                       DRAGON = 2
    0x5: "BIRD EXP",                        BEAST = 3
    0x6: "INSECTPLANT EXP",                 BIRD = 4
    0x7: "MACHINE EXP",                     MACHINE = 5
    0x8: "DARK EXP",                        AQUAN = 6
    0x9: "HOLY EXP",                        INSECTPLANT = 7
    '''

    stage = constants.STAGE_NAMES[stage_id]
    digivolution_conditions_pool = [0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF, 0x12]    # this should be a constant/setting i think
    species_condition_mapping = {0: 0x9, 1: 0x8, 2: 0x2, 3: 0x3, 4: 0x5, 5: 0x7, 6: 0x4, 7: 0x6}
    species_exp = species_condition_mapping[species]
    other_species_total = 7
    non_species_exp_conditions_count = len(digivolution_conditions_pool) - other_species_total      # assuming 7 can be a fixed number since 8 species minus the target one

    #prob_distribution_conditions = np.array([(1-bias) / non_species_exp_conditions_count if (x == species_exp or x > 0x9) else (bias) / other_species_total for x in digivolution_conditions_pool])


    condition_amount_distribution = constants.DIGIVOLUTION_CONDITION_AMOUNT_DISTRIBUTION[stage]
    condition_amount = np.random.choice(list(range(1,len(condition_amount_distribution)+1)), p=condition_amount_distribution)
    conditions = []
    for c in range(1, condition_amount+1):

        # has to be done inside the for to account for the removed condition if third condition is generated

        prob_distribution_conditions = []
        for x in digivolution_conditions_pool:
            if(x == species_exp):       # prob for own species exp
                prob_distribution_conditions.append((1-bias)/2)         
            elif(x > 0x9):              # prob for non-species-exp conditions
                prob_distribution_conditions.append(((1-bias)/2)/(len(digivolution_conditions_pool) - len(species_condition_mapping)))
            else:                       # prob for other species exp conditions
                prob_distribution_conditions.append(bias/other_species_total)

        prob_distribution_conditions = np.array(prob_distribution_conditions)
        prob_distribution_conditions /= prob_distribution_conditions.sum()

        if(c == 1):     # force level
            cur_condition = 0x1
        else:           # choose one of the other conditions randomly
            cur_condition = int(np.random.choice(digivolution_conditions_pool, p=prob_distribution_conditions))
            digivolution_conditions_pool.remove(cur_condition)

        min_val = constants.DIGIVOLUTION_CONDITIONS_VALUES[cur_condition][stage_id][0]
        max_val = constants.DIGIVOLUTION_CONDITIONS_VALUES[cur_condition][stage_id][1]
        conditions.append([cur_condition, random.randint(min_val, max_val)])
    return conditions


def generateSpeciesProbDistribution(stage_digimon_pool: dict, 
                                    base_digimon_info: dict, 
                                    species_bias: float, 
                                    species_id: int) -> List[float]:
    id_list = list(stage_digimon_pool.values())
    species_list = [base_digimon_info[x].species for x in id_list]
    species_counter = Counter(species_list)
    species_total = len(species_list)
    sp_prob_dist = [species_bias/species_counter[species_id] if x == species_id else (1 - species_bias)/(species_total - species_counter[species_id]) for x in species_list]
    return sp_prob_dist




def writeRomBytes(rom_data: bytearray, new_value: int, offset: int, byte_size: int):
    rom_data[offset:offset+byte_size] = (new_value).to_bytes(byte_size, byteorder="little")