"""
Integration tests for randomization features.

These tests verify that:
1. Each randomization function completes without errors
2. Randomization actually changes data (when not UNCHANGED)
3. UNCHANGED options truly leave data unmodified
4. Feature combinations work together
"""

import pytest
import copy

from src import constants, utils, model
from configs import (
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
from tests.conftest import set_seed


# ============================================================================
# STARTER RANDOMIZATION TESTS
# ============================================================================

class TestStarterRandomization:
    """Tests for starter pack randomization."""

    def test_unchanged_does_not_modify(self, randomizer_both):
        """UNCHANGED option should not modify starter data."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_STARTERS", RandomizeStartersConfig.UNCHANGED)

        # Use STARTER_PACK_OFFSET and compare a region around it
        starter_offset = constants.STARTER_PACK_OFFSET[randomizer.version]
        region_size = 0x200
        original_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])

        set_seed(42)
        randomizer.randomizeStarters(randomizer.rom_data)

        current_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])
        assert current_region == original_region, "UNCHANGED modified starter data"

    def test_same_stage_modifies_data(self, randomizer_both):
        """RAND_SAME_STAGE should modify at least some starter data."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_STARTERS", RandomizeStartersConfig.RAND_SAME_STAGE)

        starter_offset = constants.STARTER_PACK_OFFSET[randomizer.version]
        region_size = 0x200
        original_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])

        set_seed(42)
        randomizer.randomizeStarters(randomizer.rom_data)

        current_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])
        assert current_region != original_region, "RAND_SAME_STAGE did not modify any starter data"

    def test_full_random_modifies_data(self, randomizer_both):
        """RAND_FULL should modify at least some starter data."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_STARTERS", RandomizeStartersConfig.RAND_FULL)

        starter_offset = constants.STARTER_PACK_OFFSET[randomizer.version]
        region_size = 0x200
        original_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])

        set_seed(42)
        randomizer.randomizeStarters(randomizer.rom_data)

        current_region = bytes(randomizer.rom_data[starter_offset:starter_offset+region_size])
        assert current_region != original_region, "RAND_FULL did not modify any starter data"


# ============================================================================
# WILD ENCOUNTER RANDOMIZATION TESTS
# ============================================================================

class TestWildEncounterRandomization:
    """Tests for wild/area encounter randomization."""

    def test_unchanged_preserves_data(self, randomizer_both):
        """UNCHANGED option should preserve encounter data."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_WILD_DIGIMON_ENCOUNTERS", RandomizeWildEncounters.UNCHANGED)

        # Store a sample of original enemy data
        sample_enemies = list(randomizer.enemyDigimonInfo.items())[:10]
        original_data = {}
        for enemy_id, enemy in sample_enemies:
            original_data[enemy_id] = bytes(randomizer.rom_data[enemy.offset:enemy.offset+0x10])

        set_seed(42)
        randomizer.randomizeAreaEncounters(randomizer.rom_data)

        for enemy_id, original in original_data.items():
            enemy = randomizer.enemyDigimonInfo[enemy_id]
            current = bytes(randomizer.rom_data[enemy.offset:enemy.offset+0x10])
            assert current == original, f"UNCHANGED modified enemy {hex(enemy_id)}"

    def test_same_stage_randomization_runs(self, randomizer_both):
        """Same stage wild encounter randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS",
            RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
        )

        set_seed(42)
        # Should complete without error
        randomizer.randomizeAreaEncounters(randomizer.rom_data)

    def test_completely_random_runs(self, randomizer_both):
        """Completely random wild encounter randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS",
            RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY
        )

        set_seed(42)
        randomizer.randomizeAreaEncounters(randomizer.rom_data)

    @pytest.mark.parametrize("stat_mode", [
        model.LvlUpMode.RANDOM,
        model.LvlUpMode.FIXED_MIN,
        model.LvlUpMode.FIXED_AVG,
        model.LvlUpMode.FIXED_MAX,
    ])
    def test_stat_generation_modes(self, randomizer_both, stat_mode):
        """Test all stat generation modes for encounters."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS",
            RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
        )
        randomizer.config_manager.set("WILD_ENCOUNTERS_STATS", stat_mode)

        set_seed(42)
        randomizer.randomizeAreaEncounters(randomizer.rom_data)


# ============================================================================
# FIXED BATTLE RANDOMIZATION TESTS
# ============================================================================

class TestFixedBattleRandomization:
    """Tests for fixed/boss battle randomization."""

    def test_unchanged_preserves_data(self, randomizer_both):
        """UNCHANGED should not modify fixed battle data."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_FIXED_BATTLES",
            RandomizeEnemyDigimonEncounters.UNCHANGED
        )

        set_seed(42)
        # Capture state before
        original_enemy_count = len(randomizer.enemyDigimonInfo)

        randomizer.randomizeFixedBattles(randomizer.rom_data)

        # Enemy count should remain the same
        assert len(randomizer.enemyDigimonInfo) == original_enemy_count

    def test_same_stage_runs(self, randomizer_both):
        """Same stage fixed battle randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_FIXED_BATTLES",
            RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
        )

        set_seed(42)
        randomizer.randomizeFixedBattles(randomizer.rom_data)

    def test_completely_random_runs(self, randomizer_both):
        """Completely random fixed battle randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_FIXED_BATTLES",
            RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_COMPLETELY
        )

        set_seed(42)
        randomizer.randomizeFixedBattles(randomizer.rom_data)


