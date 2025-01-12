import os
import binascii
import logging
import random
from enum import Enum
from src import constants, utils, model
import numpy as np
import copy

# strife was here
class RookieResetConfig(Enum):
    UNCHANGED = 0                       # same as base game; resets digimon to rookies after the chaos event 
    RESET_ALL_INCLUDING_LUNAMON = 1     # same as base game but also resets Lunamon to lvl 1
    RESET_KEEPING_EVO = 2               # reset digimon's levels, stats, etc, but keep them at their original form (ex: SkullGreymon stays as SkullGreymon but lvl 1) 
    DO_NOT_RESET = 3                    # rookie reset event does not happen; keeps digimon as they were before the chaos event


class RandomizeStartersConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RAND_SAME_STAGE = 1                 # randomize while keeping the same stage of the digimon
    RAND_FULL = 2                       # fully randomize




CHANGE_TEXT_SPEED = True
CHANGE_MOVEMENT_SPEED = True
MOVEMENT_SPEED_MULTIPLIER = 1.5
CHANGE_ENCOUNTER_RATE = True
ENCOUNTER_RATE_MULTIPLIER = 0.5
CHANGE_STAT_CAPS = True
EXTEND_PLAYERNAME_SIZE = True

ROOKIE_RESET_EVENT = RookieResetConfig.UNCHANGED
RANDOMIZE_STARTERS = RandomizeStartersConfig.RAND_SAME_STAGE
NERF_FIRST_BOSS = True                                  # city attack boss's max hp will be reduced by half (to compensate for no Lunamon at lvl 20)

RANDOMIZE_AREA_ENCOUNTERS = False
AREA_ENCOUNTERS_STATS = model.LvlUpMode.FIXED_AVG      # this defines how the randomized enemy digimon's stats are generated when changing the levels

RANDOMIZE_FIXED_BATTLES = False
FIXED_BATTLES_DIGIMON_SAME_STAGE = True                 # digimon will be swapped with another digimon of the same stage
FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES = False             # do not change boss-exclusive digimon like ???, SkullBaluchimon, Grimmon, etc
FIXED_BATTLES_BALANCE_BY_BST = False                    # if true, generated encounter will have roughly the same stat total as the original encounter (which can lead to a different digimon lvl); if false, the generated encounter will be set at the same level regardless of how stronger/weaker the new digimon is
FIXED_BATTLES_KEEP_HP = True                            # do not change base HP of the encounter: most fixed battles have enemies with slightly more hp than usual, this will keep the digimon's HP stat the same as before


RANDOMIZE_DIGIVOLUTIONS = True
DIGIVOLUTIONS_SIMILAR_SPECIES = True        # example: holy digimon will be more likely to evolve into other holy digimon
DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS = 0.8    # the total odds for the same species digimon will be the bias value (in this case it's 0.8), total odds for digimon from other species will be the remaining value (1 - bias)
DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP = True       # example: a digivolution from the holy species will be less likely to have aquan/dark/etc exp as a requirement than other conditions
DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS = 0.2          # how less likely each exp condition is to be picked (in this case, the probability for each of those exp conditions is multiplied by the bias value; multiplying by 0.2 makes the condition 5 times less likely)


PATH_SOURCE = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (U)(XenoPhobia).nds"
PATH_TARGET = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (U)_deltapatched.nds"

