import os
import binascii
import logging
import random
import time
from typing import Dict, List
from src import constants, utils, model
import numpy as np
import copy
from configs import PATH_SOURCE, PATH_TARGET, ConfigManager, ExpYieldConfig, RandomizeBaseStats, RandomizeDigimonStatType, RandomizeDigivolutionConditions, RandomizeDigivolutions, RandomizeDnaDigivolutionConditions, RandomizeDnaDigivolutions, RandomizeElementalResistances, RandomizeMovesets, RandomizeOverworldItems, RandomizeSpeciesConfig, RandomizeStartersConfig, RandomizeTraits, RandomizeWildEncounters, RookieResetConfig, default_configmanager_settings
from io import StringIO
from tabulate import tabulate


#random.seed(1)
#np.random.seed(1)

#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)


class DigimonROM:
    def __init__(self, 
                 fpath: str,
                 config_manager: ConfigManager,
                 logger: logging.Logger):
        self.fpath = fpath
        self.rom_data = self.loadRom(fpath)
        self.version = self.checkHeader(self.rom_data[12:16].hex())
        self.config_manager = config_manager
        self.logger = logger
    

    def executeQolChanges(self):
        if(self.config_manager.get("CHANGE_TEXT_SPEED", False)):
            self.changeTextSpeed()
        if(self.config_manager.get("CHANGE_MOVEMENT_SPEED", False)):
            self.changeMovementSpeed()
        if(self.config_manager.get("CHANGE_ENCOUNTER_RATE", False)):
            self.changeEncounterRate()
        if(self.config_manager.get("CHANGE_STAT_CAPS", False)):
            self.changeStatCaps()
        if(self.config_manager.get("EXTEND_PLAYERNAME_SIZE", False)):
            self.extendPlayerNameSize()
        if(self.config_manager.get("BUFF_SCAN_RATE", False)):
            self.buffScanRate()
        if(self.config_manager.get("CHANGE_FARM_EXP", False)):
            self.changeFarmExp()
        if(self.config_manager.get("ENABLE_VERSION_EXCLUSIVE_AREAS", False)):
            self.unlockExclusiveAreas()
        

    def loadRom(self, 
                fpath: str):
        with open(fpath, "rb") as f:
            return bytearray(f.read())
        
    def writeRom(self, 
                 fpath: str):
        with open(fpath, "wb") as f:
            f.write(self.rom_data)
        self.logger.info("Created new rom at target path \"" + fpath + "\"")

    def checkHeader(self, header_value):
        if(header_value == "41365245"):
            return "DUSK"
        if(header_value == "41335645"):
            return "DAWN"
        raise ValueError("Game not recognized. Please check your rom (file \"" +  os.path.basename(self.fpath) + "\").")
    

    def changeTextSpeed(self):
        offset = constants.TEXT_SPEED_OFFSET[self.version]
        self.rom_data[offset:offset+4] = binascii.unhexlify("030010e3")
        self.logger.info("Increased text speed (1.5x)")


    def changeMovementSpeed(self):
        offset = constants.MOVEMENT_SPEED_OFFSET[self.version]
        movement_speed = max(2, int(2 * self.config_manager.get("MOVEMENT_SPEED_MULTIPLIER")))
        hex_str = "{0:0{1}x}".format(movement_speed,2) + "10a0e3"
        self.rom_data[offset:offset+4] = binascii.unhexlify(hex_str)
        self.logger.info("Increased movement speed (" + str(self.config_manager.get("MOVEMENT_SPEED_MULTIPLIER")) + "x)")


    def changeEncounterRate(self):
        offset_start = constants.AREA_ENCOUNTER_OFFSETS[self.version][0]
        offset_end = constants.AREA_ENCOUNTER_OFFSETS[self.version][1]

        cur_offset = offset_start
        while(cur_offset <= offset_end):    # <=  to include offset_end
            lower_bound = int(int.from_bytes(self.rom_data[cur_offset+2:cur_offset+4], byteorder="little") * self.config_manager.get("ENCOUNTER_RATE_MULTIPLIER"))
            upper_bound = int(int.from_bytes(self.rom_data[cur_offset+4:cur_offset+6], byteorder="little") * self.config_manager.get("ENCOUNTER_RATE_MULTIPLIER"))
            self.rom_data[cur_offset+2:cur_offset+4] = (lower_bound).to_bytes(2, byteorder="little")
            self.rom_data[cur_offset+4:cur_offset+6] = (upper_bound).to_bytes(2, byteorder="little")
            cur_offset += 0x200

        self.logger.info("Reduced encounter rate (" + str(self.config_manager.get("ENCOUNTER_RATE_MULTIPLIER")) + "x)")


    def changeStatCaps(self):

        return  # disabling this for now, not working properly
        #offset = constants.STAT_CAPS_OFFSET[self.version]
        #self.rom_data[offset:offset+2] = (0xffff).to_bytes(2, byteorder="little")
        #self.rom_data[offset+4:offset+6] = (0xffff).to_bytes(2, byteorder="little")
        #self.logger.info("Increased stat caps (max value for each stat is now 65535)")


    def extendPlayerNameSize(self):
        offset_dict = constants.PLAYERNAME_EXTENSION_ADDRESSES[self.version]
        for offset in offset_dict.keys():
            address_value = offset_dict[offset]
            utils.writeRomBytes(self.rom_data, address_value, offset, 4)
        self.logger.info("Expanded player name size (max player name size is now 7)")


    def buffScanRate(self):
        offset = constants.BASE_SCAN_RATE_OFFSET[self.version]
        old_scan_rate = self.rom_data[offset]
        self.rom_data[offset] = self.config_manager.get("NEW_BASE_SCAN_RATE")
        self.logger.info(f"Increased base scan rate from {old_scan_rate} to {self.config_manager.get('NEW_BASE_SCAN_RATE')}")

    
    def changeFarmExp(self):
        cur_offset = constants.FARM_TERRAINS_START_OFFSET[self.version]
        exp_modifier = self.config_manager.get("FARM_EXP_MODIFIER", 1)
        for t in range(17):         # 17 terrains
            # load terrain memory here? could load earlier if needed for other things
            cur_terrain = model.FarmTerrain(self.rom_data[cur_offset : cur_offset+0x5c], cur_offset)
            utils.applyFarmExpModifier(self.rom_data, cur_terrain, exp_modifier)
            self.logger.info(f"Farm {t} EXP: {cur_terrain.holy_exp * exp_modifier} HOLY, {cur_terrain.dark_exp * exp_modifier} DARK, {cur_terrain.dragon_exp * exp_modifier} DRAGON, {cur_terrain.beast_exp * exp_modifier} BEAST, {cur_terrain.bird_exp * exp_modifier} BIRD, {cur_terrain.machine_exp * exp_modifier} MACHINE, {cur_terrain.aquan_exp * exp_modifier} AQUAN, {cur_terrain.insectplant_exp * exp_modifier} INSECTPLANT")
            cur_offset += 0x5c      # advance to next terrain
            

    def unlockExclusiveAreas(self):
        areas_to_unlock = constants.VERSION_EXCLUSIVE_AREA_UNLOCKS[self.version]
        # format is always (offset, new value, description)
        # byte_size is always 2
        for area_el in areas_to_unlock:
            cur_address = area_el[0]
            cur_value = area_el[1]
            cur_description = area_el[2]
            utils.writeRomBytes(self.rom_data, cur_value, cur_address, 2)
            self.logger.info("VERSION-EXCLUSIVE AREA UNLOCK: " + cur_description)

            

        