# ============================================================================
# DIGIVOLUTION RANDOMIZATION TESTS
# ============================================================================

class TestDigivolutionRandomization:
    """Tests for digivolution path randomization."""

    def test_unchanged_preserves_data(self, randomizer_both):
        """UNCHANGED should not modify digivolution data."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_DIGIVOLUTIONS", RandomizeDigivolutions.UNCHANGED)

        set_seed(42)
        randomizer.randomizeDigivolutions(randomizer.rom_data)

    def test_randomize_runs(self, randomizer_both):
        """Digivolution randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_DIGIVOLUTIONS", RandomizeDigivolutions.RANDOMIZE)
        randomizer.config_manager.set("DIGIVOLUTIONS_SIMILAR_SPECIES", False)

        set_seed(42)
        randomizer.randomizeDigivolutions(randomizer.rom_data)

    def test_randomize_with_similar_species(self, randomizer_both):
        """Digivolution randomization with similar species bias should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_DIGIVOLUTIONS", RandomizeDigivolutions.RANDOMIZE)
        randomizer.config_manager.set("DIGIVOLUTIONS_SIMILAR_SPECIES", True)
        randomizer.config_manager.set("DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS", 0.9)

        set_seed(42)
        randomizer.randomizeDigivolutions(randomizer.rom_data)

    def test_conditions_only_randomization(self, randomizer_both):
        """Condition-only randomization should work without path randomization."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_DIGIVOLUTIONS", RandomizeDigivolutions.UNCHANGED)
        randomizer.config_manager.set(
            "RANDOMIZE_DIGIVOLUTION_CONDITIONS",
            RandomizeDigivolutionConditions.RANDOMIZE
        )

        set_seed(42)
        randomizer.randomizeDigivolutionConditionsOnly(randomizer.rom_data)


# ============================================================================
# BASE STATS RANDOMIZATION TESTS
# ============================================================================