#PATH_SOURCE = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA).nds"
#PATH_TARGET = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA)_deltapatched_randomized_1.nds"



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DigimonROM:
    def __init__(self, 
                 fpath: str):
        self.fpath = fpath
        self.rom_data = self.loadRom(fpath)
        self.version = self.checkHeader(self.rom_data[12:16].hex())
    

    def executeQolChanges(self):
        if(CHANGE_TEXT_SPEED):
            self.changeTextSpeed()
        if(CHANGE_MOVEMENT_SPEED):
            self.changeMovementSpeed()
        if(CHANGE_ENCOUNTER_RATE):
            self.changeEncounterRate()
        if(CHANGE_STAT_CAPS):
            self.changeStatCaps()
        if(EXTEND_PLAYERNAME_SIZE):
            self.extendPlayerNameSize()
        


    def loadRom(self, 
                fpath: str):
        with open(fpath, "rb") as f:
            return bytearray(f.read())
        
    def writeRom(self, 
                 fpath: str):
        with open(fpath, "wb") as f:
            f.write(self.rom_data)

    def checkHeader(self, header_value):
        if(header_value == "41365245"):
            return "DUSK"
        if(header_value == "41335645"):
            return "DAWN"
        raise ValueError("Game not recognized. Please check your rom (file \"" +  os.path.basename(self.fpath) + "\").")

    
    def changeTextSpeed(self):
        offset = constants.TEXT_SPEED_OFFSET[self.version]
        self.rom_data[offset:offset+4] = binascii.unhexlify("030010e3")
        logger.info("Changed text speed")


    def changeMovementSpeed(self):
        offset = constants.MOVEMENT_SPEED_OFFSET[self.version]
        movement_speed = max(2, int(2 * MOVEMENT_SPEED_MULTIPLIER))
        hex_str = "{0:0{1}x}".format(movement_speed,2) + "10a0e3"
        self.rom_data[offset:offset+4] = binascii.unhexlify(hex_str)
        logger.info("Changed movement speed (" + str(MOVEMENT_SPEED_MULTIPLIER) + "x)")


    def changeEncounterRate(self):
        offset_start = constants.AREA_ENCOUNTER_OFFSETS[self.version][0]
        offset_end = constants.AREA_ENCOUNTER_OFFSETS[self.version][1]

        cur_offset = offset_start
        while(cur_offset <= offset_end):    # <=  to include offset_end
            lower_bound = int(int.from_bytes(self.rom_data[cur_offset+2:cur_offset+4], byteorder="little") * ENCOUNTER_RATE_MULTIPLIER)
            upper_bound = int(int.from_bytes(self.rom_data[cur_offset+4:cur_offset+6], byteorder="little") * ENCOUNTER_RATE_MULTIPLIER)
            self.rom_data[cur_offset+2:cur_offset+4] = (lower_bound).to_bytes(2, byteorder="little")
            self.rom_data[cur_offset+4:cur_offset+6] = (upper_bound).to_bytes(2, byteorder="little")
            cur_offset += 0x200

        logger.info("Changed encounter rate (" + str(ENCOUNTER_RATE_MULTIPLIER) + "x)")


    def changeStatCaps(self):
        offset = constants.STAT_CAPS_OFFSET[self.version]
        self.rom_data[offset:offset+2] = (0xffff).to_bytes(2, byteorder="little")
        self.rom_data[offset+4:offset+6] = (0xffff).to_bytes(2, byteorder="little")
        logger.info("Changed stat caps (max value for each stat is now 65535)")


    def extendPlayerNameSize(self):
        offset_dict = constants.PLAYERNAME_EXTENSION_ADDRESSES[self.version]
        for offset in offset_dict.keys():
            address_value = offset_dict[offset]
            utils.writeRomBytes(self.rom_data, address_value, offset, 4)
        logger.info("Extended player name size (max player name size is now 7)")


