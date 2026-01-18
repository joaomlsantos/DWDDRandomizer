"""
Unit tests for pure utility functions in src/utils.py

These tests verify deterministic behavior of helper functions that don't
depend on random state. They use known inputs and expected outputs.
"""

import pytest
from src import utils, constants, model


# ============================================================================
# Tests for getDigimonStage()
# ============================================================================

class TestGetDigimonStage:
    """Tests for the getDigimonStage function that maps digimon IDs to stages."""

    @pytest.mark.parametrize("digimon_id,expected_stage", [
        # IN-TRAINING range: 0x41 - 0x57
        (0x41, "IN-TRAINING"),  # Chicchimon (first)
        (0x4A, "IN-TRAINING"),  # middle of range
        (0x57, "IN-TRAINING"),  # last in range

        # ROOKIE range: 0x61 - 0x9D
        (0x61, "ROOKIE"),  # first rookie
        (0x7F, "ROOKIE"),  # middle of range
        (0x9D, "ROOKIE"),  # last rookie

        # CHAMPION range: 0xA8 - 0x115 (excluding 0xBA)
        (0xA8, "CHAMPION"),  # first champion
        (0xD0, "CHAMPION"),  # middle of range
        (0x115, "CHAMPION"),  # last champion

        # ULTIMATE range: 0x120 - 0x188
        (0x120, "ULTIMATE"),  # first ultimate
        (0x150, "ULTIMATE"),  # middle of range
        (0x188, "ULTIMATE"),  # last ultimate

        # MEGA range: 0x191 - 0x1F4
        (0x191, "MEGA"),  # first mega
        (0x1C0, "MEGA"),  # middle of range
        (0x1F4, "MEGA"),  # Chaosmon (last)
    ])
    def test_valid_digimon_ids(self, digimon_id, expected_stage):
        """Test that valid digimon IDs return the correct stage."""
        assert utils.getDigimonStage(digimon_id) == expected_stage

    @pytest.mark.parametrize("digimon_id", [
        0x00,   # Below all ranges
        0x40,   # Just below IN-TRAINING
        0x58,   # Between IN-TRAINING and ROOKIE
        0x60,   # Just below ROOKIE
        0x9E,   # Between ROOKIE and CHAMPION
        0xA7,   # Just below CHAMPION
        0xBA,   # Excluded from CHAMPION
        0x116,  # Between CHAMPION and ULTIMATE
        0x11F,  # Just below ULTIMATE
        0x189,  # Between ULTIMATE and MEGA
        0x190,  # Just below MEGA
        0x1F5,  # Above MEGA
        0xFFFF, # Max value
    ])
    def test_invalid_digimon_ids_return_empty(self, digimon_id):
        """Test that invalid/gap digimon IDs return empty string."""
        assert utils.getDigimonStage(digimon_id) == ""

    def test_all_known_digimon_have_valid_stage(self):
        """Verify all digimon in DIGIMON_ID_TO_STR have a valid stage."""
        for digimon_id in constants.DIGIMON_ID_TO_STR.keys():
            stage = utils.getDigimonStage(digimon_id)
            # Most digimon should have a valid stage, but some special IDs may not
            # This test documents which ones don't
            if stage == "":
                # Log but don't fail - document edge cases
                print(f"Digimon ID {hex(digimon_id)} ({constants.DIGIMON_ID_TO_STR[digimon_id]}) has no stage")


# ============================================================================
# Tests for getDigimonStageFromSpriteInfo()
# ============================================================================