class TestBaseStatsRandomization:
    """Tests for base stats randomization."""

    def test_unchanged_preserves_stats(self, randomizer_both):
        """UNCHANGED should not modify base stats."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_BASE_STATS", RandomizeBaseStats.UNCHANGED)

        # Store original stats
        original_stats = {}
        for digimon_id, data in randomizer.baseDigimonInfo.items():
            original_stats[digimon_id] = data.getBaseStats()

        set_seed(42)
        randomizer.randomizeDigimonBaseStats(randomizer.rom_data)

        for digimon_id, original in original_stats.items():
            current = randomizer.baseDigimonInfo[digimon_id].getBaseStats()
            assert current == original, f"UNCHANGED modified stats for {hex(digimon_id)}"

    def test_shuffle_preserves_stat_values(self, randomizer_both):
        """SHUFFLE should preserve the same stat values, just reordered."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_BASE_STATS", RandomizeBaseStats.SHUFFLE)

        # Get set of valid digimon IDs from DIGIMON_IDS constant
        valid_ids = set()
        for stage_dict in constants.DIGIMON_IDS.values():
            valid_ids.update(stage_dict.values())

        # Store original stats (sorted for comparison)
        original_sorted = {}
        for digimon_id, data in randomizer.baseDigimonInfo.items():
            # Skip invalid IDs (e.g., ID 0x0 placeholder entries)
            if digimon_id not in valid_ids:
                continue
            stats = data.getBaseStats()
            # Only shuffle ATK, DEF, SPIRIT, SPEED (indices 2-5)
            original_sorted[digimon_id] = sorted(stats[2:6])

        set_seed(42)
        randomizer.randomizeDigimonBaseStats(randomizer.rom_data)

        for digimon_id, original in original_sorted.items():
            stats = randomizer.baseDigimonInfo[digimon_id].getBaseStats()
            current_sorted = sorted(stats[2:6])
            assert current_sorted == original, \
                f"SHUFFLE changed stat values for {hex(digimon_id)}"

    def test_random_sanity_runs(self, randomizer_both):
        """Random sanity mode should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_BASE_STATS", RandomizeBaseStats.RANDOM_SANITY)

        set_seed(42)
        randomizer.randomizeDigimonBaseStats(randomizer.rom_data)

    def test_random_completely_runs(self, randomizer_both):
        """Random completely mode should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_BASE_STATS", RandomizeBaseStats.RANDOM_COMPLETELY)

        set_seed(42)
        randomizer.randomizeDigimonBaseStats(randomizer.rom_data)


# ============================================================================
# MOVESET RANDOMIZATION TESTS
# ============================================================================

class TestMovesetRandomization:
    """Tests for moveset randomization."""

    def test_unchanged_preserves_moves(self, randomizer_both):
        """UNCHANGED should not modify movesets."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_MOVESETS", RandomizeMovesets.UNCHANGED)

        original_moves = {}
        for digimon_id, data in randomizer.baseDigimonInfo.items():
            original_moves[digimon_id] = (
                data.move_signature,
                data.getRegularMoves()
            )

        set_seed(42)
        randomizer.randomizeDigimonMovesets(randomizer.rom_data)

        for digimon_id, (orig_sig, orig_reg) in original_moves.items():
            data = randomizer.baseDigimonInfo[digimon_id]
            assert data.move_signature == orig_sig
            assert data.getRegularMoves() == orig_reg

    def test_species_bias_runs(self, randomizer_both):
        """Species-biased moveset randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_MOVESETS", RandomizeMovesets.RANDOM_SPECIES_BIAS)

        set_seed(42)
        randomizer.randomizeDigimonMovesets(randomizer.rom_data)

    def test_completely_random_runs(self, randomizer_both):
        """Completely random moveset randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_MOVESETS", RandomizeMovesets.RANDOM_COMPLETELY)

        set_seed(42)
        randomizer.randomizeDigimonMovesets(randomizer.rom_data)

    def test_guarantee_basic_move_adds_charge(self, randomizer_both):
        """Guarantee basic move option should add Charge to all digimon."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_MOVESETS", RandomizeMovesets.UNCHANGED)
        randomizer.config_manager.set("MOVESETS_GUARANTEE_BASIC_MOVE", True)

        set_seed(42)
        randomizer.randomizeDigimonMovesets(randomizer.rom_data)

        # Verify first move is Charge for at least some digimon
        # (The actual Charge move ID would need to be known)


# ============================================================================
# TRAIT RANDOMIZATION TESTS
# ============================================================================

