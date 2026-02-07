import argparse
import random
import sys
from pathlib import Path
import logging

import numpy as np
import toml

from configs import ConfigManager, APP_VERSION
from qol_script import DigimonROM, Randomizer

def main():

    parser = argparse.ArgumentParser(
        description="Digimon World Dawn/Dusk Randomizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python run_randomizer.py --rom ./DigimonWorldDusk.nds --config ./configs/balanced_randomization.toml --output ./DigimonWorldDusk_Randomized.nds"
    )

    parser.add_argument(
        "--rom",
        required=True,
        type=Path,
        help="Path to the input ROM file (.nds)"
    )

    parser.add_argument(
        '--config',
        required=True,
        type=Path,
        help="Path to randomization config file (.toml)"
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path for the output randomized ROM (.nds)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show output from Randomizer module in the console"
    )
    args = parser.parse_args()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    internal_logger = logging.getLogger("dwdd_internal")
    internal_logger.setLevel(logging.INFO)
    if args.verbose:
        internal_logger.addHandler(console_handler)

    if not args.rom.exists():
        logger.error(f"Error: ROM file not found: {args.rom}")
        sys.exit(1)
    
    if not args.config.exists():
        logger.error(f"Error: Randomization config file not found: {args.config}")
        sys.exit(1)
    
    if args.rom.suffix.lower() != ".nds":
        logger.error(f"Error: ROM file must be a .nds file")
        sys.exit(1)
    
    if args.config.suffix.lower() != '.toml':
        logger.error(f"Error: Config file must be a .toml file")
        sys.exit(1)
    
    try:
        logger.info(f"Loading ROM: {args.rom}")
        logger.info(f"Loading config: {args.config}")
        
        config_manager = ConfigManager()
        seed = -1
    
        input_rom = DigimonROM(str(args.rom), config_manager, internal_logger)
        randomizer = Randomizer(input_rom.version, input_rom.rom_data, config_manager, internal_logger)

        with open(str(args.config), 'r') as f:
            toml_data = toml.load(f)

        app_data = toml_data.get("app_data", None)
        if app_data:
            app_version = app_data.get("APP_VERSION", None)
            rom_version = app_data.get("ROM_VERSION", None)
            toml_seed = app_data.get("SEED", None)
            if(app_version and app_version != APP_VERSION):
                logger.warning(f"\nWarning: current app version {APP_VERSION} does not match config file's expected app version {app_version}.")
            if(rom_version and rom_version != input_rom.version):
                logger.warning(f"\nWarning: loaded rom ({input_rom.version}) does not match config file's expected rom ({rom_version}). Settings such as custom starters may have inadvertently been altered.")
            if(toml_seed):
                seed = toml_seed

        config_manager.update_from_toml(toml_data)

        # set seed
        if(seed == -1):
            seed = random.randrange(2**32-1)
            
        random.seed(seed)
        np.random.seed(seed)

        log_path = str(args.output) + ".log"
        file_handler = logging.FileHandler(log_path, mode='w', encoding='utf8')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        internal_logger.addHandler(file_handler)

        input_rom.executeQolChanges()
        randomizer.executeRandomizerFunctions(input_rom.rom_data)
        input_rom.writeRom(str(args.output))

        
        logger.info(f"Randomized ROM saved to: {args.output}")
        logger.info(f"Randomization log saved to: {args.output}.log")
        
    except Exception as e:
        logger.error(f"Error during randomization: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()