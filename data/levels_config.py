"""
Level configuration: 300 levels across 10 themes.
Each theme has 30 levels.
"""

THEMES = [
    {'id': 'forest',     'name_key': 'forest',    'bg_color': [0.13, 0.45, 0.13, 1], 'levels': range(1,   31)},
    {'id': 'cave',       'name_key': 'cave',      'bg_color': [0.25, 0.20, 0.15, 1], 'levels': range(31,  61)},
    {'id': 'clearing',   'name_key': 'clearing',  'bg_color': [0.55, 0.80, 0.30, 1], 'levels': range(61,  91)},
    {'id': 'night',      'name_key': 'night',     'bg_color': [0.05, 0.05, 0.20, 1], 'levels': range(91,  121)},
    {'id': 'underwater', 'name_key': 'underwater','bg_color': [0.05, 0.35, 0.65, 1], 'levels': range(121, 151)},
    {'id': 'volcano',    'name_key': 'volcano',   'bg_color': [0.60, 0.15, 0.05, 1], 'levels': range(151, 181)},
    {'id': 'snow',       'name_key': 'snow',      'bg_color': [0.80, 0.90, 0.95, 1], 'levels': range(181, 211)},
    {'id': 'cloud',      'name_key': 'cloud',     'bg_color': [0.70, 0.85, 1.00, 1], 'levels': range(211, 241)},
    {'id': 'desert',     'name_key': 'desert',    'bg_color': [0.90, 0.75, 0.30, 1], 'levels': range(241, 271)},
    {'id': 'haunted',    'name_key': 'haunted',   'bg_color': [0.15, 0.08, 0.20, 1], 'levels': range(271, 301)},
]

ANIMALS_PER_SET = [
    ['rabbit','fox','deer','bear','owl','wolf','squirrel','hedgehog','raccoon','beaver','otter','skunk','moose','lynx','eagle'],
    ['bat','mole','spider','scorpion','snake','lizard','toad','worm','cricket','beetle','mushroom_gnome','cave_bear','stalactite_sprite','glowworm','salamander'],
    ['butterfly','bee','ladybug','grasshopper','dragonfly','frog','duck','swan','heron','stork','firefly','mantis','caterpillar','snail','dove'],
    ['firefly','owl','wolf','panther','nighthawk','bat_prince','shadow_cat','moon_rabbit','star_fox','luna_moth','night_heron','glowbug','dark_deer','midnight_bear','phantom_bird'],
    ['dolphin','octopus','seahorse','jellyfish','clownfish','shark','turtle','crab','starfish','mermaid_cat','pufferfish','anglerfish','coral_sprite','sea_dragon','narwhal'],
    ['phoenix','fire_lizard','lava_toad','ember_fox','magma_crab','ash_wolf','flame_butterfly','volcano_bird','obsidian_snake','cinder_bear','heat_sprite','smoke_cat','eruption_frog','lava_eel','fire_deer'],
    ['arctic_fox','polar_bear','snow_owl','ice_rabbit','penguin','reindeer','snow_leopard','frost_wolf','ice_dragon','blizzard_bird','tundra_hare','glacier_seal','snowflake_fairy','yeti_cub','crystal_deer'],
    ['cloud_sheep','sky_whale','wind_horse','thunder_bird','rainbow_fox','storm_cat','nimbus_rabbit','celestial_owl','air_dragon','cumulus_bear','breeze_butterfly','lightning_beetle','gale_wolf','mist_deer','cirrus_bird'],
    ['sand_cat','camel','desert_fox','scorpion_king','dune_snake','oasis_frog','mirage_deer','dust_rabbit','sun_lizard','cactus_sprite','sandstorm_wolf','heat_owl','pyramid_cat','golden_eagle','desert_tortoise'],
    ['ghost_cat','shadow_wolf','phantom_deer','spirit_fox','haunted_owl','skeleton_rabbit','witch_bear','zombie_frog','banshee_bird','specter_snake','cursed_butterfly','demon_lizard','pumpkin_sprite','graveyard_bat','wraith_elk'],
]


def get_theme_for_level(level: int) -> dict:
    for theme in THEMES:
        if level in theme['levels']:
            return theme
    return THEMES[-1]


def get_animals_for_level(level: int) -> list:
    theme_idx = (level - 1) // 30
    return ANIMALS_PER_SET[min(theme_idx, len(ANIMALS_PER_SET) - 1)]


def diamonds_for_level(level: int) -> int:
    return 5 + (level // 10) * 2