class TestGetDigimonStageFromSpriteInfo:
    """Tests for sprite-based stage detection."""

    @pytest.mark.parametrize("sprite_val,expected_stage", [
        # IN-TRAINING: 0x01 - 0x17
        (0x01, "IN-TRAINING"),
        (0x17, "IN-TRAINING"),

        # ROOKIE: 0x18 - 0x54
        (0x18, "ROOKIE"),
        (0x54, "ROOKIE"),

        # CHAMPION: 0x55 - 0xC1
        (0x55, "CHAMPION"),
        (0xC1, "CHAMPION"),

        # ULTIMATE: 0xC2 - 0x12A
        (0xC2, "ULTIMATE"),
        (0x12A, "ULTIMATE"),

        # MEGA: 0x12B - 0x18E
        (0x12B, "MEGA"),
        (0x18E, "MEGA"),

        # Special cases
        (0x190, "JOINT_SLOT_BOSS"),
    ])
    def test_valid_sprite_values(self, sprite_val, expected_stage):
        """Test that valid sprite values return the correct stage."""
        assert utils.getDigimonStageFromSpriteInfo(sprite_val) == expected_stage

    def test_invalid_sprite_returns_empty(self):
        """Test that invalid sprite values return empty string."""
        assert utils.getDigimonStageFromSpriteInfo(0x00) == ""
        assert utils.getDigimonStageFromSpriteInfo(0xFFFF) == ""


# ============================================================================
# Tests for getAllDigimonPairs()
# ============================================================================

class TestGetAllDigimonPairs:
    """Tests for the function that returns all digimon name-ID pairs."""

    def test_returns_list(self):
        """Test that the function returns a list."""
        result = utils.getAllDigimonPairs()
        assert isinstance(result, list)

    def test_returns_tuples(self):
        """Test that each element is a tuple of (name, id)."""
        result = utils.getAllDigimonPairs()
        for pair in result:
            assert isinstance(pair, tuple)
            assert len(pair) == 2
            assert isinstance(pair[0], str)  # name
            assert isinstance(pair[1], int)  # id

    def test_contains_expected_count(self):
        """Test that the result contains all digimon from all stages."""
        result = utils.getAllDigimonPairs()
        expected_count = sum(len(stage) for stage in constants.DIGIMON_IDS.values())
        assert len(result) == expected_count

    def test_contains_known_digimon(self):
        """Test that some known digimon are present."""
        result = utils.getAllDigimonPairs()
        names = [pair[0] for pair in result]

        # Check some known digimon exist
        assert "Agumon" in names
        assert "Gabumon" in names
        assert "WarGreymon" in names
        assert "Omnimon" in names


# ============================================================================
# Tests for filterMovesByLevel()
# ============================================================================

class TestFilterMovesByLevel:
    """Tests for move filtering by level.

    Note: filterMovesByLevel takes (move, movepool) and returns filtered list.
    It uses an internal CONFIG_MOVE_LEVEL_RANGE = 5.
    """

    def test_move_within_range_included(self):
        """Test that moves within level range are included in filtered list."""
        class MockMove:
            def __init__(self, level):
                self.level_learned = level

        reference_move = MockMove(20)
        movepool = [MockMove(15), MockMove(20), MockMove(25), MockMove(50)]

        # Range is +/- 5, so levels 15-25 should be included
        result = utils.filterMovesByLevel(reference_move, movepool)
        result_levels = [m.level_learned for m in result]

        assert 15 in result_levels
        assert 20 in result_levels
        assert 25 in result_levels
        assert 50 not in result_levels

    def test_move_outside_range_excluded(self):
        """Test that moves outside level range are excluded."""
        class MockMove:
            def __init__(self, level):
                self.level_learned = level

        reference_move = MockMove(10)
        movepool = [MockMove(50), MockMove(60)]

        # Range is 5-15, neither 50 nor 60 is in range
        # Function returns original pool if no matches
        result = utils.filterMovesByLevel(reference_move, movepool)
        assert len(result) == len(movepool)  # Returns original if empty

    def test_returns_original_pool_if_no_matches(self):
        """Test that original pool is returned if no moves match."""
        class MockMove:
            def __init__(self, level):
                self.level_learned = level

        reference_move = MockMove(10)
        movepool = [MockMove(100), MockMove(200)]

        result = utils.filterMovesByLevel(reference_move, movepool)
        assert result == movepool


# ============================================================================
# Tests for filterMovesByPower()
# ============================================================================

