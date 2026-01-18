"""
Determinism and reproducibility tests.

These tests verify that:
1. Same seed + same config = same output (determinism)
2. Different seeds produce different outputs (randomness)
3. Seed isolation works correctly between runs
"""

import pytest
import copy
import random
import numpy as np

from src import constants
from configs import (
    RandomizeStartersConfig,
    RandomizeWildEncounters,
    RandomizeBaseStats,
    RandomizeMovesets,
    RandomizeDigivolutions,
)
from unittests.conftest import set_seed, create_config_manager


# ============================================================================
# DETERMINISM TESTS
# ============================================================================

class TestDeterminism:
    """
    Tests that verify identical seeds produce identical results.
    This is crucial for reproducibility and sharing seeds between users.
    """

    def test_same_seed_same_starters(self, rom_dawn):
        """Same seed should produce identical starter randomization."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        # First run
        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(42)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeStarters(rom_copy1)

        # Second run with same seed
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(42)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeStarters(rom_copy2)

        # Compare starter pack region - use the STARTER_PACK_OFFSET constant
        starter_offset = constants.STARTER_PACK_OFFSET[rom_dawn.version]
        # Compare a region around the starter pack (0x200 bytes should cover it)
        region_size = 0x200
        val1 = rom_copy1[starter_offset:starter_offset+region_size]
        val2 = rom_copy2[starter_offset:starter_offset+region_size]
        assert val1 == val2, \
            f"Determinism failure in starter region starting at {hex(starter_offset)}"

    def test_same_seed_same_base_stats(self, rom_dawn):
        """Same seed should produce identical base stats randomization."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_BASE_STATS": RandomizeBaseStats.RANDOM_COMPLETELY
        })

        # First run
        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(12345)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeDigimonBaseStats(rom_copy1)
        stats1 = {did: d.getBaseStats() for did, d in randomizer1.baseDigimonInfo.items()}

        # Second run with same seed
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(12345)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeDigimonBaseStats(rom_copy2)
        stats2 = {did: d.getBaseStats() for did, d in randomizer2.baseDigimonInfo.items()}

        # Compare
        for digimon_id in stats1:
            assert stats1[digimon_id] == stats2[digimon_id], \
                f"Stats differ for {hex(digimon_id)}"

    def test_same_seed_same_movesets(self, rom_dawn):
        """Same seed should produce identical moveset randomization."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_MOVESETS": RandomizeMovesets.RANDOM_COMPLETELY
        })

        # First run
        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(999)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeDigimonMovesets(rom_copy1)
        moves1 = {
            did: (d.move_signature, d.getRegularMoves())
            for did, d in randomizer1.baseDigimonInfo.items()
        }

        # Second run with same seed
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(999)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeDigimonMovesets(rom_copy2)
        moves2 = {
            did: (d.move_signature, d.getRegularMoves())
            for did, d in randomizer2.baseDigimonInfo.items()
        }

        # Compare
        for digimon_id in moves1:
            assert moves1[digimon_id] == moves2[digimon_id], \
                f"Moves differ for {hex(digimon_id)}"

    def test_same_seed_full_pipeline_deterministic(self, rom_dawn, config_all_random):
        """Same seed should produce identical results for full randomization."""
        from qol_script import Randomizer

        # First run
        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(54321)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config_all_random, rom_dawn.logger)
        randomizer1.executeRandomizerFunctions(rom_copy1)

        # Second run with same seed
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(54321)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config_all_random, rom_dawn.logger)
        randomizer2.executeRandomizerFunctions(rom_copy2)

        # ROMs should be identical
        assert rom_copy1 == rom_copy2, "Full pipeline produced different results with same seed"


# ============================================================================
# RANDOMNESS TESTS
# ============================================================================

class TestRandomness:
    """
    Tests that verify different seeds produce different results.
    This ensures randomization is actually happening.
    """

    def test_different_seeds_different_starters(self, rom_dawn):
        """Different seeds should (usually) produce different starters."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        results = []
        starter_offset = constants.STARTER_PACK_OFFSET[rom_dawn.version]
        region_size = 0x200  # Compare a region around starter pack

        for seed in [1, 2, 3, 4, 5]:
            rom_copy = bytearray(rom_dawn.rom_data)
            set_seed(seed)
            randomizer = Randomizer(rom_dawn.version, rom_copy, config, rom_dawn.logger)
            randomizer.randomizeStarters(rom_copy)

            # Capture starter region
            values = bytes(rom_copy[starter_offset:starter_offset+region_size])
            results.append(values)

        # At least some should be different
        unique_results = set(results)
        assert len(unique_results) > 1, \
            "Different seeds produced identical results - randomization may not be working"

    def test_different_seeds_different_movesets(self, rom_dawn):
        """Different seeds should produce different movesets."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_MOVESETS": RandomizeMovesets.RANDOM_COMPLETELY
        })

        results = []
        sample_digimon = 0x61  # First rookie (Agumon typically)

        for seed in [10, 20, 30, 40, 50]:
            rom_copy = bytearray(rom_dawn.rom_data)
            set_seed(seed)
            randomizer = Randomizer(rom_dawn.version, rom_copy, config, rom_dawn.logger)
            randomizer.randomizeDigimonMovesets(rom_copy)

            if sample_digimon in randomizer.baseDigimonInfo:
                data = randomizer.baseDigimonInfo[sample_digimon]
                results.append((data.move_signature, tuple(data.getRegularMoves())))

        # Should have variety
        unique_results = set(results)
        assert len(unique_results) > 1, \
            "Different seeds produced identical movesets"


# ============================================================================
# SEED ISOLATION TESTS
# ============================================================================

class TestSeedIsolation:
    """
    Tests that verify seed state is properly isolated.
    """

    def test_seed_reset_produces_same_result(self, rom_dawn):
        """Resetting seed mid-execution should produce reproducible results."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        rom_copy = bytearray(rom_dawn.rom_data)
        starter_offset = constants.STARTER_PACK_OFFSET[rom_dawn.version]
        region_size = 0x200

        # Consume some random numbers
        set_seed(42)
        for _ in range(100):
            random.random()
            np.random.random()

        # Now reset and randomize
        set_seed(42)
        randomizer = Randomizer(rom_dawn.version, rom_copy, config, rom_dawn.logger)
        randomizer.randomizeStarters(rom_copy)

        # Capture result
        result1 = bytes(rom_copy[starter_offset:starter_offset+region_size])

        # Fresh ROM, same seed
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(42)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeStarters(rom_copy2)

        result2 = bytes(rom_copy2[starter_offset:starter_offset+region_size])

        assert result1 == result2, "Seed reset didn't produce reproducible results"

    def test_independent_randomizers_with_same_seed(self, rom_dawn, rom_dusk):
        """Two randomizers with same seed should produce comparable results."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        # Dawn with seed 42
        rom_copy_dawn = bytearray(rom_dawn.rom_data)
        set_seed(42)
        randomizer_dawn = Randomizer(
            rom_dawn.version, rom_copy_dawn, config, rom_dawn.logger
        )
        randomizer_dawn.randomizeStarters(rom_copy_dawn)

        # Dusk with seed 42
        rom_copy_dusk = bytearray(rom_dusk.rom_data)
        set_seed(42)
        randomizer_dusk = Randomizer(
            rom_dusk.version, rom_copy_dusk, config, rom_dusk.logger
        )
        randomizer_dusk.randomizeStarters(rom_copy_dusk)

        # Both should have run without error
        # (Actual comparison would need version-aware logic)


# ============================================================================
# NUMPY RANDOM STATE TESTS
# ============================================================================

class TestNumpyRandomState:
    """
    Tests that numpy's random state is properly managed alongside Python's random.
    Some randomization uses np.random for probability distributions.
    """

    def test_numpy_seed_consistency(self, rom_dawn):
        """Numpy random should be seeded consistently with Python random."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.RANDOMIZE
        })

        # First run - digivolutions use np.random.choice
        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(777)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeDigivolutions(rom_copy1)

        # Second run
        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(777)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeDigivolutions(rom_copy2)

        # Results should be identical
        # Compare a sample of digivolution addresses
        sample_digimon_id = 0x61
        addr1 = constants.DIGIVOLUTION_ADDRESSES[rom_dawn.version].get(sample_digimon_id)
        if addr1:
            region1 = bytes(rom_copy1[addr1:addr1+0x70])
            region2 = bytes(rom_copy2[addr1:addr1+0x70])
            assert region1 == region2, "Numpy random state not deterministic"


