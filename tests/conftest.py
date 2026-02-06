"""
Pytest configuration and shared fixtures for the DWDD Randomizer test suite.

This module provides:
- Centralized ROM path configuration
- Reusable fixtures for ROM loading and randomizer instances
- Helpers for seed management and test isolation
"""

import os
import copy
import random
import logging
from io import StringIO
from typing import Generator, Tuple

import pytest
import numpy as np

from configs import (
    ConfigManager,
    ExpYieldConfig,
    RandomizeBaseStats,
    RandomizeDigimonStatType,
    RandomizeDigivolutionConditions,
    RandomizeDigivolutions,
    RandomizeDnaDigivolutionConditions,
    RandomizeDnaDigivolutions,
    RandomizeElementalResistances,
    RandomizeEnemyDigimonEncounters,
    RandomizeItems,
    RandomizeMovesets,
    RandomizeSpeciesConfig,
    RandomizeStartersConfig,
    RandomizeTraits,
    RandomizeWildEncounters,
    RookieResetConfig,
)
from src import model


# ============================================================================
# PATH CONFIGURATION
# ============================================================================
# These can be overridden via environment variables for CI/CD or different machines

def get_rom_paths() -> Tuple[str, str]:
    """Get ROM paths from environment or use defaults."""
    dawn_path = os.environ.get(
        "DWDD_ROM_DAWN",
        "C:/Workspace/digimon_stuffs/rom_files/1421 - Digimon World - Dawn (USA).nds"
    )
    dusk_path = os.environ.get(
        "DWDD_ROM_DUSK",
        "C:/Workspace/digimon_stuffs/rom_files/1420 - Digimon World - Dusk (US).nds"
    )
    return dawn_path, dusk_path


PATH_SOURCE_DAWN, PATH_SOURCE_DUSK = get_rom_paths()


# ============================================================================
# DEFAULT TEST SETTINGS
# ============================================================================
# All settings set to UNCHANGED/False - tests can override as needed