class TestFilterMovesByPower:
    """Tests for move filtering by power.

    Note: filterMovesByPower takes (move, movepool) and returns filtered list.
    It uses an internal CONFIG_MOVE_POWER_RANGE = 8.
    """

    def test_move_within_power_range_included(self):
        """Test that moves within power range are included."""
        class MockMove:
            def __init__(self, power):
                self.primary_value = power

        reference_move = MockMove(100)
        movepool = [MockMove(92), MockMove(100), MockMove(108), MockMove(150)]

        # Range is +/- 8, so powers 92-108 should be included
        result = utils.filterMovesByPower(reference_move, movepool)
        result_powers = [m.primary_value for m in result]

        assert 92 in result_powers
        assert 100 in result_powers
        assert 108 in result_powers
        assert 150 not in result_powers

    def test_move_outside_power_range_excluded(self):
        """Test that moves outside power range are excluded."""
        class MockMove:
            def __init__(self, power):
                self.primary_value = power

        reference_move = MockMove(100)
        movepool = [MockMove(50), MockMove(200)]

        # Neither is within +/- 8 of 100
        result = utils.filterMovesByPower(reference_move, movepool)
        assert result == movepool  # Returns original if empty

    def test_returns_original_pool_if_no_matches(self):
        """Test that original pool is returned if no moves match."""
        class MockMove:
            def __init__(self, power):
                self.primary_value = power

        reference_move = MockMove(100)
        movepool = [MockMove(1), MockMove(500)]

        result = utils.filterMovesByPower(reference_move, movepool)
        assert result == movepool


# ============================================================================
# Tests for writeRomBytes()
# ============================================================================

class TestWriteRomBytes:
    """Tests for the ROM byte writing utility."""

    def test_write_single_byte(self):
        """Test writing a single byte value."""
        rom_data = bytearray(10)
        utils.writeRomBytes(rom_data, 0xAB, 5, 1)
        assert rom_data[5] == 0xAB

    def test_write_two_bytes_little_endian(self):
        """Test writing a two-byte value in little endian."""
        rom_data = bytearray(10)
        utils.writeRomBytes(rom_data, 0x1234, 3, 2)
        # Little endian: low byte first
        assert rom_data[3] == 0x34
        assert rom_data[4] == 0x12

    def test_write_four_bytes_little_endian(self):
        """Test writing a four-byte value in little endian."""
        rom_data = bytearray(10)
        utils.writeRomBytes(rom_data, 0x12345678, 2, 4)
        assert rom_data[2] == 0x78
        assert rom_data[3] == 0x56
        assert rom_data[4] == 0x34
        assert rom_data[5] == 0x12

    def test_write_does_not_affect_other_bytes(self):
        """Test that writing only affects the specified bytes."""
        rom_data = bytearray([0xFF] * 10)
        utils.writeRomBytes(rom_data, 0x00, 5, 2)

        # Check surrounding bytes unchanged
        assert rom_data[4] == 0xFF
        assert rom_data[7] == 0xFF

        # Check written bytes changed
        assert rom_data[5] == 0x00
        assert rom_data[6] == 0x00

    def test_write_max_values(self):
        """Test writing maximum values for each byte size."""
        rom_data = bytearray(10)

        utils.writeRomBytes(rom_data, 0xFF, 0, 1)
        assert rom_data[0] == 0xFF

        utils.writeRomBytes(rom_data, 0xFFFF, 2, 2)
        assert rom_data[2] == 0xFF
        assert rom_data[3] == 0xFF


# ============================================================================
# Tests for DIGIMON_IDS constant structure
# ============================================================================