class Randomizer:
    version: str
    baseDigimonInfo: Dict[int, model.BaseDataDigimon]
    enemyDigimonInfo: Dict[int, model.EnemyDataDigimon]
    armorDigivolutions: List[model.ArmorDigivolution]
    dnaDigivolutions: List[model.DNADigivolution]

    def __init__(self, 
                 version: str, 
                 rom_data: bytearray,
                 config_manager: ConfigManager,
                 logger: logging.Logger):
        self.version = version
        self.config_manager = config_manager
        self.logger = logger
        self.rom_data = rom_data
        self.baseDigimonInfo = utils.loadBaseDigimonInfo(version, rom_data)
        self.enemyDigimonInfo = utils.loadEnemyDigimonInfo(version, rom_data)
        self.standardDigivolutions = utils.loadStandardDigivolutions(version, rom_data)
        self.armorDigivolutions = utils.loadArmorDigivolutions(version, rom_data)
        self.dnaDigivolutions, self.dnaConditionsByDigimonId = utils.loadDnaDigivolutions(version, rom_data)
        self.moveDataArray: List[model.MoveData] = utils.loadMoveData(version, rom_data)
        self.lvlupTypeTable = utils.loadLvlupTypeTable(version, rom_data)
        self.spriteMapTable = utils.loadSpriteMapTable(version, rom_data)
        self.battleStrTable = utils.loadBattleStringTable(version, rom_data)

    
    def executeRandomizerFunctions(self, target_rom_data: bytearray = None):

        if(target_rom_data is None):
            target_rom_data = self.rom_data

        self.rookieResetEvent(target_rom_data)
        self.randomizeAreaEncounters(target_rom_data)      # returned enemyDigimonInfo is taken into account for the exp patch
        self.nerfFirstBoss(target_rom_data)
        self.randomizeOverworldItems(target_rom_data)

        # the following function modifies self.baseDigimonInfo; this is needed to propagate base data changes into the randomization
        self.randomizeDigimonSpecies(target_rom_data)

        # this function must be called AFTER randomizeDigimonSpecies()
        self.randomizeElementalResistances(target_rom_data)

        self.randomizeDigimonMovesets(target_rom_data)

        self.randomizeDigimonTraits(target_rom_data)

        if(self.config_manager.get("RANDOMIZE_DIGIVOLUTIONS") not in [None, RandomizeDigivolutions.UNCHANGED]):
            # in the future this should modify self.standardDigivolutions instead of having two extra objects to manage
            self.curUpdatedPreEvos, self.curStandardEvos = self.randomizeDigivolutions(target_rom_data)
        elif(self.config_manager.get("RANDOMIZE_DIGIVOLUTION_CONDITIONS") not in [None, RandomizeDigivolutionConditions.UNCHANGED]):
            self.randomizeDigivolutionConditionsOnly(target_rom_data)   # this only triggers if randomize digivolutions is not applied

        self.manageDnaDigivolutions(target_rom_data)

        # starter randomization must happen after digivolution randomization
        self.randomizeStarters(target_rom_data)

        '''
        if(self.config_manager.get("RANDOMIZE_DNADIGIVOLUTIONS") not in [None, RandomizeDnaDigivolutions.UNCHANGED]):
            self.randomizeDnaDigivolutions(target_rom_data)
        elif(self.config_manager.get("RANDOMIZE_DNADIGIVOLUTION_CONDITIONS") in [RandomizeDnaDigivolutionConditions.RANDOMIZE]):
            self.randomizeDnaDigivolutionConditionsOnly(target_rom_data)  # similar to above, only triggers if randomize dna evos not applied
        '''

        self.expPatchFlat(target_rom_data)

    
    def randomizeStarters(self, 
                          rom_data: bytearray):
        # NOTE: If generated digimon's aptitude is lower than target lvl, target lvl becomes digimon's aptitude

        if(self.config_manager.get("RANDOMIZE_STARTERS") == RandomizeStartersConfig.UNCHANGED):
            return

        if(self.config_manager.get("FORCE_STARTER_W_ROOKIE")):
            digimon_ids_w_rookie = {
                *constants.DIGIMON_IDS["IN-TRAINING"].values(),
                *constants.DIGIMON_IDS["ROOKIE"].values()
            }
            for stage in ["CHAMPION", "ULTIMATE", "MEGA"]:
                for cur_digimon_id in constants.DIGIMON_IDS[stage].values():
                    cur_pre_evo = self.curUpdatedPreEvos.get(cur_digimon_id, None)
                    if(cur_pre_evo != None and cur_pre_evo in digimon_ids_w_rookie):
                        digimon_ids_w_rookie.add(cur_digimon_id)

        
        self.logger.info("\n==================== STARTER PACKS ====================")
        cur_offset = constants.STARTER_PACK_OFFSET[self.version]
        for spack_i in range(4):            # there are 4 starter packs
            new_starter_pack = []
            for starter_i in range(3):       # 3 starters
                cur_starter_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                cur_starter_level = int.from_bytes(rom_data[cur_offset+2:cur_offset+4], byteorder="little")
                cur_x_coord = int.from_bytes(rom_data[cur_offset+4:cur_offset+6], byteorder="little")
                cur_y_coord = int.from_bytes(rom_data[cur_offset+6:cur_offset+8], byteorder="little")
                randomized_digimon_id = -1

                if(self.config_manager.get("RANDOMIZE_STARTERS") == RandomizeStartersConfig.RAND_SAME_STAGE):
                    starter_stage = utils.getDigimonStage(cur_starter_id)
                    if(starter_stage == ""):
                        self.logger.debug("Original starter digimon not recognized, randomizing between rookie and ultimate")
                        starter_stage = random.choice(["ROOKIE","CHAMPION","ULTIMATE"])
                    cur_digimon_pool = constants.DIGIMON_IDS[starter_stage].items()
                
                elif(self.config_manager.get("RANDOMIZE_STARTERS") == RandomizeStartersConfig.RAND_FULL):
                    cur_digimon_pool = utils.getAllDigimonPairs()

                else:       # default escape case
                    self.logger.error("No RANDOMIZE_STARTERS compatible option, escaping to full randomization")
                    cur_digimon_pool = utils.getAllDigimonPairs()

                if self.config_manager.get("FORCE_STARTER_W_ROOKIE"):
                    cur_digimon_pool = [(name, id_) for name, id_ in cur_digimon_pool if id_ in digimon_ids_w_rookie]

                randomized_digimon = random.choice(list(cur_digimon_pool))
                new_starter_pack.append(randomized_digimon[0])
                randomized_digimon_id = randomized_digimon[1]

                rom_data[cur_offset:cur_offset+2] = (randomized_digimon_id).to_bytes(2, byteorder="little")    # write new digimon id

                target_digimon_lvl = self.baseDigimonInfo[randomized_digimon_id].aptitude
                if(target_digimon_lvl < cur_starter_level):                                                     # check if digimon's aptitude is lower than starter lvl
                    rom_data[cur_offset+2:cur_offset+4] = (target_digimon_lvl).to_bytes(2, byteorder="little")    # set lvl to max aptitude

                rom_data[cur_offset+4:cur_offset+6] = (0x30 + 0x50*starter_i).to_bytes(2, byteorder="little")  # write x coordinate
                rom_data[cur_offset+6:cur_offset+8] = (0x90).to_bytes(2, byteorder="little")                   # write y coordinate
                
                cur_offset += 8

            
            self.logger.info("Starter Pack " + str(spack_i + 1) + ": " + ", ".join(new_starter_pack))

        # we actually don't need to do anything w the outer cycle i think, each starter advances the offset by 8 already


    def rookieResetEvent(self,
                         rom_data: bytearray):
        
        rookie_reset_event_var = self.config_manager.get("ROOKIE_RESET_EVENT")
        if(rookie_reset_event_var == RookieResetConfig.UNCHANGED):
            return
        
        if(rookie_reset_event_var == RookieResetConfig.RESET_KEEPING_EVO):
            offsets_array = constants.ROOKIE_RESET_KEEPING_EVO[self.version]
            for offset in offsets_array:
                utils.writeRomBytes(rom_data, 0xb3a08002, offset, 4)
            self.logger.info("Changed rookie reset event to reset stats but keep the original digivolutions")

        if(rookie_reset_event_var == RookieResetConfig.DO_NOT_RESET):
            cancel_offset = constants.ROOKIE_RESET_CANCEL[self.version]
            utils.writeRomBytes(rom_data, 0xe3500040, cancel_offset, 4)
            utils.writeRomBytes(rom_data, 0x1a000017, cancel_offset+4, 4)
            self.logger.info("Disabled the rookie reset event")

    
    def randomizeAreaEncounters(self, 
                                rom_data: bytearray):
        
        previousEnemyDigimonInfo = copy.deepcopy(self.enemyDigimonInfo)

        if(self.config_manager.get("RANDOMIZE_AREA_ENCOUNTERS") == RandomizeWildEncounters.UNCHANGED):
            return
        
        offset_start = constants.AREA_ENCOUNTER_OFFSETS[self.version][0]
        offset_end = constants.AREA_ENCOUNTER_OFFSETS[self.version][1]

        options_same_stage = [RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE]
        options_completely_random = [RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY]

        if(self.config_manager.get("RANDOMIZE_AREA_ENCOUNTERS") in options_same_stage):
            digimon_stage_pool = copy.deepcopy(constants.DIGIMON_IDS)
            if(self.config_manager.get("WILD_DIGIMON_EXCLUDE_CALUMON", False)):
                digimon_stage_pool["IN-TRAINING"].pop("Calumon")
        
        # if completely random, digimon_pool is mixed between all digimon
        if(self.config_manager.get("RANDOMIZE_AREA_ENCOUNTERS") in options_completely_random):
            digimon_ids_by_stage = copy.deepcopy(constants.DIGIMON_IDS)
            digimon_pool = {}
            for stage in digimon_ids_by_stage:
                digimon_pool = digimon_pool | digimon_ids_by_stage[stage]
            if(self.config_manager.get("WILD_DIGIMON_EXCLUDE_CALUMON", False)):
                digimon_pool.pop("Calumon")

        randomized_digimon_history = {}

        self.logger.info("\n==================== WILD DIGIMON ====================")
        area_i = 1                      # this is only used for logging; should be replaced when we have labels for each area
        area_offset = offset_start
        while(area_offset <= offset_end):    # <=  to include offset_end
            cur_offset = area_offset + 16   # skip area header
            new_area_digimon = []
            
            cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
            while(cur_digimon_id != 0 and cur_offset <= area_offset + 0x200):
                digimon_stage = utils.getDigimonStage(cur_digimon_id)
                if(digimon_stage == ""):
                    self.logger.debug("Digimon with id " + str(cur_digimon_id) + " not recognized, skipping encounter")
                    cur_offset += 24        # skip 24 bytes to get next encounter
                    cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                    continue
                if(cur_digimon_id in randomized_digimon_history.keys()):
                    new_area_digimon.append(randomized_digimon_history[cur_digimon_id][0])
                    rom_data[cur_offset:cur_offset+2] = (randomized_digimon_history[cur_digimon_id][1]).to_bytes(2, byteorder="little")
                    cur_offset += 24        # skip 24 bytes to get next encounter
                    cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")
                    continue

                # this randomizes by stage
                if(self.config_manager.get("RANDOMIZE_AREA_ENCOUNTERS") in options_same_stage):
                    picked_digimon_name = random.choice(list(digimon_stage_pool[digimon_stage].keys()))
                    randomized_digimon_id = digimon_stage_pool[digimon_stage].pop(picked_digimon_name)     # this ensures there are no repeated digimon

                # this randomizes completely
                if(self.config_manager.get("RANDOMIZE_AREA_ENCOUNTERS") in options_completely_random):
                    picked_digimon_name = random.choice(list(digimon_pool.keys()))
                    randomized_digimon_id = digimon_pool.pop(picked_digimon_name)     # this ensures there are no repeated digimon


                randomized_digimon_history[cur_digimon_id] = (picked_digimon_name, randomized_digimon_id)
                
                new_area_digimon.append(picked_digimon_name)
                rom_data[cur_offset:cur_offset+2] = (randomized_digimon_id).to_bytes(2, byteorder="little")    # write new digimon id


                # change enemy stats to match the previous digimon's level
                # compare to previousEnemyDigimonInfo in order to maintain coherency w previous data
                prev_digimon_data = previousEnemyDigimonInfo[cur_digimon_id]
                encounter_level = prev_digimon_data.level

                base_digimon_leveled = utils.generateLvlupStats(self.lvlupTypeTable, self.baseDigimonInfo[randomized_digimon_id], encounter_level, self.config_manager.get("AREA_ENCOUNTERS_STATS"))
                enemy_digimon_offset = self.enemyDigimonInfo[randomized_digimon_id].offset

                # update stats
                enemy_digimon_to_update = self.enemyDigimonInfo[randomized_digimon_id]
                enemy_digimon_to_update.level = base_digimon_leveled.level
                enemy_digimon_to_update.hp = base_digimon_leveled.hp
                enemy_digimon_to_update.attack = base_digimon_leveled.attack
                enemy_digimon_to_update.defense = base_digimon_leveled.defense
                enemy_digimon_to_update.spirit = base_digimon_leveled.spirit
                enemy_digimon_to_update.speed = base_digimon_leveled.speed

                
                # we do not write generated MP since enemy MP is always FF FF
                utils.writeRomBytes(rom_data, base_digimon_leveled.level, enemy_digimon_offset+2, 1)    # write new level to rom
                utils.writeRomBytes(rom_data, base_digimon_leveled.hp, enemy_digimon_offset+4, 2)    # write new hp
                utils.writeRomBytes(rom_data, base_digimon_leveled.attack, enemy_digimon_offset+0xa, 2)    # write new attack
                utils.writeRomBytes(rom_data, base_digimon_leveled.defense, enemy_digimon_offset+0xc, 2)    # write new defense
                utils.writeRomBytes(rom_data, base_digimon_leveled.spirit, enemy_digimon_offset+0xe, 2)    # write new spirit
                utils.writeRomBytes(rom_data, base_digimon_leveled.speed, enemy_digimon_offset+0x10, 2)    # write new speed


                cur_offset += 24        # skip 24 bytes to get next encounter
                cur_digimon_id = int.from_bytes(rom_data[cur_offset:cur_offset+2], byteorder="little")

            self.logger.info("Area " + str(area_i) + ": " + ", ".join(new_area_digimon))
            area_offset += 0x200
            area_i += 1





    # patches wild encounters only; tamer digimon are not changed
    def expPatchFlat(self, rom_data: bytearray):

        exp_yield_opt = self.config_manager.get("APPLY_EXP_PATCH_FLAT")
        if exp_yield_opt == ExpYieldConfig.UNCHANGED:
            return
        
        stage_exp_ref = constants.EXP_FLAT_BY_STAGE

        exp_denominator = 7

        if(exp_yield_opt == ExpYieldConfig.INCREASE_HALVED):
            exp_denominator = 14


        # update for every digimon_id (will update only the wild encounters and not the tamers)
        # exp calc: (base_exp * lvl) / 7
        # will change to divide by 14 (7*2) if exp reward is too huge afterwards
        for stage in constants.DIGIMON_IDS:
            for digimon_id in constants.DIGIMON_IDS[stage]:
                enemy_digimon = self.enemyDigimonInfo[constants.DIGIMON_IDS[stage][digimon_id]]
                new_exp_yield = round((stage_exp_ref[stage] * enemy_digimon.level) / exp_denominator)
                enemy_digimon.updateExpYield(new_exp_yield)

                # we always write all of the exp attributes; updateExpYield should change only the ones corresponding to the digimon's species
                utils.writeRomBytes(rom_data, enemy_digimon.holy_exp, enemy_digimon.offset+0x3c, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.dark_exp, enemy_digimon.offset+0x40, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.dragon_exp, enemy_digimon.offset+0x44, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.beast_exp, enemy_digimon.offset+0x48, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.bird_exp, enemy_digimon.offset+0x4c, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.machine_exp, enemy_digimon.offset+0x50, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.aquan_exp, enemy_digimon.offset+0x54, 4) 
                utils.writeRomBytes(rom_data, enemy_digimon.insectplant_exp, enemy_digimon.offset+0x58, 4)

        str_logger_exp = "halved" if exp_yield_opt == ExpYieldConfig.INCREASE_HALVED else "full"

        self.logger.info("Applied exp patch (" + str_logger_exp + ")")



    def randomizeOverworldItems(self,
                                rom_data: bytearray):
        
        config_randomize_overworld_items = self.config_manager.get("RANDOMIZE_OVERWORLD_ITEMS")
        
        if(config_randomize_overworld_items == RandomizeOverworldItems.UNCHANGED):
            return
        
        overworld_item_addrs = constants.OVERWORLD_ITEM_ADDRESSES[self.version]

        item_lookup_table = {
            item_id: category
            for category, (min_id, max_id) in constants.ITEM_TYPE_IDS.items()
            for item_id in range(min_id, max_id + 1)
        }

        non_key_item_ids = [item_id for category, (min_id, max_id) in constants.ITEM_TYPE_IDS.items() if category != "KEY_ITEM" for item_id in range(min_id, max_id + 1)]

        self.logger.info("\n==================== OVERWORLD ITEMS ====================")

        # right now this is using the preset values instead of looking at the rom's current item values; might want to change this in the future
        for addr, item_value in overworld_item_addrs.items():
            item_category = item_lookup_table[item_value]

            # skip key items and digieggs for now
            if(model.ItemType[item_category] in [model.ItemType.KEY_ITEM, model.ItemType.DIGIEGG]):
                continue    

            new_item_value = -1
            if(config_randomize_overworld_items == RandomizeOverworldItems.RANDOMIZE_KEEP_CATEGORY):
                new_item_value = random.randint(*constants.ITEM_TYPE_IDS[item_category])

            if(config_randomize_overworld_items == RandomizeOverworldItems.RANDOMIZE_COMPLETELY):
                new_item_value = random.choice(non_key_item_ids)

            
            # need to eventually determine location of each address
            self.logger.info(hex(addr) + "(" + constants.ITEM_ID_TO_STR[item_value] + ") -> " + constants.ITEM_ID_TO_STR[new_item_value])

            utils.writeRomBytes(rom_data, new_item_value, addr+4, 2)






    def randomizeFixedBattles(self,
                              rom_data: bytearray):
        
        if(not self.config_manager.get("RANDOMIZE_FIXED_BATTLES", False)):
            return
        

        # to accomplish this we randomize every enemy encounter after 0x01f4

        
    def nerfFirstBoss(self,
                      rom_data: bytearray):
        if(not self.config_manager.get("NERF_FIRST_BOSS", False)):
            return
        # id for first city boss is 0x205

        first_boss_data = self.enemyDigimonInfo[0x205]
        nerfed_hp = first_boss_data.hp // 2
        self.logger.info("Nerfed first boss (%d HP -> %d HP)", first_boss_data.hp, nerfed_hp)

        utils.writeRomBytes(rom_data, nerfed_hp, first_boss_data.offset+4, 2)    # write new hp


    def randomizeDigimonSpecies(self,
                                rom_data: bytearray):
        randomize_digimon_species = self.config_manager.get("RANDOMIZE_DIGIMON_SPECIES", RandomizeSpeciesConfig.UNCHANGED)
        if(randomize_digimon_species == RandomizeSpeciesConfig.UNCHANGED):
            return
        
        # randomize species for all entries in baseDigimonInfo
        if(randomize_digimon_species == RandomizeSpeciesConfig.RANDOM):
            self.logger.info("\n==================== DIGIMON SPECIES ====================")
            species_pool = [s for s in model.Species]
            if(not self.config_manager.get("SPECIES_ALLOW_UNKNOWN")):
                species_pool.remove(model.Species.UNKNOWN)

            for digimon_id in self.baseDigimonInfo.keys():
                prev_species = self.baseDigimonInfo[digimon_id].species
                new_species = random.choice(species_pool)

                digimon_name = constants.DIGIMON_ID_TO_STR.get(digimon_id, f"ID_{digimon_id}")

                self.logger.info(f"{digimon_name}: {model.Species(prev_species).name} -> {new_species.name}")

                # overwrite species in baseDigimonInfo to propagate for other modules
                self.baseDigimonInfo[digimon_id].species = new_species

                # 0x3 corresponds to the species info in digimon data
                cur_offset = self.baseDigimonInfo[digimon_id].offset + 3
                utils.writeRomBytes(rom_data, new_species.value, cur_offset, 1)

                # attempt to update for enemyDigimonInfo as well

                corresponding_enemy_data = self.enemyDigimonInfo.get(digimon_id, None)
                if(corresponding_enemy_data == None):
                    # cover edge-cases where digimon_id does not have a match
                    continue
                corresponding_enemy_data.species = new_species

                # 0x3 corresponds to the species info in enemy digimon data as well
                cur_offset = corresponding_enemy_data.offset + 3
                utils.writeRomBytes(rom_data, new_species.value, cur_offset, 1)



    def randomizeElementalResistances(self,
                                      rom_data: bytearray):
        randomize_elemental_resistances = self.config_manager.get("RANDOMIZE_ELEMENTAL_RESISTANCES", RandomizeElementalResistances.UNCHANGED)

        if(randomize_elemental_resistances == RandomizeElementalResistances.UNCHANGED):
            return
        
        self.logger.info("\n==================== DIGIMON ELEMENTAL RESISTANCES ====================")
        
        # randomize resistances for all entries in baseDigimonInfo
        for digimon_id in self.baseDigimonInfo.keys():
            resistance_values = self.baseDigimonInfo[digimon_id].getResistanceValues()
            randomized_values = copy.deepcopy(resistance_values)
            if(randomize_elemental_resistances == RandomizeElementalResistances.SHUFFLE):
                # shuffle values
                random.shuffle(randomized_values)

            if(randomize_elemental_resistances == RandomizeElementalResistances.RANDOM):
                resistances_total = sum(resistance_values)
                # generate fractions
                resistance_fractions = np.random.dirichlet(np.ones(len(resistance_values)))
                randomized_values = np.round(resistance_fractions * resistances_total).astype(int).tolist()

            if(self.config_manager.get("KEEP_SPECIES_RESISTANCE_COHERENCE")):
                cur_digimon_species = self.baseDigimonInfo[digimon_id].species
                main_resistance = model.ELEMENTAL_RESISTANCES.get(cur_digimon_species)
                main_weakness = model.ELEMENTAL_WEAKNESSES.get(cur_digimon_species)

                ix_max = randomized_values.index(max(randomized_values))

                if(main_resistance is not None):
                # this check is needed to cover for [???] values
                    ix_main_res = main_resistance.value
                    randomized_values[ix_max], randomized_values[ix_main_res] = randomized_values[ix_main_res], randomized_values[ix_max]
                    
                ix_min = randomized_values.index(min(randomized_values))
                # this check is needed to cover for [???] values
                if(main_weakness is not None):
                    ix_main_weak = main_weakness.value
                    randomized_values[ix_min], randomized_values[ix_main_weak] = randomized_values[ix_main_weak], randomized_values[ix_min]

            # update baseDigimonInfo and enemyDigimonInfo w randomized resistances
            self.baseDigimonInfo[digimon_id].setResistanceValues(randomized_values)
            self.enemyDigimonInfo[digimon_id].setResistanceValues(randomized_values)

            # write baseDigimonInfo and enemyDigimonInfo into rom
            cur_base_offset = self.baseDigimonInfo[digimon_id].offset + 0x16
            cur_enemy_offset = self.enemyDigimonInfo[digimon_id].offset + 0x14
            cur_resistance_values = self.baseDigimonInfo[digimon_id].getResistanceValues()
            for cur_res_val in cur_resistance_values:
                utils.writeRomBytes(rom_data, cur_res_val, cur_base_offset, 2)
                utils.writeRomBytes(rom_data, cur_res_val, cur_enemy_offset, 2)
                cur_base_offset += 2
                cur_enemy_offset += 2

            
            digimon_name = constants.DIGIMON_ID_TO_STR.get(digimon_id, f"ID_{digimon_id}")
            self.logger.info(f"{digimon_name}: {resistance_values} -> {randomized_values}")


    def randomizeDigimonBaseStats(self,
                                  rom_data: bytearray):
        randomize_base_stats = self.config_manager.get("RANDOMIZE_BASE_STATS", RandomizeBaseStats.UNCHANGED)
        digimon_stattype_bias = self.config_manager.get("BASESTATS_STATTYPE_BIAS", False)
        stattype_bias_mapping = {
            model.DigimonType.ATTACKER: 2,
            model.DigimonType.TANK: 3,
            model.DigimonType.TECHNICAL: 4,
            model.DigimonType.SPEED: 5,
            model.DigimonType.HPTYPE: 0,
            model.DigimonType.MPTYPE: 1
        }

        if(randomize_base_stats == RandomizeBaseStats.UNCHANGED):
            return
        
        self.logger.info("\n==================== DIGIMON BASE STATS ====================")

        for digimon_id in self.baseDigimonInfo.keys():
            previous_basestats = self.baseDigimonInfo[digimon_id].getBaseStats()
            new_basestats = copy.deepcopy(previous_basestats)

            
            # shuffle atk, def, spirit, speed
            if(randomize_base_stats == RandomizeBaseStats.SHUFFLE):
                # cut array to get only the target attrs
                stats_to_shuffle = previous_basestats[2:6]
                random.shuffle(stats_to_shuffle)

                if(digimon_stattype_bias):
                    biased_stat_ix = stattype_bias_mapping.get(self.baseDigimonInfo[digimon_id].digimon_type, None)
                    # exclude BALANCE, HPTYPE, MPTYPE
                    if(biased_stat_ix is not None and biased_stat_ix >= 2):
                        highest_stat_ix = stats_to_shuffle.index(max(stats_to_shuffle))

                        stats_to_shuffle[highest_stat_ix], stats_to_shuffle[biased_stat_ix - 2] = stats_to_shuffle[biased_stat_ix - 2], stats_to_shuffle[highest_stat_ix]

                # update current_basestats with new stats
                new_basestats[2:6] = stats_to_shuffle
                self.baseDigimonInfo[digimon_id].setBaseStats(new_basestats)


            if(randomize_base_stats == RandomizeBaseStats.RANDOM_SANITY):

                # exclude aptitude
                base_stat_total = sum(new_basestats[0:6])

                hp_ratio = random.uniform(0.2, 0.3)
                mp_ratio = random.uniform(0.2, 0.3)
                atk_ratio = random.uniform(0.1, 0.2)
                def_ratio = random.uniform(0.1, 0.2)
                spirit_ratio = random.uniform(0.1, 0.2)
                speed_ratio = random.uniform(0.1, 0.2)

                ratio_array = [hp_ratio, mp_ratio, atk_ratio, def_ratio, spirit_ratio, speed_ratio]
                total_ratios = sum(ratio_array)
                new_basestats[0:6] = [round((ratio * base_stat_total) / total_ratios) for ratio in ratio_array]


                if(digimon_stattype_bias):
                    biased_stat_ix = stattype_bias_mapping.get(self.baseDigimonInfo[digimon_id].digimon_type, None)
                    # exclude BALANCE
                    if(biased_stat_ix is not None):
                        # do not eval APTITUDE from max()
                        search_range = (
                            [0, 1] if biased_stat_ix in {0, 1} else     # HP/MP
                            range(2, 6)                                 # Atk/Def/Spirit/Speed
                        )

                        # find the highest stat IN THE RELEVANT RANGE
                        highest_stat_ix = max(
                            search_range,
                            key=lambda i: new_basestats[i]
                        )
                     
                        new_basestats[highest_stat_ix], new_basestats[biased_stat_ix] = new_basestats[biased_stat_ix], new_basestats[highest_stat_ix]


                self.baseDigimonInfo[digimon_id].setBaseStats(new_basestats)

                # write updated hp and mp first
                utils.writeRomBytes(rom_data, new_basestats[0], self.baseDigimonInfo[digimon_id].offset + 0x4, 2)
                utils.writeRomBytes(rom_data, new_basestats[1], self.baseDigimonInfo[digimon_id].offset + 0x8, 2)


            if(randomize_base_stats == RandomizeBaseStats.RANDOM_COMPLETELY):
                
                # exclude aptitude, take away 160 from the stats to add later
                base_stat_total = sum(new_basestats[0:6]) - 160

                # generate fractions
                stat_fractions = np.random.dirichlet(np.ones(6))
                randomized_values = np.round(stat_fractions * base_stat_total).astype(int)
                
                # sum baseline values; the 160 we took away are distributed here
                randomized_values += np.array([40, 40, 20, 20, 20, 20], dtype=int)
                new_basestats[0:6] = randomized_values.tolist()


                if(digimon_stattype_bias):
                    biased_stat_ix = stattype_bias_mapping.get(self.baseDigimonInfo[digimon_id].digimon_type, None)
                    # exclude BALANCE
                    if(biased_stat_ix is not None):
                        # do not eval APTITUDE from max()

                        highest_stat_ix = new_basestats.index(max(new_basestats[0:6]))
                     
                        new_basestats[highest_stat_ix], new_basestats[biased_stat_ix] = new_basestats[biased_stat_ix], new_basestats[highest_stat_ix]


                self.baseDigimonInfo[digimon_id].setBaseStats(new_basestats)

                # write updated hp and mp first
                utils.writeRomBytes(rom_data, new_basestats[0], self.baseDigimonInfo[digimon_id].offset + 0x4, 2)
                utils.writeRomBytes(rom_data, new_basestats[1], self.baseDigimonInfo[digimon_id].offset + 0x8, 2)



            # write updated stats into rom
            cur_base_offset = self.baseDigimonInfo[digimon_id].offset + 0xa
            for cur_stat_value in new_basestats[2:6]:
                utils.writeRomBytes(rom_data, cur_stat_value, cur_base_offset, 2)
                cur_base_offset += 2

            digimon_name = constants.DIGIMON_ID_TO_STR.get(digimon_id, f"ID_{digimon_id}")
            self.logger.info(f"{digimon_name}: {previous_basestats} -> {new_basestats}")

        
    
    def randomizeDigimonStatType(self,
                                 rom_data: bytearray):
        randomize_stat_type = self.config_manager.get("RANDOMIZE_DIGIMON_STATTYPE", RandomizeDigimonStatType.UNCHANGED)

        if(randomize_stat_type == RandomizeDigimonStatType.UNCHANGED):
            return
        
        if(randomize_stat_type == RandomizeDigimonStatType.RANDOMIZE):
            self.logger.info("\n==================== DIGIMON STAT TYPES ====================")
            
            # randomize stat type for all entries in baseDigimonInfo
            for digimon_id in self.baseDigimonInfo.keys():
                current_type = copy.deepcopy(self.baseDigimonInfo[digimon_id].digimon_type)
                randomized_type_ix = random.randrange(len(model.DigimonType))

                # update baseDigimonInfo with new StatType
                self.baseDigimonInfo[digimon_id].digimon_type = model.DigimonType(randomized_type_ix)
               
                # write new statType into rom
                cur_offset = self.baseDigimonInfo[digimon_id].offset + 0x2d
                utils.writeRomBytes(rom_data, randomized_type_ix, cur_offset, 1)

                digimon_name = constants.DIGIMON_ID_TO_STR.get(digimon_id, f"ID_{digimon_id}")
                self.logger.info(f"{digimon_name}: {current_type.name} -> {self.baseDigimonInfo[digimon_id].digimon_type.name}")


    def randomizeDigimonMovesets(self,
                                 rom_data: bytearray):
        randomize_movesets = self.config_manager.get("RANDOMIZE_MOVESETS", RandomizeMovesets.UNCHANGED)
        MOVESET_SPECIES_BIAS = 0.9


        if(randomize_movesets == RandomizeMovesets.UNCHANGED):
            # check for guaranteeBasicMove is done inside the function as it returns immediately if setting is UNCHANGED
            if(self.config_manager.get("MOVESETS_GUARANTEE_BASIC_MOVE", False)):
                self.guaranteeBasicMove(rom_data)
            return
        
        learned_moves_pool = copy.deepcopy(self.moveDataArray[:196])
        signature_moves_pool = copy.deepcopy(self.moveDataArray[196:503])

        target_regular_moves_pool = [] + learned_moves_pool
        target_signature_moves_pool = [] + signature_moves_pool

        moveset_level_bias = self.config_manager.get("MOVESETS_LEVEL_BIAS", False)
        regular_move_power_bias = self.config_manager.get("REGULAR_MOVE_POWER_BIAS", False)
        signature_move_power_bias = self.config_manager.get("SIGNATURE_MOVE_POWER_BIAS", False)


        # add signature moves to regular moves pool
        if(self.config_manager.get("MOVESETS_SIGNATURE_MOVES_POOL", False)):
            target_regular_moves_pool += signature_moves_pool

        
            
        # randomize digimon movesets; only randomize valid base digimon ids since we're replacing movesets on the enemies as well

        for digimon_id in constants.DIGIMON_ID_TO_STR.keys():
            
            current_regular_moves_pool = list(target_regular_moves_pool)
            digimon_moves = self.baseDigimonInfo[digimon_id].getRegularMoves()
            current_randomized_regular_moves = []
            for move_id in digimon_moves:

                possible_movepool = list(set(current_regular_moves_pool).difference(current_randomized_regular_moves))  # do not repeat moves
    
                if(moveset_level_bias):     # filter by level
                    if(move_id < len(self.moveDataArray)):     # if move does not exist, then keep the original movepool (move is still randomized into a legitimate one)
                        previous_move = self.moveDataArray[move_id]
                        # if no moves pass the filter, filterMovesByLevel() returns the received movepool
                        possible_movepool = utils.filterMovesByLevel(previous_move, possible_movepool)

                if(regular_move_power_bias):    # filter by move power
                    if(move_id < len(self.moveDataArray)):     # if move does not exist, then keep the original movepool (move is still randomized into a legitimate one)
                        previous_move = self.moveDataArray[move_id]
                        # if no moves pass the filter, filterMovesByLevel() returns the received movepool
                        possible_movepool = utils.filterMovesByPower(previous_move, possible_movepool)
                    

                if(randomize_movesets == RandomizeMovesets.RANDOM_SPECIES_BIAS):
                    probability_array = []
                    cur_digimon_element = model.ELEMENTAL_RESISTANCES.get(model.Species(self.baseDigimonInfo[digimon_id].species), None)
                    total_matching_moves = sum(move.element == cur_digimon_element for move in possible_movepool)
                    if(total_matching_moves > 0):
                        for m in possible_movepool:
                            if(m.element == cur_digimon_element):
                                probability_array.append(MOVESET_SPECIES_BIAS / total_matching_moves)
                            else:
                                probability_array.append((1 - MOVESET_SPECIES_BIAS) / (len(possible_movepool) - total_matching_moves))
                        current_randomized_regular_moves.append(random.choices(possible_movepool, weights=probability_array, k=1)[0])
                    else:
                        current_randomized_regular_moves.append(random.choice(possible_movepool))

                if(randomize_movesets == RandomizeMovesets.RANDOM_COMPLETELY):
                    current_randomized_regular_moves.append(random.choice(possible_movepool))

            # randomize signature move

            prev_signature_move_id = self.baseDigimonInfo[digimon_id].move_signature
            possible_signature_movepool = list(set(target_signature_moves_pool).difference(current_randomized_regular_moves))  # do not repeat moves

            if(signature_move_power_bias):    # filter by move power
                if(prev_signature_move_id < len(self.moveDataArray)):     # if move does not exist, then keep the original movepool (move is still randomized into a legitimate one)
                    previous_move = self.moveDataArray[prev_signature_move_id]
                    # if no moves pass the filter, filterMovesByLevel() returns the received movepool
                    possible_movepool = utils.filterMovesByPower(previous_move, possible_signature_movepool)

            if(randomize_movesets == RandomizeMovesets.RANDOM_SPECIES_BIAS):
                probability_array = []
                cur_digimon_element = model.ELEMENTAL_RESISTANCES.get(self.baseDigimonInfo[digimon_id].species, None)
                total_matching_moves = sum(move.element == cur_digimon_element for move in possible_signature_movepool)
                if(total_matching_moves > 0):
                    for m in possible_signature_movepool:
                        if(m.element == cur_digimon_element):
                            probability_array.append(MOVESET_SPECIES_BIAS / total_matching_moves)
                        else:
                            probability_array.append((1 - MOVESET_SPECIES_BIAS) / (len(possible_signature_movepool) - total_matching_moves))
                    current_signature_move = random.choices(possible_signature_movepool, weights=probability_array, k=1)[0]
                else:
                    current_signature_move = random.choice(possible_signature_movepool)

            if(randomize_movesets == RandomizeMovesets.RANDOM_COMPLETELY):
                current_signature_move = random.choice(possible_signature_movepool)

            # update base digimon moves and enemy digimon moves
            self.baseDigimonInfo[digimon_id].setRegularMoves([m.id for m in current_randomized_regular_moves])
            self.enemyDigimonInfo[digimon_id].setRegularMoves([m.id for m in current_randomized_regular_moves])
            move_offset = 0x30
            for regular_move in current_randomized_regular_moves:        # we can do this since moves start at 0x30 for both base digimon and enemy digimon
                utils.writeRomBytes(rom_data, regular_move.id, self.baseDigimonInfo[digimon_id].offset + move_offset, 2)
                utils.writeRomBytes(rom_data, regular_move.id, self.enemyDigimonInfo[digimon_id].offset + move_offset, 2)
                move_offset += 0x2

            # update signature moves for both as well
            self.baseDigimonInfo[digimon_id].move_signature = current_signature_move.id
            self.enemyDigimonInfo[digimon_id].move_signature = current_signature_move.id
            utils.writeRomBytes(rom_data, current_signature_move.id, self.baseDigimonInfo[digimon_id].offset + 0x2e, 2)
            utils.writeRomBytes(rom_data, current_signature_move.id, self.enemyDigimonInfo[digimon_id].offset + 0x2e, 2)


        
        if(self.config_manager.get("MOVESETS_GUARANTEE_BASIC_MOVE", False)):
            self.guaranteeBasicMove(rom_data)

        # print logs
        self.logger.info("\n==================== MOVESETS ====================")
        updated_move_table = []

        for digimon_id in constants.DIGIMON_ID_TO_STR.keys():
            cur_digimon_basedata = self.baseDigimonInfo[digimon_id]
            cur_digimon_log = []
            cur_digimon_log.append(constants.DIGIMON_ID_TO_STR[digimon_id])
            for move_id in cur_digimon_basedata.getRegularMoves():
                cur_digimon_log.append(constants.MOVE_ARRAY_STR[move_id] if move_id < len(constants.MOVE_ARRAY_STR) else "-")
            cur_digimon_log.append(constants.MOVE_ARRAY_STR[cur_digimon_basedata.move_signature] if cur_digimon_basedata.move_signature < len(constants.MOVE_ARRAY_STR) else "-")
            updated_move_table.append(cur_digimon_log)
        
        log_table = tabulate(updated_move_table, headers=["Digimon", "Move 1", "Move 2", "Move 3", "Move 4", "Signature Move"])
        self.logger.info(f"\n{log_table}")

    
    def randomizeDigimonTraits(self,
                               rom_data: bytearray):
        
        randomize_traits = self.config_manager.get("RANDOMIZE_TRAITS", RandomizeTraits.UNCHANGED)
        if(randomize_traits == RandomizeTraits.UNCHANGED):
            return
        
        FORCE_FOUR_TRAITS = self.config_manager.get("TRAITS_FORCE_FOUR", False)
        ENABLE_UNUSED_TRAITS = self.config_manager.get("TRAITS_ENABLE_UNUSED", False)

        # easier to set as all traits in the beginning
        all_regular_traits = list(set(sum((constants.TRAITS_REGULAR_BY_STAGE[stage] for stage in constants.STAGE_NAMES), [])))
        all_support_traits = list(set(sum((constants.TRAITS_SUPPORT_BY_STAGE[stage] for stage in constants.STAGE_NAMES), [])))

        if(ENABLE_UNUSED_TRAITS):
            # do not need to convert into set here since these are not repeated
            all_regular_traits += constants.TRAITS_REGULAR_BY_STAGE["OTHER"]

        for digimon_id in constants.DIGIMON_ID_TO_STR.keys():
            new_traits = []
            regular_traits_pool = []
            support_traits_pool = []
            regular_traits = self.baseDigimonInfo[digimon_id].getRegularTraits()

            if(randomize_traits == RandomizeTraits.RANDOM_STAGE_BIAS):
                # set regular traits pool as specific for the stage
                cur_digimon_stage = utils.getDigimonStage(digimon_id)
                regular_traits_pool = list(constants.TRAITS_REGULAR_BY_STAGE[cur_digimon_stage])
                support_traits_pool = list(constants.TRAITS_SUPPORT_BY_STAGE[cur_digimon_stage])
                if(cur_digimon_stage in ["ULTIMATE", "MEGA"] and ENABLE_UNUSED_TRAITS):
                    # do not need to convert into set here since these are not repeated
                    regular_traits_pool += constants.TRAITS_REGULAR_BY_STAGE["OTHER"]
                    
            if (randomize_traits == RandomizeTraits.RANDOM_COMPLETELY):
                regular_traits_pool = list(all_regular_traits)
                support_traits_pool = list(all_support_traits)
                if(ENABLE_UNUSED_TRAITS):
                    regular_traits_pool += constants.TRAITS_REGULAR_BY_STAGE["OTHER"]

            
            for trait_id in regular_traits:
                # skip trait if force four is disabled and trait is not defined
                if(trait_id == 0xff and not FORCE_FOUR_TRAITS):
                    new_traits.append(trait_id)
                    continue

                # do this w indexes so that we pop the trait each time; otherwise we'd have to cover repeating traits another way
                new_trait_ix = random.randrange(len(regular_traits_pool))
                new_traits.append(regular_traits_pool.pop(new_trait_ix))

            # in the case of the support trait we don't need to pop since it's only one
            new_support_trait = random.choice(support_traits_pool)


            # update base digimon traits and enemy digimon traits
            self.baseDigimonInfo[digimon_id].setRegularTraits(new_traits)
            self.enemyDigimonInfo[digimon_id].setRegularTraits(new_traits)
            trait_base_offset = 0x28
            trait_enemy_offset = 0x26
            for regular_trait in new_traits:     # distinct writes since base and enemy deal w trait ids differently
                utils.writeRomBytes(rom_data, regular_trait, self.baseDigimonInfo[digimon_id].offset + trait_base_offset, 1)
                utils.writeRomBytes(rom_data, regular_trait, self.enemyDigimonInfo[digimon_id].offset + trait_enemy_offset, 2)
                trait_base_offset += 0x1
                trait_enemy_offset += 0x2

            # update support traits (only for base digimon since enemy does not have support trait)
            self.baseDigimonInfo[digimon_id].support_trait = new_support_trait
            utils.writeRomBytes(rom_data, new_support_trait, self.baseDigimonInfo[digimon_id].offset + 0x2c, 1)
                

        # print logs
        self.logger.info("\n==================== TRAITS ====================")
        updated_trait_table = []

        for digimon_id in constants.DIGIMON_ID_TO_STR.keys():
            cur_digimon_basedata = self.baseDigimonInfo[digimon_id]
            cur_digimon_log = []
            cur_digimon_log.append(constants.DIGIMON_ID_TO_STR[digimon_id])
            for trait_id in cur_digimon_basedata.getRegularTraits():
                cur_digimon_log.append(constants.TRAIT_ARRAY_STR[trait_id] if trait_id < len(constants.TRAIT_ARRAY_STR) else "-")
            cur_digimon_log.append(constants.TRAIT_ARRAY_STR[cur_digimon_basedata.support_trait] if cur_digimon_basedata.support_trait < len(constants.TRAIT_ARRAY_STR) else "-")
            updated_trait_table.append(cur_digimon_log)
        
        log_table = tabulate(updated_trait_table, headers=["Digimon", "Trait 1", "Trait 2", "Trait 3", "Trait 4", "Support Trait"])
        self.logger.info(f"\n{log_table}")
            



        

    def guaranteeBasicMove(self,
                           rom_data: bytearray):
        
        if(self.config_manager.get("MOVESETS_GUARANTEE_BASIC_MOVE", False)):
            
            # change Charge to have 8 base power and 0 MP
            # Charge's move ID is 0
            move_charge = self.moveDataArray[0]
            move_charge.primary_value = 8
            move_charge.mp_cost = 0

            # write move Charge to rom
            utils.writeRomBytes(rom_data, move_charge.primary_value, move_charge.offset + 8, 2)
            utils.writeRomBytes(rom_data, move_charge.mp_cost, move_charge.offset + 2, 2)
            
            # set first move of all base digimon and enemy digimon to Charge (id = 0)
            for digimon_id in self.baseDigimonInfo.keys():
                if(0x0 in self.baseDigimonInfo[digimon_id].getRegularMoves() + [self.baseDigimonInfo[digimon_id].move_signature]):
                    # skip if digimon already has Charge in its movepool
                    continue
                self.baseDigimonInfo[digimon_id].move_1 = 0
                utils.writeRomBytes(rom_data, 0, self.baseDigimonInfo[digimon_id].offset + 0x30, 2)
            
            for digimon_id in self.enemyDigimonInfo.keys():
                if(0x0 in self.baseDigimonInfo[digimon_id].getRegularMoves() + [self.baseDigimonInfo[digimon_id].move_signature]):
                    # skip if digimon already has Charge in its movepool
                    continue
                self.enemyDigimonInfo[digimon_id].move_1 = 0
                utils.writeRomBytes(rom_data, 0, self.enemyDigimonInfo[digimon_id].offset + 0x30, 2)


            self.logger.info(f"Changed Charge to 8 base power and 0 MP")
            self.logger.info(f"Set Charge as first move for all digimon")

        


    def randomizeDigivolutions(self,
                               rom_data: bytearray):
        if(not self.config_manager.get("RANDOMIZE_DIGIVOLUTIONS")):
            return
        
        digimon_to_randomize = copy.deepcopy(constants.DIGIMON_IDS)     # this will be used to iterate through all digimon
        digimon_pool_selection = copy.deepcopy(constants.DIGIMON_IDS)   # this will be used to define if a given digimon is available or not
        generated_conditions = {}
        pre_evos = {}
        generated_evolutions = {}

        if(not self.config_manager.get("RANDOMIZE_DIGIVOLUTION_CONDITIONS")):
            # do initial scan to add base digivolution conditions to generated_conditions
            # this is used to randomize the digivolutions but keep any original conditions as they were
            for s in range(len(constants.STAGE_NAMES)):
                stage = constants.STAGE_NAMES[s]
                for digimon_id in list(digimon_to_randomize[stage].values()):
                    hex_addr = constants.DIGIVOLUTION_ADDRESSES[self.version][digimon_id]
                    digivolution_info = utils.loadDigivolutionInformation(rom_data, hex_addr)
                    for k in digivolution_info.keys():
                        generated_conditions[k] = digivolution_info[k]

        self.logger.info("\n==================== DIGIVOLUTIONS ====================")
        for s in range(len(constants.STAGE_NAMES)):
            stage = constants.STAGE_NAMES[s]
            logger_dict = {v: k for k, v in digimon_to_randomize[stage].items()}
            stage_ids = list(digimon_to_randomize[stage].values())
            evo_amount_distribution = constants.DIGIVOLUTION_AMOUNT_DISTRIBUTION[stage]

            self.logger.info("\n==================== " + stage + " ====================")
            random.shuffle(stage_ids)
            for digimon_id in stage_ids:

                log_digimon_name = logger_dict[digimon_id]
                self.logger.info("\n" + log_digimon_name)
                hex_addr = constants.DIGIVOLUTION_ADDRESSES[self.version][digimon_id]
                evos_amount = np.random.choice(list(range(len(evo_amount_distribution))), p=evo_amount_distribution)
                
                hasPreDigivolution = digimon_id in pre_evos.keys()      # hotfix to avoid deadlocking due to lvl requirement higher than aptitude
                
                self.logger.info("Digivolutions: %d", evos_amount)
                #log_evo_names = []
                evo_ids = []
                evo_conditions_debug = []             # setting this here to avoid lvl requirement deadlocking
                for e in range(evos_amount):
                    try:
                        # pick evo digimon id
                        evo_digi_name = random.choice(list(digimon_pool_selection[constants.STAGE_NAMES[s+1]].keys()))
                        if(self.config_manager.get("DIGIVOLUTIONS_SIMILAR_SPECIES", False)):
                            evo_species_prob_dist = np.array(utils.generateSpeciesProbDistribution(digimon_pool_selection[constants.STAGE_NAMES[s+1]], self.baseDigimonInfo, self.config_manager.get("DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS"), self.baseDigimonInfo[digimon_id].species))
                            evo_species_prob_dist /= evo_species_prob_dist.sum()
                            evo_digi_name = np.random.choice(list(digimon_pool_selection[constants.STAGE_NAMES[s+1]].keys()), p=evo_species_prob_dist)
                        evo_digi_id = digimon_pool_selection[constants.STAGE_NAMES[s+1]].pop(evo_digi_name)              # this ensures there are no repeated digimon
                        #log_evo_names.append(evo_digi_name)
                        #self.logger.info("Digivolution " + str(e+1) + ": " + evo_digi_name)

                        # if randomize conditions is enabled, base conditions are overriden; if digimon doesn't have conditions yet, then new conditions are generated for it
                        if(self.config_manager.get("RANDOMIZE_DIGIVOLUTION_CONDITIONS") or evo_digi_id not in generated_conditions.keys()):
                            # generate conditions for evo digimon
                            # no need to override w/ hasPreDigivolution here
                            if(self.config_manager.get("DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP")):
                                conditions_evo = utils.generateBiasedConditions(s+1, self.config_manager.get("DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS"), [self.baseDigimonInfo[evo_digi_id].species])
                            else:
                                conditions_evo = utils.generateConditions(s+1)    # [[condition id (hex), value (int)], ...]
                            generated_conditions[evo_digi_id] = conditions_evo
                            evo_conditions_debug.append(conditions_evo)

                            #log_conditions = [constants.DIGIVOLUTION_CONDITIONS[cond_el[0]] + ": " + str(cond_el[1]) for cond_el in conditions_evo]
                            #self.logger.info(" | ".join(log_conditions))


                        # add pre-evo register to propagate conditions on next cycles
                        pre_evos[evo_digi_id] = digimon_id

                        # add evo_id to current digimon's evo ids
                        evo_ids.append(evo_digi_id)

                    except IndexError:
                        self.logger.debug("No more digimon in the pool, skip current evos")
                        continue


                # if conditions do not exist for current digimon, generate them
                # NOTE: right now this is inefficient, will randomize up to three times unecessarily in order to account for generatedConditions already being filled at the start if Digimon Conditions is left unchanged
                if(self.config_manager.get("RANDOMIZE_DIGIVOLUTION_CONDITIONS") or digimon_id not in generated_conditions.keys()):
                    if(self.config_manager.get("DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP")):
                        conditions_cur = utils.generateBiasedConditions(s, self.config_manager.get("DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS"), [self.baseDigimonInfo[digimon_id].species])
                    else:
                        conditions_cur = utils.generateConditions(s)

                    # check hasPreDigivolution here since we do not know
                    # if it does not have a predigivolution (and it does have at least a digivolution), change one of them randomly to match aptitude level
                    
                    if(not hasPreDigivolution):
                        log_deadlock = utils.checkAptitudeDeadlockTuple(evo_conditions_debug, self.baseDigimonInfo[digimon_id].aptitude)
                        # no need to return anything other than log, conditions_evo changes are propagated by reference
                        if(log_deadlock != ""):
                            self.logger.info(log_deadlock)

                    generated_conditions[digimon_id] = conditions_cur


                # write to rom

                # pre-evo section

                if(digimon_id in pre_evos.keys()):
                    utils.writeRomBytes(rom_data, pre_evos[digimon_id], hex_addr, 4)
                    conditions_cur = generated_conditions[pre_evos[digimon_id]]

                    # write log for pre-digivolution
                    self.logger.info("Pre-digivolution: " +  constants.DIGIMON_ID_TO_STR[pre_evos[digimon_id]])

                    log_conditions = [constants.DIGIVOLUTION_CONDITIONS[cond_el[0]] + ": " + str(cond_el[1]) for cond_el in conditions_cur]
                    self.logger.info(" | ".join(log_conditions))

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

                        # write log for digivolution
                        self.logger.info("Digivolution " + str(i+1) + ": " +  constants.DIGIMON_ID_TO_STR[cur_evo_id])
                        log_conditions = [constants.DIGIVOLUTION_CONDITIONS[cond_el[0]] + ": " + str(cond_el[1]) for cond_el in conditions_cur]
                        self.logger.info(" | ".join(log_conditions))

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

                generated_evolutions[digimon_id] = evo_ids
                #self.logger.info(log_digimon_name + " -> " + str(log_evo_names))

        return pre_evos, generated_evolutions

    def randomizeDigivolutionConditionsOnly(self,
                                            rom_data: bytearray):
        # This randomizes digivolution conditions without changing the original digivolutions
        # digivolution conditions -> unchanged
        # digivolution conditions -> random
        # follow species exp may be enabled
        # only replace existing conditions; new conditions do not have to be created
        # need to track generated conditions


        # extra check to ensure that we don't run this if digivolutions were already randomized: 
        if(self.config_manager.get("RANDOMIZE_DIGIVOLUTIONS") not in [None, RandomizeDigivolutions.UNCHANGED]):
            return

        self.logger.info("\n==================== DIGIVOLUTIONS ====================")
        generated_conditions = {}
        for stage in constants.DIGIMON_IDS:
            self.logger.info("\n==================== " + stage + " ====================")
            for digimon_name in constants.DIGIMON_IDS[stage]:
                self.logger.info("\n" + digimon_name)
                digimon_id = constants.DIGIMON_IDS[stage][digimon_name]
                hex_addr = constants.DIGIVOLUTION_ADDRESSES[self.version][digimon_id]
                hasPreDigivolution = True           # hotfix to avoid deadlocking due to lvl requirement higher than aptitude

                # do a similar operation to loadDigivolutionInformation but writing immediately and propagating the info
                digivolution_hex_info = rom_data[hex_addr:hex_addr+0x70]            # length of digivolution info for a given digimon is always 0x70

                data_to_write = []      # make it like this so that conditions are only written at the end; this allows us to check for the aptitude requirement
                
                # check up to 4 ids; if the id is different than 0xffffffff, then it's a valid digimon
                for n in range(4):
                    evo_digimon_id = int.from_bytes(digivolution_hex_info[n*4:(n*4)+4], byteorder="little")
                    evo_stage_int = constants.STAGE_NAMES.index(stage) - 1 if n == 0 else constants.STAGE_NAMES.index(stage) + 1    # [0, 1, 2, 3, 4]
                    if(evo_digimon_id == 0xffffffff):
                        if(n == 0):         # change hasPreDigivolution to false
                            hasPreDigivolution = False
                        continue

                    digivolution_baseinfo = self.baseDigimonInfo[evo_digimon_id]    # load this to account for biased conditions
                    base_conditions = []
                    for c in range(3):  # check up to 3 conditions: if condition id is different than 0x0, then it's a valid condition
                        cur_pointer = 16 + (24*n) + (8*c)
                        condition_id = int.from_bytes(digivolution_hex_info[cur_pointer:cur_pointer+4], byteorder="little")
                        condition_value = int.from_bytes(digivolution_hex_info[cur_pointer+4:cur_pointer+8], byteorder="little")
                        if(condition_id == 0x0):
                            continue
                        base_conditions.append([condition_id, condition_value])
                    
                    if(len(base_conditions) > 0):
                        if(evo_digimon_id in generated_conditions.keys()):
                            conditions_evo = generated_conditions[evo_digimon_id]
                        elif(self.config_manager.get("DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP")):
                            conditions_evo = utils.generateBiasedConditions(evo_stage_int, self.config_manager.get("DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS"), [digivolution_baseinfo.species], max_conditions=len(base_conditions))
                            generated_conditions[evo_digimon_id] = conditions_evo
                        else:
                            conditions_evo = utils.generateConditions(evo_stage_int, max_conditions=len(base_conditions))
                            generated_conditions[evo_digimon_id] = conditions_evo

                        log_conditions = [constants.DIGIVOLUTION_CONDITIONS[cond_el[0]] + ": " + str(cond_el[1]) for cond_el in conditions_evo]
                        prepend_info = "Pre-digivolution: " if n == 0 else "Digivolution " + str(n) + ": "

                        self.logger.info(prepend_info + constants.DIGIMON_ID_TO_STR[evo_digimon_id])
                        self.logger.info(" | ".join(log_conditions))

                        # write conditions_evo in the corresponding memory
                        cur_pointer = 16 + (24*n)   # no need for (8*c) here; we'll increase the pointer as we go
                        for condition in conditions_evo:
                            condition_id = condition[0]
                            condition_value = condition[1]
                            #utils.writeRomBytes(rom_data, condition_id, hex_addr + cur_pointer, 4)
                            #utils.writeRomBytes(rom_data, condition_value, hex_addr + cur_pointer + 4, 4)
                            condition_data = {}
                            condition_data["condition_id"] = condition_id
                            condition_data["condition_value"] = condition_value
                            condition_data["base_addr"] = hex_addr + cur_pointer
                            data_to_write.append(condition_data)
                            cur_pointer += 8    # advance to next condition

                if not hasPreDigivolution:
                    data_to_write, log_deadlock = utils.checkAptitudeDeadlockDict(data_to_write, self.baseDigimonInfo[digimon_id].aptitude)
                    if(log_deadlock != ""):
                        self.logger.info(log_deadlock)

                for condition in data_to_write:
                    utils.writeRomBytes(rom_data, condition["condition_id"], condition["base_addr"], 4)
                    utils.writeRomBytes(rom_data, condition["condition_value"], condition["base_addr"] + 4, 4)

        return generated_conditions


    def manageDnaDigivolutions(self,
                               rom_data: bytearray):
        
        dna_digivolutions_var = self.config_manager.get("RANDOMIZE_DNADIGIVOLUTIONS")
        dna_digivolution_conditions_var = self.config_manager.get("RANDOMIZE_DNADIGIVOLUTION_CONDITIONS")

        # define mapping between original digimon id and target digimon id
        # this is essentially the only way to ensure that dna digivolutions remain structured

        mapping_digimon_ids = {}

        # map digimon ids between same stage
        if(dna_digivolutions_var == RandomizeDnaDigivolutions.RANDOMIZE_SAME_STAGE):
            self.logger.info("\n==================== DNA DIGIMON MAPPING ====================")
            for stage in constants.DIGIMON_IDS:
                cur_digimon_sorted = list(copy.deepcopy(constants.DIGIMON_IDS[stage]).items())
                random.shuffle(cur_digimon_sorted)
                ix = 0
                for d_name, d_id in constants.DIGIMON_IDS[stage].items():
                    mapping_digimon_ids[d_id] = cur_digimon_sorted[ix][1]
                    self.logger.info(f"{d_name} -> {cur_digimon_sorted[ix][0]}")
                    ix += 1

        # map digimon ids between any stage
        if(dna_digivolutions_var == RandomizeDnaDigivolutions.RANDOMIZE_COMPLETELY):
            self.logger.info("\n==================== DNA DIGIMON MAPPING ====================")
            cur_digimon_sorted = list(copy.deepcopy(constants.DIGIMON_ID_TO_STR).items())
            random.shuffle(cur_digimon_sorted)
            ix = 0
            for d_id, d_name in constants.DIGIMON_ID_TO_STR.items():
                mapping_digimon_ids[d_id] = cur_digimon_sorted[ix][0]
                self.logger.info(f"{d_name} -> {cur_digimon_sorted[ix][1]}")
                ix += 1


        # replace digimon ids for all dna digivolution objects
        for dnaDigivolutionObj in self.dnaDigivolutions:
            # skip if no randomization to perform
            if(dna_digivolutions_var == RandomizeDnaDigivolutions.UNCHANGED):
                break
            dnaDigivolutionObj.digimon_1_id = mapping_digimon_ids.get(dnaDigivolutionObj.digimon_1_id, dnaDigivolutionObj.digimon_1_id)
            dnaDigivolutionObj.digimon_2_id = mapping_digimon_ids.get(dnaDigivolutionObj.digimon_2_id, dnaDigivolutionObj.digimon_2_id)
            dnaDigivolutionObj.dna_evolution_id = mapping_digimon_ids.get(dnaDigivolutionObj.dna_evolution_id, dnaDigivolutionObj.dna_evolution_id)


        # replace/generate dna digivolution conditions
        if(dna_digivolution_conditions_var == RandomizeDnaDigivolutionConditions.UNCHANGED):
            if(dna_digivolutions_var == RandomizeDnaDigivolutions.UNCHANGED):
                # no changes to be made
                return
            
            for dnaDigivolutionObj in self.dnaDigivolutions:
                if(dnaDigivolutionObj.dna_evolution_id in self.dnaConditionsByDigimonId.keys()):
                    # maintain original dna digivolution conditions
                    cur_dnadigivolution_conditions = self.dnaConditionsByDigimonId[dnaDigivolutionObj.dna_evolution_id]
                    dnaDigivolutionObj.setConditionsFromArray(cur_dnadigivolution_conditions)
                else:
                    # generate conditions for dna digivolutions that did not exist
                    cur_dnadigivolution_stage = constants.STAGE_NAMES.index(utils.getDigimonStage(dnaDigivolutionObj.dna_evolution_id))
                    species_array = [self.baseDigimonInfo[dnaDigivolutionObj.digimon_1_id].species,
                                     self.baseDigimonInfo[dnaDigivolutionObj.digimon_2_id].species,
                                     self.baseDigimonInfo[dnaDigivolutionObj.dna_evolution_id].species]

                    conditions_evo = utils.generateBiasedConditions(cur_dnadigivolution_stage, self.config_manager.get("DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS"), species_array) if(self.config_manager.get("DNADIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP")) else utils.generateConditions(cur_dnadigivolution_stage)
                    conditions_evo += [[0, 0]] * (3 - len(conditions_evo))  # pad w/ empty conditions/values if result does not have 3 conditions

                    # set conditions
                    dnaDigivolutionObj.setConditionsFromArray(conditions_evo)


        if(dna_digivolution_conditions_var == RandomizeDnaDigivolutionConditions.RANDOMIZE):
            
            for dnaDigivolutionObj in self.dnaDigivolutions:
                cur_dnadigivolution_stage = constants.STAGE_NAMES.index(utils.getDigimonStage(dnaDigivolutionObj.dna_evolution_id))
                species_array = [self.baseDigimonInfo[dnaDigivolutionObj.digimon_1_id].species,
                                 self.baseDigimonInfo[dnaDigivolutionObj.digimon_2_id].species,
                                 self.baseDigimonInfo[dnaDigivolutionObj.dna_evolution_id].species]

                conditions_evo = utils.generateBiasedConditions(cur_dnadigivolution_stage, self.config_manager.get("DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS"), species_array) if(self.config_manager.get("DNADIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP")) else utils.generateConditions(cur_dnadigivolution_stage)
                conditions_evo += [[0, 0]] * (3 - len(conditions_evo))  # pad w/ empty conditions/values if result does not have 3 conditions

                # set conditions
                dnaDigivolutionObj.setConditionsFromArray(conditions_evo)
                
        
        if(dna_digivolution_conditions_var == RandomizeDnaDigivolutionConditions.REMOVED):
            for dnaDigivolutionObj in self.dnaDigivolutions:
                dnaDigivolutionObj.removeRequirements()


        # write and log dna digivolutions

        self.logger.info("\n==================== DNA DIGIVOLUTIONS ====================")
        sorted_dnaDigivolutions = sorted(self.dnaDigivolutions, key=lambda x: x.dna_evolution_id)
        for dnaDigivolutionObj in sorted_dnaDigivolutions:
            dnaDigivolutionObj.writeDnaDigivolutionToRom(rom_data)
            self.logger.info(dnaDigivolutionObj.getDnaDigivolutionLog())
        self.logger.info("\n")
        





