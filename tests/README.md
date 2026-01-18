# DWDD Randomizer Test Suite

This directory contains the test suite for the Digimon World Dusk/Dawn Randomizer.

## Test Structure

```
unittests/
├── conftest.py          # Shared fixtures and configuration
├── pytest.ini           # Pytest configuration
├── test_utils_unit.py   # Unit tests for pure utility functions
├── test_invariants.py   # Property-based invariant tests
├── test_qol.py          # QoL feature tests
├── test_randomization.py # Randomization integration tests
├── test_determinism.py  # Seed reproducibility tests
└── README.md            # This file
```

## Test Categories

### Unit Tests (`test_utils_unit.py`)
Tests for pure functions that have deterministic outputs:
- `getDigimonStage()` - ID to stage mapping
- `writeRomBytes()` - ROM byte writing
- Constants validation

### Invariant Tests (`test_invariants.py`)
Property-based tests that verify constraints hold regardless of random values:
- Stage preservation (same-stage randomization)
- Value conservation (resistance totals)
- Range constraints (valid IDs, positive stats)
- No-crash smoke tests

### QoL Tests (`test_qol.py`)
Tests for Quality of Life patches:
- ROM modification verification
- Idempotency (applying twice = applying once)
- Header preservation

### Randomization Tests (`test_randomization.py`)
Integration tests for randomization features:
- UNCHANGED preserves data
- Randomization modifies data
- All option combinations complete

### Determinism Tests (`test_determinism.py`)
Seed reproducibility tests:
- Same seed = same output
- Different seeds = different outputs
- Numpy random state consistency

## Running Tests

### Prerequisites
1. Pytest installed: `pip install pytest`
2. ROM files available (see Configuration)

### Basic Usage
```bash
# Run all tests
pytest

# Run specific test file
pytest test_utils_unit.py

# Run specific test class
pytest test_invariants.py::TestStagePreservationInvariants

# Run specific test
pytest test_determinism.py::TestDeterminism::test_same_seed_same_starters
```

### Filtering Tests
```bash
# Skip slow tests
pytest -m "not slow"

# Run only unit tests (no ROM required)
pytest test_utils_unit.py

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Configuration

### ROM Paths
ROM paths can be configured via environment variables:
```bash
export DWDD_ROM_DAWN="/path/to/dawn.nds"
export DWDD_ROM_DUSK="/path/to/dusk.nds"
```

Default paths are set in `conftest.py`.

### Test Settings
Default test settings disable all randomization. Tests override specific
settings as needed. See `DEFAULT_TEST_SETTINGS` in `conftest.py`.

## Writing New Tests

### Key Principles
1. **Don't test exact random outputs** - Use invariants instead
2. **Test properties that must always hold** - Regardless of seed
3. **Use parametrized fixtures** - `randomizer_both` runs on Dawn and Dusk
4. **Reset random state** - Use `set_seed()` for reproducibility

### Example: Testing a New Randomization Feature
```python
def test_my_feature_preserves_invariant(self, randomizer_both):
    """Test that my feature maintains some invariant."""
    randomizer = randomizer_both

    # Store original state
    original_value = get_something(randomizer)

    # Configure and run
    randomizer.config_manager.set("MY_FEATURE", MyFeatureConfig.ENABLED)
    set_seed(42)
    randomizer.myFeatureFunction(randomizer.rom_data)

    # Verify invariant holds
    new_value = get_something(randomizer)
    assert invariant_holds(original_value, new_value)
```

### Fixtures Available
- `rom_dawn`, `rom_dusk` - Single version ROM
- `rom_both` - Parametrized, runs on both versions
- `randomizer_dawn`, `randomizer_dusk` - Single version randomizer
- `randomizer_both` - Parametrized randomizer
- `config_unchanged` - All settings disabled
- `config_all_random` - All randomization enabled

## Markers

- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.requires_rom` - Needs ROM files
- `@pytest.mark.dawn_only` - Dawn-specific test
- `@pytest.mark.dusk_only` - Dusk-specific test