DEFAULT_TEST_SETTINGS = {
    # QoL settings
    "INCREASE_TEXT_SPEED": False,
    "INCREASE_MOVEMENT_SPEED": False,
    "REDUCE_WILD_ENCOUNTER_RATE": False,
    "CHANGE_STAT_CAPS": False,
    "EXPAND_PLAYER_NAME_LENGTH": False,
    "INCREASE_DIGIMON_EXP": ExpYieldConfig.UNCHANGED,
    "INCREASE_SCAN_RATE": False,
    "INCREASE_FARM_EXP": False,
    "UNLOCK_VERSION_EXCLUSIVE_AREAS": False,

    # Starters
    "RANDOMIZE_STARTERS": RandomizeStartersConfig.UNCHANGED,
    "ROOKIE_RESET_EVENT": RookieResetConfig.UNCHANGED,
    "NERF_FIRST_BOSS": False,
    "FORCE_STARTER_W_ROOKIE_STAGE": False,

    # Wild encounters
    "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters.UNCHANGED,
    "BALANCE_CALUMON_STATS": False,
    "WILD_ENCOUNTERS_STATS": model.LvlUpMode.FIXED_AVG,
    "INCREASE_WILD_ENCOUNTER_MONEY": False,
    "RANDOMIZE_WILD_ENCOUNTER_ITEMS": RandomizeItems.UNCHANGED,

    # Fixed battles
    "RANDOMIZE_FIXED_BATTLES": RandomizeEnemyDigimonEncounters.UNCHANGED,

    # Species
    "RANDOMIZE_DIGIMON_SPECIES": RandomizeSpeciesConfig.UNCHANGED,
    "SPECIES_ALLOW_UNKNOWN": False,
    "RANDOMIZE_ELEMENTAL_RESISTANCES": RandomizeElementalResistances.UNCHANGED,
    "KEEP_SPECIES_RESISTANCE_COHERENCE": False,

    # Base stats
    "RANDOMIZE_BASE_STATS": RandomizeBaseStats.UNCHANGED,
    "BASESTATS_STATTYPE_BIAS": False,
    "RANDOMIZE_DIGIMON_STATTYPE": RandomizeDigimonStatType.UNCHANGED,

    # Movesets
    "RANDOMIZE_MOVESETS": RandomizeMovesets.UNCHANGED,
    "MOVESETS_LEVEL_BIAS": False,
    "REGULAR_MOVE_POWER_BIAS": False,
    "SIGNATURE_MOVE_POWER_BIAS": False,
    "MOVESETS_SIGNATURE_MOVES_POOL": False,
    "MOVESETS_GUARANTEE_BASIC_MOVE": False,

    # Traits
    "RANDOMIZE_TRAITS": RandomizeTraits.UNCHANGED,
    "TRAITS_FORCE_FOUR": False,
    "TRAITS_ENABLE_UNUSED": False,

    # Digivolutions
    "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.UNCHANGED,
    "DIGIVOLUTIONS_SIMILAR_SPECIES": False,
    "DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS": 0.9,
    "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions.UNCHANGED,
    "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": False,
    "DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS": 0.2,

    # DNA Digivolutions
    "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions.UNCHANGED,
    "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions.UNCHANGED,
    "DNADIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": False,

    # Items
    "RANDOMIZE_OVERWORLD_ITEMS": RandomizeItems.UNCHANGED,
    "RANDOMIZE_QUEST_ITEM_REWARDS": RandomizeItems.UNCHANGED,

    # Quests
    "ENABLE_LEGENDARY_TAMER_QUEST": False,
    "UNLOCK_MAIN_QUESTS_IN_SEQUENCE": False,

    # Internal settings
    "MOVEMENT_SPEED_MULTIPLIER": 1.5,
    "ENCOUNTER_RATE_MULTIPLIER": 0.5,
    "NEW_BASE_SCAN_RATE": 25,
    "FARM_EXP_MODIFIER": 10,
    "ENCOUNTER_MONEY_MULTIPLIER": 4,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_config_manager(settings: dict = None) -> ConfigManager:
    """Create a ConfigManager with the given settings (or defaults)."""
    config = ConfigManager()
    base_settings = copy.deepcopy(DEFAULT_TEST_SETTINGS)
    if settings:
        base_settings.update(settings)
    config.update_from_ui(base_settings)
    return config


def create_logger() -> Tuple[logging.Logger, StringIO]:
    """Create a logger that writes to a StringIO for test inspection."""
    log_stream = StringIO()
    logger = logging.getLogger(f"test_logger_{id(log_stream)}")
    logger.handlers = []  # Clear any existing handlers
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger, log_stream


def set_seed(seed: int):
    """Set both random and numpy random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def reset_random_state():
    """Reset random state to a known value for test isolation."""
    set_seed(42)


# ============================================================================
# FIXTURES - ROM Loading
# ============================================================================

@pytest.fixture
def rom_paths() -> Tuple[str, str]:
    """Provide ROM paths as a fixture for tests that need them."""
    return PATH_SOURCE_DAWN, PATH_SOURCE_DUSK


@pytest.fixture
def dawn_rom_path() -> str:
    """Provide Dawn ROM path."""
    return PATH_SOURCE_DAWN


@pytest.fixture
def dusk_rom_path() -> str:
    """Provide Dusk ROM path."""
    return PATH_SOURCE_DUSK


# ============================================================================
# FIXTURES - DigimonROM instances
# ============================================================================

@pytest.fixture
def rom_dawn():
    """Load a fresh Dawn ROM instance with default settings."""
    from qol_script import DigimonROM

    if not os.path.exists(PATH_SOURCE_DAWN):
        pytest.skip(f"Dawn ROM not found at {PATH_SOURCE_DAWN}")

    config = create_config_manager()
    logger, _ = create_logger()
    return DigimonROM(PATH_SOURCE_DAWN, config, logger)


@pytest.fixture
def rom_dusk():
    """Load a fresh Dusk ROM instance with default settings."""
    from qol_script import DigimonROM

    if not os.path.exists(PATH_SOURCE_DUSK):
        pytest.skip(f"Dusk ROM not found at {PATH_SOURCE_DUSK}")

    config = create_config_manager()
    logger, _ = create_logger()
    return DigimonROM(PATH_SOURCE_DUSK, config, logger)


@pytest.fixture(params=["DAWN_US", "DUSK_US"])
def rom_both(request) -> Generator:
    """Parametrized fixture that runs tests against both Dawn and Dusk ROMs."""
    from qol_script import DigimonROM

    path = PATH_SOURCE_DAWN if request.param == "DAWN_US" else PATH_SOURCE_DUSK

    if not os.path.exists(path):
        pytest.skip(f"{request.param} ROM not found at {path}")

    config = create_config_manager()
    logger, _ = create_logger()
    rom = DigimonROM(path, config, logger)
    rom.version_name = request.param  # Add version name for test context
    yield rom


# ============================================================================
# FIXTURES - Randomizer instances
# ============================================================================

@pytest.fixture
def randomizer_dawn(rom_dawn):
    """Create a Randomizer instance for Dawn ROM."""
    from qol_script import Randomizer

    reset_random_state()
    return Randomizer(
        rom_dawn.version,
        rom_dawn.rom_data,
        rom_dawn.config_manager,
        rom_dawn.logger
    )


@pytest.fixture
def randomizer_dusk(rom_dusk):
    """Create a Randomizer instance for Dusk ROM."""
    from qol_script import Randomizer

    reset_random_state()
    return Randomizer(
        rom_dusk.version,
        rom_dusk.rom_data,
        rom_dusk.config_manager,
        rom_dusk.logger
    )


@pytest.fixture(params=["DAWN", "DUSK"])
def randomizer_both(request) -> Generator:
    """Parametrized fixture that runs tests against randomizers for both versions."""
    from qol_script import DigimonROM, Randomizer

    path = PATH_SOURCE_DAWN if request.param == "DAWN" else PATH_SOURCE_DUSK

    if not os.path.exists(path):
        pytest.skip(f"{request.param} ROM not found at {path}")

    config = create_config_manager()
    logger, log_stream = create_logger()
    rom = DigimonROM(path, config, logger)

    reset_random_state()
    randomizer = Randomizer(rom.version, rom.rom_data, config, logger)
    randomizer.version_name = request.param
    randomizer.log_stream = log_stream
    yield randomizer


# ============================================================================
# FIXTURES - Isolated randomizer (fresh copy per test)
# ============================================================================

@pytest.fixture
def fresh_randomizer_dawn():
    """Create an isolated Randomizer with a fresh ROM copy for mutation tests."""
    from qol_script import DigimonROM, Randomizer

    if not os.path.exists(PATH_SOURCE_DAWN):
        pytest.skip(f"Dawn ROM not found at {PATH_SOURCE_DAWN}")

    config = create_config_manager()
    logger, log_stream = create_logger()
    rom = DigimonROM(PATH_SOURCE_DAWN, config, logger)

    # Create a copy of rom_data so mutations don't affect other tests
    rom_data_copy = bytearray(rom.rom_data)

    reset_random_state()
    randomizer = Randomizer(rom.version, rom_data_copy, config, logger)
    randomizer.log_stream = log_stream
    return randomizer


# ============================================================================
# FIXTURES - Config manager variations
# ============================================================================

@pytest.fixture
def config_unchanged() -> ConfigManager:
    """ConfigManager with all settings unchanged."""
    return create_config_manager()


@pytest.fixture
def config_all_random() -> ConfigManager:
    """ConfigManager with all randomization settings enabled."""
    settings = {
        "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL,
        "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY,
        "RANDOMIZE_FIXED_BATTLES": RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_COMPLETELY,
        "RANDOMIZE_DIGIMON_SPECIES": RandomizeSpeciesConfig.RANDOM,
        "RANDOMIZE_ELEMENTAL_RESISTANCES": RandomizeElementalResistances.RANDOM,
        "RANDOMIZE_BASE_STATS": RandomizeBaseStats.RANDOM_COMPLETELY,
        "RANDOMIZE_DIGIMON_STATTYPE": RandomizeDigimonStatType.RANDOMIZE,
        "RANDOMIZE_MOVESETS": RandomizeMovesets.RANDOM_COMPLETELY,
        "RANDOMIZE_TRAITS": RandomizeTraits.RANDOM_COMPLETELY,
        "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.RANDOMIZE,
        "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions.RANDOMIZE,
        "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions.RANDOMIZE_COMPLETELY,
        "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions.RANDOMIZE,
        "RANDOMIZE_OVERWORLD_ITEMS": RandomizeItems.RANDOMIZE_COMPLETELY,
        "RANDOMIZE_QUEST_ITEM_REWARDS": RandomizeItems.RANDOMIZE_COMPLETELY,
        "RANDOMIZE_WILD_ENCOUNTER_ITEMS": RandomizeItems.RANDOMIZE_COMPLETELY,
    }
    return create_config_manager(settings)


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_rom: marks tests that require ROM files to be present"
    )
    config.addinivalue_line(
        "markers", "dawn_only: marks tests that only run on Dawn ROM"
    )
    config.addinivalue_line(
        "markers", "dusk_only: marks tests that only run on Dusk ROM"
    )
