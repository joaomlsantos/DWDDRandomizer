
TEXT_SPEED_OFFSET = {
    "DUSK": 0x40328,
    "DAWN": 0x40314
}

MOVEMENT_SPEED_OFFSET = {
    "DUSK": 0x66AC4,
    "DAWN": 0x66A54
}

# these are (offset_start, offset_end); offset_end corresponds to the last area, content that follows it should still be analyzed
AREA_ENCOUNTER_OFFSETS = {
    "DUSK": (0x01F6D800, 0x01F76A00),
    "DAWN": (0X01F6D600, 0x01F76800)
}

STAT_CAPS_OFFSET = {
    "DUSK": 0x00059B30,
    "DAWN": 0x00059B14
}

STARTER_PACK_OFFSET = {
    "DUSK": 0x0027FF90,
    "DAWN": 0x0027FDEC
}

BASE_DIGIMON_OFFSETS = {
    "DUSK": (0x01F55200, 0x01F6D600),
    "DAWN": (0x01F55000, 0x01F6D400)
}

ENEMY_DIGIMON_OFFSETS = {
    "DUSK": (0x01F78800, 0x01F90C00),
    "DAWN": (0X01F78600, 0x01F90A00)
}

LVLUP_TYPE_TABLE_OFFSET = {
    "DUSK": 0x00122458,
    "DAWN": 0x00122298
}

SPRITE_MAPPING_TABLE_OFFSET = {
    "DUSK": (0x000FCE04, 0x00100834),
    "DAWN": (0x000FCD08, 0x00100738)
}

STRING_BATTLE_TABLE_OFFSET = {
    "DUSK": (0x00116A94, 0x00117920),
    "DAWN": (0X00116998, 0x00117824)
}


STAGE_NAMES = ["IN-TRAINING", "ROOKIE", "CHAMPION", "ULTIMATE", "MEGA"]