class Randomizer:
    version: str
    baseDigimonInfo: dict[int, model.BaseDataDigimon]
    enemyDigimonInfo: dict[int, model.EnemyDataDigimon]

    def __init__(self, 
                 version: str, 
                 rom_data: bytearray):
        self.version = version
        self.baseDigimonInfo = utils.loadBaseDigimonInfo(version, rom_data)
        self.enemyDigimonInfo = utils.loadEnemyDigimonInfo(version, rom_data)
        self.lvlupTypeTable = utils.loadLvlupTypeTable(version, rom_data)
        self.spriteMapTable = utils.loadSpriteMapTable(version, rom_data)
        self.battleStrTable = utils.loadBattleStringTable(version, rom_data)

    
    def randomizeStarters(self, 
                          rom_data: bytearray):
        # NOTE: If generated digimon's aptitude is lower than target lvl, target lvl becomes digimon's aptitude

        if(RANDOMIZE_STARTERS == RandomizeStartersConfig.UNCHANGED):
            return
        
        cur_offset = constants.STARTER_PACK_OFFSET[self.version]
        for spack_i in range(4):            # there are 4 starter packs
            new_starter_pack = []
            for starter_i in range(3):       # 3 starters
                cur_starter_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                cur_starter_level = int.from_bytes(rom_data[cur_offset+2:cur_offset+4], byteorder="little")
                cur_x_coord = int.from_bytes(rom_data[cur_offset+4:cur_offset+6], byteorder="little")
                cur_y_coord = int.from_bytes(rom_data[cur_offset+6:cur_offset+8], byteorder="little")
                randomized_digimon_id = -1

                if(RANDOMIZE_STARTERS == RandomizeStartersConfig.RAND_SAME_STAGE):
                    starter_stage = utils.getDigimonStage(cur_starter_id)
                    if(starter_stage == ""):
                        logger.info("Original starter digimon not recognized, randomizing between rookie and ultimate")
                        starter_stage = random.choice(["ROOKIE","CHAMPION","ULTIMATE"])

                    randomized_digimon = random.choice(list(constants.DIGIMON_IDS[starter_stage].items()))
                    randomized_digimon_id = randomized_digimon[1]
                    new_starter_pack.append(randomized_digimon[0])


                elif(RANDOMIZE_STARTERS == RandomizeStartersConfig.RAND_FULL):
                    possibleDigimonIds = utils.getAllDigimonPairs()
                    randomized_digimon = random.choice(possibleDigimonIds)
                    randomized_digimon_id = randomized_digimon[1]
                    new_starter_pack.append(randomized_digimon[0])

                    
                rom_data[cur_offset:cur_offset+2] = (randomized_digimon_id).to_bytes(2, byteorder="little")    # write new digimon id

                target_digimon_lvl = self.baseDigimonInfo[randomized_digimon_id].aptitude
                if(target_digimon_lvl < cur_starter_level):                                                     # check if digimon's aptitude is lower than starter lvl
                    rom_data[cur_offset+2:cur_offset+4] = (target_digimon_lvl).to_bytes(2, byteorder="little")    # set lvl to max aptitude

                rom_data[cur_offset+4:cur_offset+6] = (0x30 + 0x50*starter_i).to_bytes(2, byteorder="little")  # write x coordinate
                rom_data[cur_offset+6:cur_offset+8] = (0x90).to_bytes(2, byteorder="little")                   # write y coordinate
                
                cur_offset += 8
            
            logger.info("Starter pack " + str(spack_i + 1) + ": " + str(new_starter_pack))

        # we actually don't need to do anything w the outer cycle i think, each starter advances the offset by 8 already

    
    def randomizeAreaEncounters(self, 
                                rom_data: bytearray):
        
        if(not RANDOMIZE_AREA_ENCOUNTERS):
            return
        
        offset_start = constants.AREA_ENCOUNTER_OFFSETS[self.version][0]
        offset_end = constants.AREA_ENCOUNTER_OFFSETS[self.version][1]

        digimon_pool = copy.deepcopy(constants.DIGIMON_IDS)

        randomized_digimon_history = {}

        area_offset = offset_start
        while(area_offset <= offset_end):    # <=  to include offset_end
            cur_offset = area_offset + 16   # skip area header
            new_area_digimon = []
            
            cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
            while(cur_digimon_id != 0 and cur_offset <= area_offset + 0x200):
                digimon_stage = utils.getDigimonStage(cur_digimon_id)
                if(digimon_stage == ""):
                    logger.info("Digimon with id " + str(cur_digimon_id) + " not recognized, skipping encounter")
                    cur_offset += 24        # skip 24 bytes to get next encounter
                    cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                    continue
                if(cur_digimon_id in randomized_digimon_history.keys()):
                    new_area_digimon.append(randomized_digimon_history[cur_digimon_id][0])
                    rom_data[cur_offset:cur_offset+2] = (randomized_digimon_history[cur_digimon_id][1]).to_bytes(2, byteorder="little")
                    cur_offset += 24        # skip 24 bytes to get next encounter
                    cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                    continue

                picked_digimon_name = random.choice(list(digimon_pool[digimon_stage].keys()))
                randomized_digimon_id = digimon_pool[digimon_stage].pop(picked_digimon_name)     # this ensures there are no repeated digimon

                randomized_digimon_history[cur_digimon_id] = (picked_digimon_name, randomized_digimon_id)
                
                new_area_digimon.append(picked_digimon_name)
                rom_data[cur_offset:cur_offset+2] = (randomized_digimon_id).to_bytes(2, byteorder="little")    # write new digimon id


                # change enemy stats to match the previous digimon's level
                prev_digimon_data = self.enemyDigimonInfo[cur_digimon_id]
                encounter_level = prev_digimon_data.level

                base_digimon_leveled = utils.generateLvlupStats(self.lvlupTypeTable, self.baseDigimonInfo[randomized_digimon_id], encounter_level, AREA_ENCOUNTERS_STATS)
                enemy_digimon_offset = self.enemyDigimonInfo[randomized_digimon_id].offset


                # the following does NOT change self.enemyDigimonInfo; this is on purpose
                # we do not write generated MP since enemy MP is always FF FF
                utils.writeRomBytes(rom_data, base_digimon_leveled.level, enemy_digimon_offset+2, 1)    # write new level to rom
                utils.writeRomBytes(rom_data, base_digimon_leveled.hp, enemy_digimon_offset+4, 2)    # write new hp
                utils.writeRomBytes(rom_data, base_digimon_leveled.attack, enemy_digimon_offset+0xa, 2)    # write new attack
                utils.writeRomBytes(rom_data, base_digimon_leveled.defense, enemy_digimon_offset+0xc, 2)    # write new defense
                utils.writeRomBytes(rom_data, base_digimon_leveled.spirit, enemy_digimon_offset+0xe, 2)    # write new spirit
                utils.writeRomBytes(rom_data, base_digimon_leveled.speed, enemy_digimon_offset+0x10, 2)    # write new speed


                cur_offset += 24        # skip 24 bytes to get next encounter
                cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")

            logger.info(new_area_digimon)
            area_offset += 0x200


    def randomizeFixedBattles(self,
                              rom_data: bytearray):
        
        if(not RANDOMIZE_FIXED_BATTLES):
            return
        

        # to accomplish this we randomize every enemy encounter after 0x01f4

        
    def nerfFirstBoss(self,
                      rom_data: bytearray):
        if(not NERF_FIRST_BOSS):
            return
        # id for first city boss is 0x205

        first_boss_data = self.enemyDigimonInfo[0x205]
        nerfed_hp = first_boss_data.hp // 2

        utils.writeRomBytes(rom_data, nerfed_hp, first_boss_data.offset+4, 2)    # write new hp


    def randomizeDigivolutions(self,
                               rom_data: bytearray):
        if(not RANDOMIZE_DIGIVOLUTIONS):
            return
        
        digimon_to_randomize = copy.deepcopy(constants.DIGIMON_IDS)     # this will be used to iterate through all digimon
        digimon_pool_selection = copy.deepcopy(constants.DIGIMON_IDS)   # this will be used to define if a given digimon is available or not
        generated_conditions = {}
        pre_evos = {}

        for s in range(len(constants.STAGE_NAMES)):
            stage = constants.STAGE_NAMES[s]
            logger_dict = {v: k for k, v in digimon_to_randomize[stage].items()}
            stage_ids = list(digimon_to_randomize[stage].values())
            evo_amount_distribution = constants.DIGIVOLUTION_AMOUNT_DISTRIBUTION[stage]

            random.shuffle(stage_ids)
            for digimon_id in stage_ids:

                log_digimon_name = logger_dict[digimon_id]
                hex_addr = constants.DIGIVOLUTION_ADDRESSES[self.version][digimon_id]
                evos_amount = np.random.choice(list(range(len(evo_amount_distribution))), p=evo_amount_distribution)
                log_evo_names = []
                evo_ids = []
                for e in range(evos_amount):
                    try:
                        # pick evo digimon id
                        evo_digi_name = random.choice(list(digimon_pool_selection[constants.STAGE_NAMES[s+1]].keys()))
                        if(DIGIVOLUTIONS_SIMILAR_SPECIES):
                            evo_species_prob_dist = np.array(utils.generateSpeciesProbDistribution(digimon_pool_selection[constants.STAGE_NAMES[s+1]], self.baseDigimonInfo, DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS, self.baseDigimonInfo[digimon_id].species))
                            evo_species_prob_dist /= evo_species_prob_dist.sum()
                            evo_digi_name = np.random.choice(list(digimon_pool_selection[constants.STAGE_NAMES[s+1]].keys()), p=evo_species_prob_dist)
                        evo_digi_id = digimon_pool_selection[constants.STAGE_NAMES[s+1]].pop(evo_digi_name)              # this ensures there are no repeated digimon
                        log_evo_names.append(evo_digi_name)

                        # generate conditions for evo digimon
                        if(DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP):
                            conditions_evo = utils.generateBiasedConditions(s+1, DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS, self.baseDigimonInfo[evo_digi_id].species)
                        else:
                            conditions_evo = utils.generateConditions(s+1)    # [[condition id (hex), value (int)], ...]
                        generated_conditions[evo_digi_id] = conditions_evo


                        # add pre-evo register to propagate conditions on next cycles
                        pre_evos[evo_digi_id] = digimon_id

                        # add evo_id to current digimon's evo ids
                        evo_ids.append(evo_digi_id)

                    except IndexError:
                        logger.error("No more digimon in the pool, skip current evos")
                        continue


                # if conditions do not exist for current digimon, generate them
                if(digimon_id not in generated_conditions.keys()):
                    if(DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP):
                        conditions_cur = utils.generateBiasedConditions(s, DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS, self.baseDigimonInfo[digimon_id].species)
                    else:
                        conditions_cur = utils.generateConditions(s)
                    generated_conditions[digimon_id] = conditions_cur


                # write to rom

                # pre-evo section

                if(digimon_id in pre_evos.keys()):
                    utils.writeRomBytes(rom_data, pre_evos[digimon_id], hex_addr, 4)
                    conditions_cur = generated_conditions[pre_evos[digimon_id]]
                    for i in range(3):  # write conditions
                        if(len(conditions_cur) > i):
                            utils.writeRomBytes(rom_data, conditions_cur[i][0], hex_addr+0x10 + (0x8*i), 4)
                            utils.writeRomBytes(rom_data, conditions_cur[i][1], hex_addr+0x14 + (0x8*i), 4)
                        else:
                            utils.writeRomBytes(rom_data, 0x0, hex_addr+0x10 + (0x8*i), 4)
                            utils.writeRomBytes(rom_data, 0x0, hex_addr+0x14 + (0x8*i), 4)
                else:
                    utils.writeRomBytes(rom_data, 0xffffffff, hex_addr, 4)
                    for i in range(3):  # write conditions
                        utils.writeRomBytes(rom_data, 0x0, hex_addr+0x10 + (0x8*i), 4)
                        utils.writeRomBytes(rom_data, 0x0, hex_addr+0x14 + (0x8*i), 4)


                # write evos

                for i in range(3):
                    if(len(evo_ids) > i):
                        cur_evo_id = evo_ids[i]
                        utils.writeRomBytes(rom_data, cur_evo_id, hex_addr+(0x4*(i+1)), 4)
                        conditions_cur = generated_conditions[cur_evo_id]
                        for j in range(3):  # write conditions
                            if(len(conditions_cur) > j):
                                utils.writeRomBytes(rom_data, conditions_cur[j][0], hex_addr+0x10 + (0x8*j) + (0x18*(i+1)), 4)
                                utils.writeRomBytes(rom_data, conditions_cur[j][1], hex_addr+0x14 + (0x8*j) + (0x18*(i+1)), 4)
                            else:
                                utils.writeRomBytes(rom_data, 0x0, hex_addr+0x10 + (0x8*j) + (0x18*(i+1)), 4)
                                utils.writeRomBytes(rom_data, 0x0, hex_addr+0x14 + (0x8*j) + (0x18*(i+1)), 4)
                    else:
                        utils.writeRomBytes(rom_data, 0xffffffff, hex_addr+(0x4*(i+1)), 4)
                        for j in range(3):  # write conditions
                            utils.writeRomBytes(rom_data, 0x0, hex_addr+0x10 + (0x8*j) + (0x18*(i+1)), 4)
                            utils.writeRomBytes(rom_data, 0x0, hex_addr+0x14 + (0x8*j) + (0x18*(i+1)), 4)

                logger.info(log_digimon_name + " -> " + str(log_evo_names))


    




if __name__ == '__main__':
    
    logger.info("Creating new rom from source \"" + PATH_SOURCE + "\"")
    
    rom = DigimonROM(PATH_SOURCE)
    rom.executeQolChanges()
    randomizer = Randomizer(rom.version, rom.rom_data)
    randomizer.randomizeStarters(rom.rom_data)
    randomizer.randomizeAreaEncounters(rom.rom_data)
    randomizer.nerfFirstBoss(rom.rom_data)
    randomizer.randomizeDigivolutions(rom.rom_data)

    rom.writeRom(PATH_TARGET)