# ============================================================================
# EDGE CASE DETERMINISM TESTS
# ============================================================================

class TestEdgeCaseDeterminism:
    """
    Tests for determinism in edge cases.
    """

    def test_seed_zero_is_valid(self, rom_dawn):
        """Seed value of 0 should work correctly."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        starter_offset = constants.STARTER_PACK_OFFSET[rom_dawn.version]
        region_size = 0x200

        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(0)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeStarters(rom_copy1)

        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(0)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeStarters(rom_copy2)

        # Should be deterministic even with seed 0
        result1 = rom_copy1[starter_offset:starter_offset+region_size]
        result2 = rom_copy2[starter_offset:starter_offset+region_size]
        assert result1 == result2, "Seed 0 did not produce deterministic results"

    def test_large_seed_is_valid(self, rom_dawn):
        """Large seed values should work correctly."""
        from qol_script import Randomizer

        config = create_config_manager({
            "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_FULL
        })

        large_seed = 2**31 - 1  # Max 32-bit signed int
        starter_offset = constants.STARTER_PACK_OFFSET[rom_dawn.version]
        region_size = 0x200

        rom_copy1 = bytearray(rom_dawn.rom_data)
        set_seed(large_seed)
        randomizer1 = Randomizer(rom_dawn.version, rom_copy1, config, rom_dawn.logger)
        randomizer1.randomizeStarters(rom_copy1)

        rom_copy2 = bytearray(rom_dawn.rom_data)
        set_seed(large_seed)
        randomizer2 = Randomizer(rom_dawn.version, rom_copy2, config, rom_dawn.logger)
        randomizer2.randomizeStarters(rom_copy2)

        result1 = rom_copy1[starter_offset:starter_offset+region_size]
        result2 = rom_copy2[starter_offset:starter_offset+region_size]
        assert result1 == result2, "Large seed did not produce deterministic results"