DIGIMON_IDS = {
    "IN-TRAINING":
    {
        "Chicchimon": 0x41,
        "Koromon": 0x42,
        "Tsunomon": 0x43,
        "Poyomon": 0x44,
        "Tokomon": 0x45,
        "Tanemon": 0x46,
        "Pagumon": 0x47,
        "Kapurimon": 0x48,
        "Kuramon": 0x49,
        "Puttimon": 0x4A,
        "Chibomon": 0x4B,
        "Dorimon": 0x4C,
        "Calumon": 0x4D,
        "Gigimon": 0x4E,
        "Gummymon": 0x4F,
        "Kokomon": 0x50,
        "Tsumemon": 0x51,
        "Minomon": 0x52,
        "Wanyamon": 0x53,
        "Budmon": 0x54,
        "Botamon": 0x55,
        "Sunmon": 0x56,
        "Moonmon": 0x57
    },
    "ROOKIE":
    {
        "Monodramon": 0x61,
        "Agumon": 0x62,
        "Veemon": 0x63,
        "Guilmon": 0x64,
        "Dorumon": 0x65,
        "Betamon": 0x66,
        "Gabumon": 0x67,
        "Patamon": 0x68,
        "Biyomon": 0x69,
        "Palmon": 0x6A,
        "Tentomon": 0x6B,
        "Gotsumon": 0x6C,
        "Otamamon": 0x6D,
        "Gomamon": 0x6E,
        "Tapirmon": 0x6F,
        "DemiDevimon": 0x70,
        "ToyAgumon": 0x71,
        "Hagurumon": 0x72,
        "Salamon": 0x73,
        "Wormmon": 0x74,
        "Hawkmon": 0x75,
        "Armadillomon": 0x76,
        "Terriermon": 0x77,
        "Lopmon": 0x78,
        "Renamon": 0x79,
        "Impmon": 0x7A,
        "Keramon": 0x7B,
        "Falcomon": 0x7C,
        "Penguinmon": 0x7D,
        "Goburimon": 0x7E,
        "Kumamon": 0x7F,
        "Kotemon": 0x80,
        "Shamamon": 0x81,
        "Snow Goblimon": 0x82,
        "Syakomon": 0x83,
        "SnowAgumon": 0x84,
        "BlackAgumon": 0x85,
        "Muchomon": 0x86,
        "Crabmon": 0x87,
        "Floramon": 0x88,
        "Gizamon": 0x89,
        "Lalamon": 0x8A,
        "Aruraumon": 0x8B,
        "ToyAgumon(Black)": 0x8C,
        "Tsukaimon": 0x8D,
        "PawnChessmon(Black)": 0x8E,
        "Gaomon": 0x8F,
        "Dfalcomon": 0x90,
        "Kudamon": 0x91,
        "Kamemon": 0x92,
        "Dracmon": 0x93,
        "PawnChessmon(White)": 0x94,
        "DotAgumon": 0x95,
        "Kunemon": 0x96,
        "Mushroomon": 0x97,
        "Solarmon": 0x98,
        "Candlemon": 0x99,
        "Kokuwamon": 0x9A,
        "DoKunemon": 0x9B,
        "Coronamon": 0x9C,
        "Lunamon": 0x9D
    },
    "CHAMPION":
    {
        "Mekanorimon": 0xA8,
        "Greymon": 0xA9,
        "Tyrannomon": 0xAA,
        "Devimon": 0xAB,
        "Airdramon": 0xAC,
        "Seadramon": 0xAD,
        "Numemon": 0xAE,
        "Kabuterimon": 0xAF,
        "Garurumon": 0xB0,
        "Angemon": 0xB1,
        "Veggiemon": 0xB2,
        "Ogremon": 0xB3,
        "Bakemon": 0xB4,
        "Sukamon": 0xB5,
        "Kokatorimon": 0xB6,
        "Leomon": 0xB7,
        "Kuwagamon": 0xB8,
        "Raremon": 0xB9,
        "Gekomon": 0xBB,
        "Gatomon": 0xBC,
        "Wizardmon": 0xBD,
        "Togemon": 0xBE,
        "Guardromon": 0xBF,
        "ExVeemon": 0xC0,
        "Stingmon": 0xC1,
        "Birdramon": 0xC2,
        "Ankylomon": 0xC3,
        "Gargomon": 0xC4,
        "Growlmon": 0xC5,
        "Kyubimon": 0xC6,
        "Kurisarimon": 0xC7,
        "Seasarmon": 0xC8,
        "Vilemon": 0xC9,
        "Aquilamon": 0xCA,
        "Roachmon": 0xCB,
        "Dinohumon": 0xCC,
        "Hookmon": 0xCD,
        "Grizzmon": 0xCE,
        "Dorugamon": 0xCF,
        "Reptiledramon": 0xD0,
        "Apemon": 0xD1,
        "Starmon": 0xD2,
        "BomberNanimon": 0xD3,
        "Kiwimon": 0xD4,
        "Unimon": 0xD5,
        "Sorcerymon": 0xD6,
        "DKTyrannomon": 0xD7,
        "Akatorimon": 0xD8,
        "PlatinumSukamon": 0xD9,
        "Ikkakumon": 0xDA,
        "Minotarumon": 0xDB,
        "Icemon": 0xDC,
        "DarkLizardmon": 0xDD,
        "Flarerizamon": 0xDE,
        "GeoGreymon": 0xDF,
        "Gaogamon": 0xE0,
        "Diatrymon": 0xE1,
        "Reppamon": 0xE2,
        "Sunflowmon": 0xE3,
        "Gawappamon": 0xE4,
        "Sangloupmon": 0xE5,
        "Peckmon": 0xE6,
        "Drimogemon": 0xE7,
        "NiseDrimogemon": 0xE8,
        "MoriShellmon": 0xE9,
        "Wendigomon": 0xEA,
        "Fugamon": 0xEB,
        "Tsuchidarumon": 0xEC,
        "Tortamon": 0xED,
        "Ebidramon": 0xEE,
        "Octomon": 0xEF,
        "Gesomon": 0xF0,
        "Coelamon": 0xF1,
        "Shellmon": 0xF2,
        "Frigimon": 0xF3,
        "Geremon": 0xF4,
        "Hyogamon": 0xF5,
        "KaratsukiNumemon": 0xF6,
        "IceDevimon": 0xF7,
        "Dolphmon": 0xF8,
        "Saberdramon": 0xF9,
        "Woodmon": 0xFA,
        "Snimon": 0xFB,
        "Flymon": 0xFC,
        "Yanmamon": 0xFD,
        "Sand Yanmamon": 0xFE,
        "Red Vegiemon": 0xFF,
        "Weedmon": 0x100,
        "Ninjamon": 0x101,
        "Kogamon": 0x102,
        "Omekamon": 0x103,
        "Clockmon": 0x104,
        "Thunderballmon": 0x105,
        "Tankmon": 0x106,
        "Nanimon": 0x107,
        "Golemon": 0x108,
        "Monochromon": 0x109,
        "Mojyamon": 0x10A,
        "Jungle Mojyamon": 0x10B,
        "Deputymon": 0x10C,
        "Centarumon": 0x10D,
        "Devidramon": 0x10E,
        "Dokugumon": 0x10F,
        "Veedramon": 0x110,
        "Musyamon": 0x111,
        "KnightChessmon(White)": 0x112,
        "KnightChessmon(Black)": 0x113,
        "Firamon": 0x114,
        "Lekismon": 0x115
    },
    "ULTIMATE":
    {
        "Volcanomon": 0x120,
        "MetalGreymon": 0x121,
        "Monzaemon": 0x122,
        "SkullGreymon": 0x123,
        "MetalMamemon": 0x124,
        "Andromon": 0x125,
        "Etemon": 0x126,
        "Megadramon": 0x127,
        "Piximon": 0x128,
        "Digitamamon": 0x129,
        "Mammothmon": 0x12A,
        "Megakabuterimon(Blue)": 0x12B,
        "Okuwamon": 0x12C,
        "ShogunGekomon": 0x12D,
        "Angewomon": 0x12E,
        "Tylomon": 0x12F,
        "Scorpiomon": 0x130,
        "MegaSeadramon": 0x131,
        "Dragomon": 0x132,
        "WarGarurumon(Black)": 0x133,
        "WarGarurumon(Blue)": 0x134,
        "Myotismon": 0x135,
        "LadyDevimon": 0x136,
        "Garudamon": 0x137,
        "Blossomon": 0x138,
        "Lillymon": 0x139,
        "MegaKabuterimon(Red)": 0x13A,
        "Datamon": 0x13B,
        "Cyberdramon": 0x13C,
        "MagnaAngemon": 0x13D,
        "Paildramon": 0x13E,
        "Dinobeemon": 0x13F,
        "Antylamon": 0x140,
        "Arukenimon": 0x141,
        "Mummymon": 0x142,
        "WarGrowlmon": 0x143,
        "Rapidmon": 0x144,
        "Taomon": 0x145,
        "Parrotmon": 0x146,
        "Infermon": 0x147,
        "BlackRapidmon": 0x148,
        "Pandamon": 0x149,
        "Marine Devimon": 0x14A,
        "Karatenmon": 0x14B,
        "Kyukimon": 0x14C,
        "Sinduramon": 0x14D,
        "Pipismon": 0x14E,
        "DoruGreymon": 0x14F,
        "Divermon": 0x150,
        "Kimeramon": 0x151,
        "Triceramon": 0x152,
        "Deramon": 0x153,
        "Silphymon": 0x154,
        "SuperStarmon": 0x155,
        "BlackWarGrowlmon ": 0x156,
        "Zudomon": 0x157,
        "Whamon (Ultimate)": 0x158,
        "Mamemon": 0x159,
        "Toucanmon": 0x15A,
        "Aurumon": 0x15B,
        "Meteormon": 0x15C,
        "Gigadramon": 0x15D,
        "RiseGreymon": 0x15E,
        "MachGaogamon": 0x15F,
        "Yatakaramon": 0x160,
        "Tyilinmon": 0x161,
        "Lilamon": 0x162,
        "Shadramon": 0x163,
        "Matadormon": 0x164,
        "Kabukimon": 0x165,
        "Cherrymon": 0x166,
        "Garbagemon": 0x167,
        "Lucemon Chaos Mode": 0x168,
        "MameTyramon": 0x169,
        "Giromon": 0x16A,
        "Vademon": 0x16B,
        "MetalTyrannomon": 0x16C,
        "Tekkamon": 0x16D,
        "Big Mamemon": 0x16E,
        "EXTyrannomon": 0x16F,
        "Vermilimon": 0x170,
        "Phantomon": 0x171,
        "Vajramon": 0x172,
        "AeroVeedramon": 0x173,
        "Grapleomon": 0x174,
        "Knightmon": 0x175,
        "Brachiomon": 0x176,
        "Allomon": 0x177,
        "Lanksmon": 0x178,
        "Shaujinmon": 0x179,
        "Yatagaramon": 0x17A,
        "BishopChessmon": 0x17B,
        "RookChessmon": 0x17C,
        "Flaremon": 0x17D,
        "Crescemon": 0x17E,
        "Flamedramon": 0x17F,
        "Magnamon": 0x180,
        "Prairiemon": 0x181,
        "Kongoumon": 0x182,
        "Seahomon": 0x183,
        "Shurimon": 0x184,
        "Kenkimon": 0x185,
        "Ponchomon": 0x186,
        "Argomon Ultimate": 0x187,
        "Shakkoumon": 0x188
    },
    "MEGA":
    {
        "Lampmon": 0x191,
        "HerculesKabuterimon": 0x192,
        "SaberLeomon": 0x193,
        "MetalEtemon": 0x194,
        "MarineAngemon": 0x195,
        "GigaSeadramon": 0x196,
        "Piedmon": 0x197,
        "Creepymon": 0x198,
        "Phoenixmon": 0x199,
        "Puppetmon": 0x19A,
        "Rosemon": 0x19B,
        "WarGreymon": 0x19C,
        "MetalGarurumon": 0x19D,
        "MachineDramon": 0x19E,
        "VenomMyotismon": 0x19F,
        "Omnimon": 0x1A0,
        "Imperialdramon Dragon Mode": 0x1A1,
        "Imperialdramon Fighter Mode": 0x1A2,
        "Imperialdramon Paladin Mode": 0x1A3,
        "Ghoulmon": 0x1A4,
        "Seraphimon": 0x1A5,
        "HiAndromon": 0x1A6,
        "Devitamamon": 0x1A7,
        "Cherubimon (Good)": 0x1A8,
        "Cherubimon (Evil)": 0x1A9,
        "Gallantmon": 0x1AA,
        "Gallantmon Crimson Mode": 0x1AB,
        "Mega Gargomon": 0x1AC,
        "Sakuyamon": 0x1AD,
        "Diaboromon": 0x1AE,
        "Neptunmon": 0x1AF,
        "Pukumon": 0x1B0,
        "Gryphonmon ": 0x1B1,
        "Preciomon": 0x1B2,
        "Armageddemon": 0x1B3,
        "MaloMyotismon": 0x1B4,
        "Imperialdramon Dragon Mode(Black)": 0x1B5,
        "Boltmon": 0x1B6,
        "PrinceMamemon": 0x1B7,
        "Ophanimon": 0x1B8,
        "Zanbamon": 0x1B9,
        "Black SaintGargomon": 0x1BA,
        "Jijimon": 0x1BB,
        "Babamon": 0x1BC,
        "Anubismon": 0x1BD,
        "Parasimon": 0x1BE,
        "Cannondramon": 0x1BF,
        "SL Angemon": 0x1C0,
        "Eaglemon": 0x1C1,
        "Dorugoramon": 0x1C2,
        "Beelzemon": 0x1C3,
        "Bantyo Leomon": 0x1C4,
        "Dark Dramon": 0x1C5,
        "Apocalymon": 0x1C6,
        "Ebemon": 0x1C7,
        "Gulfmon ": 0x1C8,
        "Goldramon": 0x1C9,
        "ZeedMillenniummon": 0x1CA,
        "Ghoulmon (Black)": 0x1CB,
        "Kuzuhamon": 0x1CC,
        "Chaos Gallantmon": 0x1CD,
        "MetalSeadramon": 0x1CE,
        "Valkyrimon": 0x1CF,
        "Justimon": 0x1D0,
        "Vikemon": 0x1D1,
        "BlackWarGreymon": 0x1D2,
        "Skull Mammothmon": 0x1D3,
        "GrandisKuwagamon": 0x1D4,
        "Pharaohmon": 0x1D5,
        "Susanoomon": 0x1D6,
        "Alphamon": 0x1D7,
        "Magna Dramon": 0x1D8,
        "Millenniummon  ": 0x1D9,
        "Moon=Millenniummon  ": 0x1DA,
        "Megidramon": 0x1DB,
        "Sleipmon": 0x1DC,
        "ShineGreymon": 0x1DD,
        "MirageGaogamon": 0x1DE,
        "JumboGamemon": 0x1DF,
        "Ravemon": 0x1E0,
        "QueenChessmon": 0x1E1,
        "KingChessmon": 0x1E2,
        "Chronomon Holy Mode": 0x1E3,
        "Lilithmon": 0x1E4,
        "Varodurumon": 0x1E5,
        "Apollomon": 0x1E6,
        "Dianamon": 0x1E7,
        "Shine Greymon Burst Mode": 0x1E8,
        "Shine Greymon Ruin Mode": 0x1E9,
        "MirageGaogamon Burst Mode": 0x1EA,
        "Ravemon Burst Mode": 0x1EB,
        "Lotosmon": 0x1EC,
        "DotShineGreymon": 0x1ED,
        "DotMirageGaogamon": 0x1EE,
        "Beelzemon Blast Mode": 0x1EF,
        "Rosemon Burst Mode": 0x1F0,
        "Argomon Mega": 0x1F1,
        "Minervamon": 0x1F2,
        "Duftmon": 0x1F3,
        "Chaosmon": 0x1F4
    }
}

