import os
import binascii
import logging
import constants
import random
from enum import Enum
import utils
import model


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
ROOKIE_RESET_EVENT = RookieResetConfig.UNCHANGED
RANDOMIZE_STARTERS = RandomizeStartersConfig.RAND_SAME_STAGE
NERF_FIRST_BOSS = True                                  # city attack boss's max hp will be reduced by half (to compensate for no Lunamon at lvl 20)

RANDOMIZE_AREA_ENCOUNTERS = True
AREA_ENCOUNTERS_STATS = model.LvlUpMode.FIXED_AVG      # this defines how the randomized enemy digimon's stats are generated when changing the levels

RANDOMIZE_FIXED_BATTLES = True
FIXED_BATTLES_DIGIMON_SAME_STAGE = True                 # digimon will be swapped with another digimon of the same stage
FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES = False             # do not change boss-exclusive digimon like ???, SkullBaluchimon, Grimmon, etc
FIXED_BATTLES_BALANCE_BY_BST = False                    # if true, generated encounter will have roughly the same stat total as the original encounter (which can lead to a different digimon lvl); if false, the generated encounter will be set at the same level regardless of how stronger/weaker the new digimon is
FIXED_BATTLES_KEEP_HP = True                            # do not change base HP of the encounter: most fixed battles have enemies with slightly more hp than usual, this will keep the digimon's HP stat the same as before



PATH_SOURCE = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (USA).nds"
PATH_TARGET = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (USA)_patched.nds"

#PATH_SOURCE = "C:/Workspace/digimon_stuffs/1420 - Digimon World - Dusk (US).nds"
#PATH_TARGET = "C:/Workspace/digimon_stuffs/1420 - Digimon World - Dusk (US)_patched.nds"



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

        digimon_pool = constants.DIGIMON_IDS.copy()

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



    




if __name__ == '__main__':
    
    logger.info("Creating new rom from source \"" + PATH_SOURCE + "\"")
    
    rom = DigimonROM(PATH_SOURCE)
    rom.executeQolChanges()
    randomizer = Randomizer(rom.version, rom.rom_data)
    randomizer.randomizeStarters(rom.rom_data)
    randomizer.randomizeAreaEncounters(rom.rom_data)
    randomizer.nerfFirstBoss(rom.rom_data)

    rom.writeRom(PATH_TARGET)