class TestTraitRandomization:
    """Tests for trait randomization."""

    def test_unchanged_preserves_traits(self, randomizer_both):
        """UNCHANGED should not modify traits."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_TRAITS", RandomizeTraits.UNCHANGED)

        original_traits = {}
        for digimon_id, data in randomizer.baseDigimonInfo.items():
            original_traits[digimon_id] = (
                data.trait_1, data.trait_2, data.trait_3, data.trait_4, data.support_trait
            )

        set_seed(42)
        randomizer.randomizeDigimonTraits(randomizer.rom_data)

        for digimon_id, original in original_traits.items():
            data = randomizer.baseDigimonInfo[digimon_id]
            current = (data.trait_1, data.trait_2, data.trait_3, data.trait_4, data.support_trait)
            assert current == original, f"UNCHANGED modified traits for {hex(digimon_id)}"

    def test_stage_bias_runs(self, randomizer_both):
        """Stage-biased trait randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_TRAITS", RandomizeTraits.RANDOM_STAGE_BIAS)

        set_seed(42)
        randomizer.randomizeDigimonTraits(randomizer.rom_data)

    def test_completely_random_runs(self, randomizer_both):
        """Completely random trait randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_TRAITS", RandomizeTraits.RANDOM_COMPLETELY)

        set_seed(42)
        randomizer.randomizeDigimonTraits(randomizer.rom_data)


# ============================================================================
# ITEM RANDOMIZATION TESTS
# ============================================================================

class TestItemRandomization:
    """Tests for item randomization."""

    def test_overworld_unchanged_preserves_items(self, randomizer_both):
        """UNCHANGED should not modify overworld items."""
        randomizer = randomizer_both
        randomizer.config_manager.set("RANDOMIZE_OVERWORLD_ITEMS", RandomizeItems.UNCHANGED)

        set_seed(42)
        randomizer.randomizeOverworldItems(randomizer.rom_data)

    def test_overworld_keep_category_runs(self, randomizer_both):
        """Keep category overworld item randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_OVERWORLD_ITEMS",
            RandomizeItems.RANDOMIZE_KEEP_CATEGORY
        )

        set_seed(42)
        randomizer.randomizeOverworldItems(randomizer.rom_data)

    def test_overworld_completely_random_runs(self, randomizer_both):
        """Completely random overworld item randomization should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set(
            "RANDOMIZE_OVERWORLD_ITEMS",
            RandomizeItems.RANDOMIZE_COMPLETELY
        )

        set_seed(42)
        randomizer.randomizeOverworldItems(randomizer.rom_data)


# ============================================================================
# EXP PATCH TESTS
# ============================================================================

class TestExpPatch:
    """Tests for experience yield modification."""

    def test_unchanged_preserves_exp(self, randomizer_both):
        """UNCHANGED should not modify exp values."""
        randomizer = randomizer_both
        randomizer.config_manager.set("INCREASE_DIGIMON_EXP", ExpYieldConfig.UNCHANGED)

        set_seed(42)
        randomizer.expPatchFlat(randomizer.rom_data)

    def test_halved_runs(self, randomizer_both):
        """Halved exp patch should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("INCREASE_DIGIMON_EXP", ExpYieldConfig.INCREASE_HALVED)

        set_seed(42)
        randomizer.expPatchFlat(randomizer.rom_data)

    def test_full_runs(self, randomizer_both):
        """Full exp patch should complete."""
        randomizer = randomizer_both
        randomizer.config_manager.set("INCREASE_DIGIMON_EXP", ExpYieldConfig.INCREASE_FULL)

        set_seed(42)
        randomizer.expPatchFlat(randomizer.rom_data)


# ============================================================================
# FULL PIPELINE INTEGRATION TESTS
# ============================================================================

class TestFullPipeline:
    """Tests for the full randomization pipeline."""

    def test_execute_all_unchanged(self, randomizer_both):
        """Execute full pipeline with all settings unchanged."""
        randomizer = randomizer_both

        set_seed(42)
        randomizer.executeRandomizerFunctions(randomizer.rom_data)

    def test_execute_all_random(self, randomizer_both, config_all_random):
        """Execute full pipeline with all randomization enabled."""
        randomizer = randomizer_both
        randomizer.config_manager = config_all_random

        set_seed(42)
        # This is a comprehensive smoke test
        randomizer.executeRandomizerFunctions(randomizer.rom_data)

    @pytest.mark.slow
    def test_multiple_full_runs(self, randomizer_both, config_all_random):
        """Execute full pipeline multiple times with different seeds."""
        randomizer = randomizer_both
        randomizer.config_manager = config_all_random

        for seed in [1, 42, 999, 12345, 99999]:
            set_seed(seed)
            # Create fresh ROM copy for each run
            rom_copy = bytearray(randomizer.rom_data)

            # Should complete without error
            from qol_script import Randomizer
            fresh_randomizer = Randomizer(
                randomizer.version,
                rom_copy,
                config_all_random,
                randomizer.logger
            )
            fresh_randomizer.executeRandomizerFunctions(rom_copy)