DIGIVOLUTION_CONDITIONS = {
    0x0: "NONE",
    0x1: "LEVEL",
    0x2: "DRAGON EXP",
    0x3: "BEAST EXP",
    0x4: "AQUAN EXP",
    0x5: "BIRD EXP",
    0x6: "INSECTPLANT EXP",
    0x7: "MACHINE EXP",
    0x8: "DARK EXP",
    0x9: "HOLY EXP",
    0xA: "SPECIES EXP",
    0xB: "ATK STAT",
    0xC: "DEF STAT",
    0xD: "SPEED STAT",
    0xE: "SPIRIT STAT",
    0xF: "APTITUDE STAT",
    #0x10: "STRESS % STAT",             # unused
    #0x11: "STRESS % STAT [2]",         # unused
    0x12: "FRIENDSHIP % STAT",
    #0x13: "FRIENDSHIP % STAT [2]",     # unused
    #0x14: "ITEM IN INVENTORY",         # unused, this doesn't seem to be implemented correctly
    0x15: "DIGIMON ID IN PARTY",
    0x16: "BEFRIENDED DIGIMON ID"
}

# stage -> min, max
# do not set 0x15 or 0x16 for now
DIGIVOLUTION_CONDITIONS_VALUES = {
    0x0: [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
    0x1: [[1, 5], [7, 16], [17, 30], [32, 45], [46, 65]],
    0x2: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x3: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x4: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x5: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x6: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x7: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x8: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0x9: [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
    0xA: [[0, 0], [300, 1500], [1000, 3000], [4500, 20000], [15000, 90000]],
    0xB: [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
    0xC: [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
    0xD: [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
    0xE: [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
    0xF: [[0, 0], [15, 25], [25, 40], [40, 50], [50, 65]],
    0x12: [[0, 0], [50, 70], [60, 70], [70, 80], [90, 100]],
    0x15: [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
    0x16: [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
}


# probability array [a, b, c] where a -> 1 condition, b -> 2 conditions, c -> 3 conditions
# a is always the level
DIGIVOLUTION_CONDITION_AMOUNT_DISTRIBUTION = {
    "IN-TRAINING": [1, 0, 0],
    "ROOKIE": [0.3, 0.6, 0.1],
    "CHAMPION": [0.05, 0.4, 0.55],
    "ULTIMATE": [0.01, 0.19, 0.8],
    "MEGA": [0, 0.05, 0.95]
}

# probability array [a, b, c, d] where a -> 0 evos, b -> 1 evo, c -> 2 evos, d -> 3 evos
DIGIVOLUTION_AMOUNT_DISTRIBUTION = {
    "IN-TRAINING": [0, 0.2, 0.4, 0.4],
    "ROOKIE": [0, 0.25, 0.55, 0.2],
    "CHAMPION": [0.25 , 0.4, 0.3, 0.05],
    "ULTIMATE": [0.3, 0.5, 0.18, 0.02],
    "MEGA": [1, 0, 0, 0]
}

DIGIVOLUTION_ADDRESSES = {
    "DUSK":
    {
        0x40: 0x327c020,
        0x41: 0x327c090,
        0x42: 0x327c100,
        0x43: 0x327c170,
        0x44: 0x327c1e0,
        0x45: 0x327c250,
        0x46: 0x327c2c0,
        0x47: 0x327c330,
        0x48: 0x327c420,
        0x49: 0x327c490,
        0x4a: 0x327c500,
        0x4b: 0x327c570,
        0x4c: 0x327c5e0,
        0x4d: 0x327c650,
        0x4e: 0x327c6c0,
        0x4f: 0x327c730,
        0x50: 0x326d420,
        0x51: 0x326d490,
        0x52: 0x326d500,
        0x53: 0x326d570,
        0x54: 0x326d5e0,
        0x55: 0x326d650,
        0x56: 0x326d6c0,
        0x57: 0x326d730,
        0x58: 0x326d820,
        0x59: 0x326d890,
        0x5a: 0x326d900,
        0x5b: 0x326d970,
        0x5c: 0x326d9e0,
        0x5d: 0x326da50,
        0x5e: 0x326dac0,
        0x5f: 0x326db30,
        0x60: 0x326dc20,
        0x61: 0x326dc90,
        0x62: 0x326dd00,
        0x63: 0x326dd70,
        0x64: 0x326dde0,
        0x65: 0x326de50,
        0x66: 0x326dec0,
        0x67: 0x326df30,
        0x68: 0x326e020,
        0x69: 0x326e090,
        0x6a: 0x326e100,
        0x6b: 0x326e170,
        0x6c: 0x326e1e0,
        0x6d: 0x326e250,
        0x6e: 0x326e2c0,
        0x6f: 0x326e330,
        0x70: 0x326e420,
        0x71: 0x326e490,
        0x72: 0x326e500,
        0x73: 0x326e570,
        0x74: 0x326e5e0,
        0x75: 0x326e650,
        0x76: 0x326e6c0,
        0x77: 0x326e730,
        0x78: 0x326e820,
        0x79: 0x326e890,
        0x7a: 0x326e900,
        0x7b: 0x326e970,
        0x7c: 0x326e9e0,
        0x7d: 0x326ea50,
        0x7e: 0x326eac0,
        0x7f: 0x326eb30,
        0x80: 0x326ec20,
        0x81: 0x326ec90,
        0x82: 0x326ed00,
        0x83: 0x326ed70,
        0x84: 0x326ede0,
        0x85: 0x326ee50,
        0x86: 0x326eec0,
        0x87: 0x326ef30,
        0x88: 0x326f020,
        0x89: 0x326f090,
        0x8a: 0x326f100,
        0x8b: 0x326f170,
        0x8c: 0x326f1e0,
        0x8d: 0x326f250,
        0x8e: 0x326f2c0,
        0x8f: 0x326f330,
        0x90: 0x326f420,
        0x91: 0x326f490,
        0x92: 0x326f500,
        0x93: 0x326f570,
        0x94: 0x326f5e0,
        0x95: 0x326f650,
        0x96: 0x326f6c0,
        0x97: 0x326f730,
        0x98: 0x326f820,
        0x99: 0x326f890,
        0x9a: 0x326f900,
        0x9b: 0x326f970,
        0x9c: 0x326f9e0,
        0x9d: 0x326fa50,
        0x9e: 0x326fac0,
        0x9f: 0x326fb30,
        0xa8: 0x3270420,
        0xa9: 0x3270490,
        0xaa: 0x3270500,
        0xab: 0x3270570,
        0xac: 0x32705e0,
        0xad: 0x3270650,
        0xae: 0x32706c0,
        0xaf: 0x3270730,
        0xb0: 0x3270820,
        0xb1: 0x3270890,
        0xb2: 0x3270900,
        0xb3: 0x3270970,
        0xb4: 0x32709e0,
        0xb5: 0x3270a50,
        0xb6: 0x3270ac0,
        0xb7: 0x3270b30,
        0xb8: 0x3270c20,
        0xb9: 0x3270c90,
        0xba: 0x3270d00,
        0xbb: 0x3270d70,
        0xbc: 0x3270de0,
        0xbd: 0x3270e50,
        0xbe: 0x3270ec0,
        0xbf: 0x3270f30,
        0xc0: 0x3271020,
        0xc1: 0x3271090,
        0xc2: 0x3271100,
        0xc3: 0x3271170,
        0xc4: 0x32711e0,
        0xc5: 0x3271250,
        0xc6: 0x32712c0,
        0xc7: 0x3271330,
        0xc8: 0x3271420,
        0xc9: 0x3271490,
        0xca: 0x3271500,
        0xcb: 0x3271570,
        0xcc: 0x32715e0,
        0xcd: 0x3271650,
        0xce: 0x32716c0,
        0xcf: 0x3271730,
        0xd0: 0x3271820,
        0xd1: 0x3271890,
        0xd2: 0x3271900,
        0xd3: 0x3271970,
        0xd4: 0x32719e0,
        0xd5: 0x3271a50,
        0xd6: 0x3271ac0,
        0xd7: 0x3271b30,
        0xd8: 0x3271c20,
        0xd9: 0x3271c90,
        0xda: 0x3271d00,
        0xdb: 0x3271d70,
        0xdc: 0x3271de0,
        0xdd: 0x3271e50,
        0xde: 0x3271ec0,
        0xdf: 0x3271f30,
        0xe0: 0x3272020,
        0xe1: 0x3272090,
        0xe2: 0x3272100,
        0xe3: 0x3272170,
        0xe4: 0x32721e0,
        0xe5: 0x3272250,
        0xe6: 0x32722c0,
        0xe7: 0x3272330,
        0xe8: 0x3272420,
        0xe9: 0x3272490,
        0xea: 0x3272500,
        0xeb: 0x3272570,
        0xec: 0x32725e0,
        0xed: 0x3272650,
        0xee: 0x32726c0,
        0xef: 0x3272730,
        0xf0: 0x3272c20,
        0xf1: 0x3272c90,
        0xf2: 0x3272d00,
        0xf3: 0x3272d70,
        0xf4: 0x3272de0,
        0xf5: 0x3272e50,
        0xf6: 0x3272ec0,
        0xf7: 0x3272f30,
        0xf8: 0x3273020,
        0xf9: 0x3273090,
        0xfa: 0x3273100,
        0xfb: 0x3273170,
        0xfc: 0x32731e0,
        0xfd: 0x3273250,
        0xfe: 0x32732c0,
        0xff: 0x3273330,
        0x100: 0x3273420,
        0x101: 0x3273490,
        0x102: 0x3273500,
        0x103: 0x3273570,
        0x104: 0x32735e0,
        0x105: 0x3273650,
        0x106: 0x32736c0,
        0x107: 0x3273730,
        0x108: 0x3273820,
        0x109: 0x3273890,
        0x10a: 0x3273900,
        0x10b: 0x3273970,
        0x10c: 0x32739e0,
        0x10d: 0x3273a50,
        0x10e: 0x3273ac0,
        0x10f: 0x3273b30,
        0x110: 0x3273c20,
        0x111: 0x3273c90,
        0x112: 0x3273d00,
        0x113: 0x3273d70,
        0x114: 0x3273de0,
        0x115: 0x3273e50,
        0x116: 0x3273ec0,
        0x117: 0x3273f30,
        0x118: 0x3274020,
        0x119: 0x3274090,
        0x11a: 0x3274100,
        0x11b: 0x3274170,
        0x11c: 0x32741e0,
        0x11d: 0x3274250,
        0x11e: 0x32742c0,
        0x11f: 0x3274330,
        0x120: 0x3274420,
        0x121: 0x3274490,
        0x122: 0x3274500,
        0x123: 0x3274570,
        0x124: 0x32745e0,
        0x125: 0x3274650,
        0x126: 0x32746c0,
        0x127: 0x3274730,
        0x128: 0x3274820,
        0x129: 0x3274890,
        0x12a: 0x3274900,
        0x12b: 0x3274970,
        0x12c: 0x32749e0,
        0x12d: 0x3274a50,
        0x12e: 0x3274ac0,
        0x12f: 0x3274b30,
        0x130: 0x3274c20,
        0x131: 0x3274c90,
        0x132: 0x3274d00,
        0x133: 0x3274d70,
        0x134: 0x3274de0,
        0x135: 0x3274e50,
        0x136: 0x3274ec0,
        0x137: 0x3274f30,
        0x138: 0x3275020,
        0x139: 0x3275090,
        0x13a: 0x3275100,
        0x13b: 0x3275170,
        0x13c: 0x32751e0,
        0x13d: 0x3275250,
        0x13e: 0x32752c0,
        0x13f: 0x3275330,
        0x140: 0x3275820,
        0x141: 0x3275890,
        0x142: 0x3275900,
        0x143: 0x3275970,
        0x144: 0x32759e0,
        0x145: 0x3275a50,
        0x146: 0x3275ac0,
        0x147: 0x3275b30,
        0x148: 0x3275c20,
        0x149: 0x3275c90,
        0x14a: 0x3275d00,
        0x14b: 0x3275d70,
        0x14c: 0x3275de0,
        0x14d: 0x3275e50,
        0x14e: 0x3275ec0,
        0x14f: 0x3275f30,
        0x150: 0x3276020,
        0x151: 0x3276090,
        0x152: 0x3276100,
        0x153: 0x3276170,
        0x154: 0x32761e0,
        0x155: 0x3276250,
        0x156: 0x32762c0,
        0x157: 0x3276330,
        0x158: 0x3276420,
        0x159: 0x3276490,
        0x15a: 0x3276500,
        0x15b: 0x3276570,
        0x15c: 0x32765e0,
        0x15d: 0x3276650,
        0x15e: 0x32766c0,
        0x15f: 0x3276730,
        0x160: 0x3276820,
        0x161: 0x3276890,
        0x162: 0x3276900,
        0x163: 0x3276970,
        0x164: 0x32769e0,
        0x165: 0x3276a50,
        0x166: 0x3276ac0,
        0x167: 0x3276b30,
        0x168: 0x3276c20,
        0x169: 0x3276c90,
        0x16a: 0x3276d00,
        0x16b: 0x3276d70,
        0x16c: 0x3276de0,
        0x16d: 0x3276e50,
        0x16e: 0x3276ec0,
        0x16f: 0x3276f30,
        0x170: 0x3277020,
        0x171: 0x3277090,
        0x172: 0x3277100,
        0x173: 0x3277170,
        0x174: 0x32771e0,
        0x175: 0x3277250,
        0x176: 0x32772c0,
        0x177: 0x3277330,
        0x178: 0x3277420,
        0x179: 0x3277490,
        0x17a: 0x3277500,
        0x17b: 0x3277570,
        0x17c: 0x32775e0,
        0x17d: 0x3277650,
        0x17e: 0x32776c0,
        0x17f: 0x3277730,
        0x180: 0x3277820,
        0x181: 0x3277890,
        0x182: 0x3277900,
        0x183: 0x3277970,
        0x184: 0x32779e0,
        0x185: 0x3277a50,
        0x186: 0x3277ac0,
        0x187: 0x3277b30,
        0x188: 0x3277c20,
        0x189: 0x3277c90,
        0x18a: 0x3277d00,
        0x18b: 0x3277d70,
        0x18c: 0x3277de0,
        0x18d: 0x3277e50,
        0x18e: 0x3277ec0,
        0x18f: 0x3277f30,
        0x190: 0x3278420,
        0x191: 0x3278490,
        0x192: 0x3278500,
        0x193: 0x3278570,
        0x194: 0x32785e0,
        0x195: 0x3278650,
        0x196: 0x32786c0,
        0x197: 0x3278730,
        0x198: 0x3278820,
        0x199: 0x3278890,
        0x19a: 0x3278900,
        0x19b: 0x3278970,
        0x19c: 0x32789e0,
        0x19d: 0x3278a50,
        0x19e: 0x3278ac0,
        0x19f: 0x3278b30,
        0x1a0: 0x3278c20,
        0x1a1: 0x3278c90,
        0x1a2: 0x3278d00,
        0x1a3: 0x3278d70,
        0x1a4: 0x3278de0,
        0x1a5: 0x3278e50,
        0x1a6: 0x3278ec0,
        0x1a7: 0x3278f30,
        0x1a8: 0x3279020,
        0x1a9: 0x3279090,
        0x1aa: 0x3279100,
        0x1ab: 0x3279170,
        0x1ac: 0x32791e0,
        0x1ad: 0x3279250,
        0x1ae: 0x32792c0,
        0x1af: 0x3279330,
        0x1b0: 0x3279420,
        0x1b1: 0x3279490,
        0x1b2: 0x3279500,
        0x1b3: 0x3279570,
        0x1b4: 0x32795e0,
        0x1b5: 0x3279650,
        0x1b6: 0x32796c0,
        0x1b7: 0x3279730,
        0x1b8: 0x3279820,
        0x1b9: 0x3279890,
        0x1ba: 0x3279900,
        0x1bb: 0x3279970,
        0x1bc: 0x32799e0,
        0x1bd: 0x3279a50,
        0x1be: 0x3279ac0,
        0x1bf: 0x3279b30,
        0x1c0: 0x3279c20,
        0x1c1: 0x3279c90,
        0x1c2: 0x3279d00,
        0x1c3: 0x3279d70,
        0x1c4: 0x3279de0,
        0x1c5: 0x3279e50,
        0x1c6: 0x3279ec0,
        0x1c7: 0x3279f30,
        0x1c8: 0x327a020,
        0x1c9: 0x327a090,
        0x1ca: 0x327a100,
        0x1cb: 0x327a170,
        0x1cc: 0x327a1e0,
        0x1cd: 0x327a250,
        0x1ce: 0x327a2c0,
        0x1cf: 0x327a330,
        0x1d0: 0x327a420,
        0x1d1: 0x327a490,
        0x1d2: 0x327a500,
        0x1d3: 0x327a570,
        0x1d4: 0x327a5e0,
        0x1d5: 0x327a650,
        0x1d6: 0x327a6c0,
        0x1d7: 0x327a730,
        0x1d8: 0x327a820,
        0x1d9: 0x327a890,
        0x1da: 0x327a900,
        0x1db: 0x327a970,
        0x1dc: 0x327a9e0,
        0x1dd: 0x327aa50,
        0x1de: 0x327aac0,
        0x1df: 0x327ab30,
        0x1e0: 0x327b020,
        0x1e1: 0x327b090,
        0x1e2: 0x327b100,
        0x1e3: 0x327b170,
        0x1e4: 0x327b1e0,
        0x1e5: 0x327b250,
        0x1e6: 0x327b2c0,
        0x1e7: 0x327b330,
        0x1e8: 0x327b420,
        0x1e9: 0x327b490,
        0x1ea: 0x327b500,
        0x1eb: 0x327b570,
        0x1ec: 0x327b5e0,
        0x1ed: 0x327b650,
        0x1ee: 0x327b6c0,
        0x1ef: 0x327b730,
        0x1f0: 0x327b818,
        0x1f1: 0x327b888,
        0x1f2: 0x327b8f8,
        0x1f3: 0x327b968,
        0x1f4: 0x327b9d8,
        0x1f5: 0x327ba48
    },
    "DAWN":
    {
        0x40: 0x327be20,
        0x41: 0x327be90,
        0x42: 0x327bf00,
        0x43: 0x327bf70,
        0x44: 0x327bfe0,
        0x45: 0x327c050,
        0x46: 0x327c0c0,
        0x47: 0x327c130,
        0x48: 0x327c220,
        0x49: 0x327c290,
        0x4a: 0x327c300,
        0x4b: 0x327c370,
        0x4c: 0x327c3e0,
        0x4d: 0x327c450,
        0x4e: 0x327c4c0,
        0x4f: 0x327c530,
        0x50: 0x326d220,
        0x51: 0x326d290,
        0x52: 0x326d300,
        0x53: 0x326d370,
        0x54: 0x326d3e0,
        0x55: 0x326d450,
        0x56: 0x326d4c0,
        0x57: 0x326d530,
        0x58: 0x326d620,
        0x59: 0x326d690,
        0x5a: 0x326d700,
        0x5b: 0x326d770,
        0x5c: 0x326d7e0,
        0x5d: 0x326d850,
        0x5e: 0x326d8c0,
        0x5f: 0x326d930,
        0x60: 0x326da20,
        0x61: 0x326da90,
        0x62: 0x326db00,
        0x63: 0x326db70,
        0x64: 0x326dbe0,
        0x65: 0x326dc50,
        0x66: 0x326dcc0,
        0x67: 0x326dd30,
        0x68: 0x326de20,
        0x69: 0x326de90,
        0x6a: 0x326df00,
        0x6b: 0x326df70,
        0x6c: 0x326dfe0,
        0x6d: 0x326e050,
        0x6e: 0x326e0c0,
        0x6f: 0x326e130,
        0x70: 0x326e220,
        0x71: 0x326e290,
        0x72: 0x326e300,
        0x73: 0x326e370,
        0x74: 0x326e3e0,
        0x75: 0x326e450,
        0x76: 0x326e4c0,
        0x77: 0x326e530,
        0x78: 0x326e620,
        0x79: 0x326e690,
        0x7a: 0x326e700,
        0x7b: 0x326e770,
        0x7c: 0x326e7e0,
        0x7d: 0x326e850,
        0x7e: 0x326e8c0,
        0x7f: 0x326e930,
        0x80: 0x326ea20,
        0x81: 0x326ea90,
        0x82: 0x326eb00,
        0x83: 0x326eb70,
        0x84: 0x326ebe0,
        0x85: 0x326ec50,
        0x86: 0x326ecc0,
        0x87: 0x326ed30,
        0x88: 0x326ee20,
        0x89: 0x326ee90,
        0x8a: 0x326ef00,
        0x8b: 0x326ef70,
        0x8c: 0x326efe0,
        0x8d: 0x326f050,
        0x8e: 0x326f0c0,
        0x8f: 0x326f130,
        0x90: 0x326f220,
        0x91: 0x326f290,
        0x92: 0x326f300,
        0x93: 0x326f370,
        0x94: 0x326f3e0,
        0x95: 0x326f450,
        0x96: 0x326f4c0,
        0x97: 0x326f530,
        0x98: 0x326f620,
        0x99: 0x326f690,
        0x9a: 0x326f700,
        0x9b: 0x326f770,
        0x9c: 0x326f7e0,
        0x9d: 0x326f850,
        0x9e: 0x326f8c0,
        0x9f: 0x326f930,
        0xa8: 0x3270220,
        0xa9: 0x3270290,
        0xaa: 0x3270300,
        0xab: 0x3270370,
        0xac: 0x32703e0,
        0xad: 0x3270450,
        0xae: 0x32704c0,
        0xaf: 0x3270530,
        0xb0: 0x3270620,
        0xb1: 0x3270690,
        0xb2: 0x3270700,
        0xb3: 0x3270770,
        0xb4: 0x32707e0,
        0xb5: 0x3270850,
        0xb6: 0x32708c0,
        0xb7: 0x3270930,
        0xb8: 0x3270a20,
        0xb9: 0x3270a90,
        0xba: 0x3270b00,
        0xbb: 0x3270b70,
        0xbc: 0x3270be0,
        0xbd: 0x3270c50,
        0xbe: 0x3270cc0,
        0xbf: 0x3270d30,
        0xc0: 0x3270e20,
        0xc1: 0x3270e90,
        0xc2: 0x3270f00,
        0xc3: 0x3270f70,
        0xc4: 0x3270fe0,
        0xc5: 0x3271050,
        0xc6: 0x32710c0,
        0xc7: 0x3271130,
        0xc8: 0x3271220,
        0xc9: 0x3271290,
        0xca: 0x3271300,
        0xcb: 0x3271370,
        0xcc: 0x32713e0,
        0xcd: 0x3271450,
        0xce: 0x32714c0,
        0xcf: 0x3271530,
        0xd0: 0x3271620,
        0xd1: 0x3271690,
        0xd2: 0x3271700,
        0xd3: 0x3271770,
        0xd4: 0x32717e0,
        0xd5: 0x3271850,
        0xd6: 0x32718c0,
        0xd7: 0x3271930,
        0xd8: 0x3271a20,
        0xd9: 0x3271a90,
        0xda: 0x3271b00,
        0xdb: 0x3271b70,
        0xdc: 0x3271be0,
        0xdd: 0x3271c50,
        0xde: 0x3271cc0,
        0xdf: 0x3271d30,
        0xe0: 0x3271e20,
        0xe1: 0x3271e90,
        0xe2: 0x3271f00,
        0xe3: 0x3271f70,
        0xe4: 0x3271fe0,
        0xe5: 0x3272050,
        0xe6: 0x32720c0,
        0xe7: 0x3272130,
        0xe8: 0x3272220,
        0xe9: 0x3272290,
        0xea: 0x3272300,
        0xeb: 0x3272370,
        0xec: 0x32723e0,
        0xed: 0x3272450,
        0xee: 0x32724c0,
        0xef: 0x3272530,
        0xf0: 0x3272a20,
        0xf1: 0x3272a90,
        0xf2: 0x3272b00,
        0xf3: 0x3272b70,
        0xf4: 0x3272be0,
        0xf5: 0x3272c50,
        0xf6: 0x3272cc0,
        0xf7: 0x3272d30,
        0xf8: 0x3272e20,
        0xf9: 0x3272e90,
        0xfa: 0x3272f00,
        0xfb: 0x3272f70,
        0xfc: 0x3272fe0,
        0xfd: 0x3273050,
        0xfe: 0x32730c0,
        0xff: 0x3273130,
        0x100: 0x3273220,
        0x101: 0x3273290,
        0x102: 0x3273300,
        0x103: 0x3273370,
        0x104: 0x32733e0,
        0x105: 0x3273450,
        0x106: 0x32734c0,
        0x107: 0x3273530,
        0x108: 0x3273620,
        0x109: 0x3273690,
        0x10a: 0x3273700,
        0x10b: 0x3273770,
        0x10c: 0x32737e0,
        0x10d: 0x3273850,
        0x10e: 0x32738c0,
        0x10f: 0x3273930,
        0x110: 0x3273a20,
        0x111: 0x3273a90,
        0x112: 0x3273b00,
        0x113: 0x3273b70,
        0x114: 0x3273be0,
        0x115: 0x3273c50,
        0x116: 0x3273cc0,
        0x117: 0x3273d30,
        0x118: 0x3273e20,
        0x119: 0x3273e90,
        0x11a: 0x3273f00,
        0x11b: 0x3273f70,
        0x11c: 0x3273fe0,
        0x11d: 0x3274050,
        0x11e: 0x32740c0,
        0x11f: 0x3274130,
        0x120: 0x3274220,
        0x121: 0x3274290,
        0x122: 0x3274300,
        0x123: 0x3274370,
        0x124: 0x32743e0,
        0x125: 0x3274450,
        0x126: 0x32744c0,
        0x127: 0x3274530,
        0x128: 0x3274620,
        0x129: 0x3274690,
        0x12a: 0x3274700,
        0x12b: 0x3274770,
        0x12c: 0x32747e0,
        0x12d: 0x3274850,
        0x12e: 0x32748c0,
        0x12f: 0x3274930,
        0x130: 0x3274a20,
        0x131: 0x3274a90,
        0x132: 0x3274b00,
        0x133: 0x3274b70,
        0x134: 0x3274be0,
        0x135: 0x3274c50,
        0x136: 0x3274cc0,
        0x137: 0x3274d30,
        0x138: 0x3274e20,
        0x139: 0x3274e90,
        0x13a: 0x3274f00,
        0x13b: 0x3274f70,
        0x13c: 0x3274fe0,
        0x13d: 0x3275050,
        0x13e: 0x32750c0,
        0x13f: 0x3275130,
        0x140: 0x3275620,
        0x141: 0x3275690,
        0x142: 0x3275700,
        0x143: 0x3275770,
        0x144: 0x32757e0,
        0x145: 0x3275850,
        0x146: 0x32758c0,
        0x147: 0x3275930,
        0x148: 0x3275a20,
        0x149: 0x3275a90,
        0x14a: 0x3275b00,
        0x14b: 0x3275b70,
        0x14c: 0x3275be0,
        0x14d: 0x3275c50,
        0x14e: 0x3275cc0,
        0x14f: 0x3275d30,
        0x150: 0x3275e20,
        0x151: 0x3275e90,
        0x152: 0x3275f00,
        0x153: 0x3275f70,
        0x154: 0x3275fe0,
        0x155: 0x3276050,
        0x156: 0x32760c0,
        0x157: 0x3276130,
        0x158: 0x3276220,
        0x159: 0x3276290,
        0x15a: 0x3276300,
        0x15b: 0x3276370,
        0x15c: 0x32763e0,
        0x15d: 0x3276450,
        0x15e: 0x32764c0,
        0x15f: 0x3276530,
        0x160: 0x3276620,
        0x161: 0x3276690,
        0x162: 0x3276700,
        0x163: 0x3276770,
        0x164: 0x32767e0,
        0x165: 0x3276850,
        0x166: 0x32768c0,
        0x167: 0x3276930,
        0x168: 0x3276a20,
        0x169: 0x3276a90,
        0x16a: 0x3276b00,
        0x16b: 0x3276b70,
        0x16c: 0x3276be0,
        0x16d: 0x3276c50,
        0x16e: 0x3276cc0,
        0x16f: 0x3276d30,
        0x170: 0x3276e20,
        0x171: 0x3276e90,
        0x172: 0x3276f00,
        0x173: 0x3276f70,
        0x174: 0x3276fe0,
        0x175: 0x3277050,
        0x176: 0x32770c0,
        0x177: 0x3277130,
        0x178: 0x3277220,
        0x179: 0x3277290,
        0x17a: 0x3277300,
        0x17b: 0x3277370,
        0x17c: 0x32773e0,
        0x17d: 0x3277450,
        0x17e: 0x32774c0,
        0x17f: 0x3277530,
        0x180: 0x3277620,
        0x181: 0x3277690,
        0x182: 0x3277700,
        0x183: 0x3277770,
        0x184: 0x32777e0,
        0x185: 0x3277850,
        0x186: 0x32778c0,
        0x187: 0x3277930,
        0x188: 0x3277a20,
        0x189: 0x3277a90,
        0x18a: 0x3277b00,
        0x18b: 0x3277b70,
        0x18c: 0x3277be0,
        0x18d: 0x3277c50,
        0x18e: 0x3277cc0,
        0x18f: 0x3277d30,
        0x190: 0x3278220,
        0x191: 0x3278290,
        0x192: 0x3278300,
        0x193: 0x3278370,
        0x194: 0x32783e0,
        0x195: 0x3278450,
        0x196: 0x32784c0,
        0x197: 0x3278530,
        0x198: 0x3278620,
        0x199: 0x3278690,
        0x19a: 0x3278700,
        0x19b: 0x3278770,
        0x19c: 0x32787e0,
        0x19d: 0x3278850,
        0x19e: 0x32788c0,
        0x19f: 0x3278930,
        0x1a0: 0x3278a20,
        0x1a1: 0x3278a90,
        0x1a2: 0x3278b00,
        0x1a3: 0x3278b70,
        0x1a4: 0x3278be0,
        0x1a5: 0x3278c50,
        0x1a6: 0x3278cc0,
        0x1a7: 0x3278d30,
        0x1a8: 0x3278e20,
        0x1a9: 0x3278e90,
        0x1aa: 0x3278f00,
        0x1ab: 0x3278f70,
        0x1ac: 0x3278fe0,
        0x1ad: 0x3279050,
        0x1ae: 0x32790c0,
        0x1af: 0x3279130,
        0x1b0: 0x3279220,
        0x1b1: 0x3279290,
        0x1b2: 0x3279300,
        0x1b3: 0x3279370,
        0x1b4: 0x32793e0,
        0x1b5: 0x3279450,
        0x1b6: 0x32794c0,
        0x1b7: 0x3279530,
        0x1b8: 0x3279620,
        0x1b9: 0x3279690,
        0x1ba: 0x3279700,
        0x1bb: 0x3279770,
        0x1bc: 0x32797e0,
        0x1bd: 0x3279850,
        0x1be: 0x32798c0,
        0x1bf: 0x3279930,
        0x1c0: 0x3279a20,
        0x1c1: 0x3279a90,
        0x1c2: 0x3279b00,
        0x1c3: 0x3279b70,
        0x1c4: 0x3279be0,
        0x1c5: 0x3279c50,
        0x1c6: 0x3279cc0,
        0x1c7: 0x3279d30,
        0x1c8: 0x3279e20,
        0x1c9: 0x3279e90,
        0x1ca: 0x3279f00,
        0x1cb: 0x3279f70,
        0x1cc: 0x3279fe0,
        0x1cd: 0x327a050,
        0x1ce: 0x327a0c0,
        0x1cf: 0x327a130,
        0x1d0: 0x327a220,
        0x1d1: 0x327a290,
        0x1d2: 0x327a300,
        0x1d3: 0x327a370,
        0x1d4: 0x327a3e0,
        0x1d5: 0x327a450,
        0x1d6: 0x327a4c0,
        0x1d7: 0x327a530,
        0x1d8: 0x327a620,
        0x1d9: 0x327a690,
        0x1da: 0x327a700,
        0x1db: 0x327a770,
        0x1dc: 0x327a7e0,
        0x1dd: 0x327a850,
        0x1de: 0x327a8c0,
        0x1df: 0x327a930,
        0x1e0: 0x327ae20,
        0x1e1: 0x327ae90,
        0x1e2: 0x327af00,
        0x1e3: 0x327af70,
        0x1e4: 0x327afe0,
        0x1e5: 0x327b050,
        0x1e6: 0x327b0c0,
        0x1e7: 0x327b130,
        0x1e8: 0x327b220,
        0x1e9: 0x327b290,
        0x1ea: 0x327b300,
        0x1eb: 0x327b370,
        0x1ec: 0x327b3e0,
        0x1ed: 0x327b450,
        0x1ee: 0x327b4c0,
        0x1ef: 0x327b530,
        0x1f0: 0x327b618,
        0x1f1: 0x327b688,
        0x1f2: 0x327b6f8,
        0x1f3: 0x327b768,
        0x1f4: 0x327b7d8,
        0x1f5: 0x327b848
    }
}

# The following is mapped as [address]: [value to replace in given address]
# For this instance we assume 0x2135A00 as the new target address for Dusk, 0x2135840 as the new target address for Dawn, and 0xC as the new name length
PLAYERNAME_EXTENSION_ADDRESSES = {
    "DUSK":
    {
        0x38204: 0x2135a00, 
        0x382EC: 0x2135a00, 
        0x3842C: 0x2135a00, 
        0x3FFB4: 0x2135a00, 
        0x4793C: 0x2135a00, 
        0x4BCA0: 0x2135a00, 
        0x7AAC4: 0x2135a00, 
        0xDB3C4: 0x2135a00, 
        0xDCAB4: 0x2135a00, 
        0xDD3AC: 0x2135a00, 
        0xE50C8: 0x2135a00, 
        0xE78E4: 0x2135a00, 
        0xEADA4: 0x2135a00, 
        0x17C228: 0x2135a00, 
        0x234060: 0x2135a00, 
        0x244F60: 0x2135a00, 
        0x27F3EC: 0x2135a00,
        0x40738: 0xe2822040,
        0x40754: 0xe2822040,
        0x27EE7C: 0xe3a02007,
        0x40764: 0xe3510007,
        0x32918: 0xe2840040,
        0xe09ac: 0xe3a02000,
        0xe09bc: 0xe3a02000,
        0xe09d4: 0xe3a02000
    },
    "DAWN":
    {
        0x381F0: 0x02135840, 
        0x382D8: 0x02135840, 
        0x38418: 0x02135840, 
        0x3FFA0: 0x02135840, 
        0x47928: 0x02135840, 
        0x4BC88: 0x02135840, 
        0x7AA54: 0x02135840, 
        0xDB2CC: 0x02135840, 
        0xDC9BC: 0x02135840, 
        0xDD2B4: 0x02135840, 
        0xE4FD0: 0x02135840, 
        0xE77EC: 0x02135840, 
        0xEACA8: 0x02135840,
        0x17C028: 0x02135840, 
        0x233E60: 0x02135840, 
        0x244D60: 0x02135840, 
        0x27F1E8: 0x02135840,
        0x40724: 0xe2822040, 
        0x40740: 0xe2822040,
        0x27EC78: 0xe3a02007,
        0x40750: 0xe3510007,
        0x32910: 0xe2840040,
        0xe08b4: 0xe3a0200,
        0xe08c4: 0xe3a0200,
        0xe08dc: 0xe3a0200
    }
}

# This defines a base exp value for each digimon evolution stage which is then used to calc the patched exp values for each digimon
EXP_FLAT_BY_STAGE = {
    "IN-TRAINING": 40,
    "ROOKIE": 80,
    "CHAMPION": 150,
    "ULTIMATE": 240,
    "MEGA": 330
}