if __name__ == '__main__':
    
    log_stream = StringIO()
    logger = logging.getLogger(__name__)
    #logging.basicConfig(stream=log_stream, level=logging.INFO)
    logging.basicConfig(stream=log_stream, level=logging.INFO,  format='%(message)s')
    logger.info("Creating new rom from source \"" + PATH_SOURCE + "\"")

    config_manager = ConfigManager()
    config_manager.update_from_ui(default_configmanager_settings)
    
    rom = DigimonROM(PATH_SOURCE, config_manager, logger)
    rom.executeQolChanges()
    randomizer = Randomizer(rom.version, rom.rom_data, config_manager, logger)
    '''
    curEnemyDigimonInfo = randomizer.enemyDigimonInfo

    randomizer.randomizeStarters(rom.rom_data)
    curEnemyDigimonInfo = randomizer.randomizeAreaEncounters(rom.rom_data)      # returned enemyDigimonInfo is taken into account for the exp patch
    randomizer.nerfFirstBoss(rom.rom_data)
    randomizer.randomizeDigivolutions(rom.rom_data)

    randomizer.expPatchFlat(rom.rom_data, curEnemyDigimonInfo)
    '''
    randomizer.executeRandomizerFunctions()
    rom.writeRom(PATH_TARGET)
    print(log_stream.getvalue())