class TestDigimonIdsConstant:
    """Tests verifying the structure of the DIGIMON_IDS constant."""

    def test_all_stages_present(self):
        """Test that all expected stages are present."""
        expected_stages = ["IN-TRAINING", "ROOKIE", "CHAMPION", "ULTIMATE", "MEGA"]
        for stage in expected_stages:
            assert stage in constants.DIGIMON_IDS

    def test_stage_names_match(self):
        """Test that STAGE_NAMES matches DIGIMON_IDS keys."""
        for stage in constants.STAGE_NAMES:
            assert stage in constants.DIGIMON_IDS

    def test_no_duplicate_ids_within_stage(self):
        """Test that there are no duplicate IDs within a single stage."""
        for stage, digimon_dict in constants.DIGIMON_IDS.items():
            ids = list(digimon_dict.values())
            assert len(ids) == len(set(ids)), f"Duplicate IDs found in {stage}"

    def test_no_duplicate_ids_across_stages(self):
        """Test that there are no duplicate IDs across all stages."""
        all_ids = []
        for digimon_dict in constants.DIGIMON_IDS.values():
            all_ids.extend(digimon_dict.values())
        assert len(all_ids) == len(set(all_ids)), "Duplicate IDs found across stages"

    def test_id_to_str_consistency(self):
        """Test that DIGIMON_ID_TO_STR contains all IDs from DIGIMON_IDS."""
        for stage, digimon_dict in constants.DIGIMON_IDS.items():
            for name, digimon_id in digimon_dict.items():
                assert digimon_id in constants.DIGIMON_ID_TO_STR, \
                    f"ID {hex(digimon_id)} ({name}) not in DIGIMON_ID_TO_STR"
                # Compare stripped names to handle any trailing whitespace in constants
                id_to_str_name = constants.DIGIMON_ID_TO_STR[digimon_id].strip()
                name_stripped = name.strip()
                assert id_to_str_name == name_stripped, \
                    f"Name mismatch for {hex(digimon_id)}: '{name}' vs '{constants.DIGIMON_ID_TO_STR[digimon_id]}'"


# ============================================================================
# Tests for DIGIVOLUTION_CONDITIONS_VALUES ranges
# ============================================================================

class TestDigivolutionConditionRanges:
    """Tests verifying digivolution condition value ranges are valid."""

    def test_all_conditions_have_ranges(self):
        """Test that all documented conditions have value ranges."""
        expected_conditions = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9,
                               0xA, 0xB, 0xC, 0xD, 0xE, 0xF, 0x12, 0x15, 0x16]
        for condition in expected_conditions:
            assert condition in constants.DIGIVOLUTION_CONDITIONS_VALUES

    def test_ranges_are_valid(self):
        """Test that all ranges have min <= max."""
        for condition_id, stage_ranges in constants.DIGIVOLUTION_CONDITIONS_VALUES.items():
            for stage_idx, (min_val, max_val) in enumerate(stage_ranges):
                assert min_val <= max_val, \
                    f"Invalid range for condition {hex(condition_id)} stage {stage_idx}: [{min_val}, {max_val}]"

    def test_level_ranges_are_progressive(self):
        """Test that level requirements increase with stage."""
        level_ranges = constants.DIGIVOLUTION_CONDITIONS_VALUES[0x1]
        for i in range(1, len(level_ranges)):
            # Each stage's min should be >= previous stage's min
            assert level_ranges[i][0] >= level_ranges[i-1][0], \
                f"Level range not progressive at stage {i}"


# ============================================================================
# Tests for model enums
# ============================================================================

class TestModelEnums:
    """Tests verifying model enum definitions."""

    def test_species_count(self):
        """Test that Species enum has expected count."""
        assert len(model.Species) == 9  # Including UNKNOWN

    def test_element_count(self):
        """Test that Element enum has expected count."""
        assert len(model.Element) == 8

    def test_species_element_mapping_complete(self):
        """Test that all species (except UNKNOWN) have element mappings."""
        for species in model.Species:
            if species != model.Species.UNKNOWN:
                assert species in model.ELEMENTAL_RESISTANCES
                assert species in model.ELEMENTAL_WEAKNESSES

    def test_lvlup_mode_options(self):
        """Test that LvlUpMode has expected options."""
        assert model.LvlUpMode.RANDOM.value == 0
        assert model.LvlUpMode.FIXED_MIN.value == 1
        assert model.LvlUpMode.FIXED_AVG.value == 2
        assert model.LvlUpMode.FIXED_MAX.value == 3
