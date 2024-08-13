import math

def electric_smelter(num_furnaces):
    # https://www.factorio.school/view/-LM4FAS99hG83TEAl_9T

    # we use a basic model and assume you replace stone with electric (so
    # smelter can occupy same physical layout)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/5d7c46cad2773d4b5f185d6b2c5606a8d9e2abf9/position/1

    # this covers the splitter and belt tunnel
    splitter_belt_tunnel_width = 4

    # 2 electric furnaces take up 39 squares
    return (4 + math.ceil(num_furnaces/2)*3, 13)

def green_circuit(num_assemblers):
    packs = math.ceil(num_assemblers/2)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/af8b75847d0714575989e1efac4f8cc5e7470f9d/position/0
    first_value = min(26, packs * 13)

    # lazy https://claude.ai/chat/f936dad3-e427-42a9-b516-da32f2fd5a23
    if packs <= 2:
        second_value = 13
    elif packs <= 4:
        second_value = 26
    else:
        second_value = 26 + 13 * ((packs - 1) // 2 - 1)

    return (first_value, second_value)

def red_circuit(num_assemblers):
    # inner belt: left side red circuits, right side half green, half plastic
    # outer belt: one side copper, one side coils
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/87805c2ea48b411ef0f8e561758f6229ffb04cda/position/0
    # https://imgur.com/T5WlY0M
    # need one copper coil for every 6 red circuits
    copper_coils = math.ceil(num_assemblers/6)
    if copper_coils == 1:
        # 8 wide, 4 for copper, 4 per red assembler
        return (8, 4 + 4*num_assemblers)
    # 4 height for every two assemblers
    # 4 height for every 2 copper coil assemblers
    return (14, math.ceil(copper_coils/2)*4 + math.ceil(num_assemblers/2)*4)

def blue_circuit(num_assemblers):
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/be6ac0d54651537214601211c9d98984a16d9d3e/position/0
    # center belt is red circuits
    # left/right belts are green circuits
    # outer belts are blue circuits
    packs = math.ceil(num_assemblers/4)
    return (17, packs*9)

def plastic(num_chemical_plants):
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/265ce01196a689ef5ea6eae916b84b812b06784e/
    # petroleum gas above the chem plant
    # plastic out on top belt
    # copper on bottom belt
    if num_chemical_plants <= 3:
        return (4*num_chemical_plants, 7)

    # use both sides of belt
    return (4*math.ceil(num_chemical_plants/2), 12)

def advanced_oil(num_oil_plants):
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/4f84c953ea8d3e035c9b706ade311a99ebc0faaf/position/1
    extra_space_width = 20

    return (extra_space_width + 6*math.ceil(num_oil_plants), 12)

def low_density_structure(num_assemblers):
    # https://www.factorio.school/view/-M5Dma3GTTR-aB704Bxa
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/15759bc3e06d659beff0c65b9ff95fff4efcec40/

    # 14 high
    # 4 extra wide
    # 3 wide for every 2 assemblers
    return (14, 4 + math.ceil(num_assemblers/2)*3)

def min_speed_module(num_assemblers):
    # height:
    # - belt above
    # - inserter
    # - 3 for assembler
    # - inserter
    # - belt below
    return (7, math.ceil(num_assemblers) * 3 + 5)

def solid_fuel(num_plants):
    # ??
    # https://www.factorio.school/view/-L_dgvit-TLeoWF3EL6K
    return (7, math.ceil(num_plants) * 3 + 5)

def rocket_fuel(num_assemblers):
    # https://www.factorio.school/view/-NfTYT_f1XATK_h5dfoz
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/7adea92fb28bef85a361d46b6976064aedf817f5/
    # each one takes up 7 - pipe, 3 assembler, 2 belts, inserter
    return (7, math.ceil(num_assemblers) * 3 + 5)

grid_size = (200, 200)

# 2 rocket parts a minute
# https://kirkmcdonald.github.io/calc.html#data=1-1-19&items=rocket-part:r:2
blocks = {
    "Copper Mine": (1, 1),
    "Ore Mine": (1, 1),
    "Coal Mine": (1, 1),
    "Water": (1, 1),
    "Oil": (1, 1),

    "Copper Smelting": electric_smelter(49.4),
    "Iron Smelting": electric_smelter(26.2),
    "Steel Smelting": electric_smelter(5.4),

    "Plastic": plastic(3.2),

    # No separate copper coil block - all assembly part of green or red circuits
    "Green Circuit Assembly": green_circuit(13),
    "Red Circuit Assembly": red_circuit(28),
    "Blue Circuit Assembly": blue_circuit(4.5),

    "Advanced Oil Processing": advanced_oil(4.7),

    # need 1.5 light oil crackers
    "Light Oil Cracking": (10, 10),
    # 1.2 crackers
    "Heavy Oil Cracking": (10, 10),

    "Sulfuric Acid": (15, 10),

    "Low Density Structure": low_density_structure(13.4),

    "Speed Module": min_speed_module(10),

    "Solid Fuel": solid_fuel(6.7),
    "Rocket Fuel": rocket_fuel(13.4),
    "Rocket Control Unit": electric_smelter(10),

    "Rocket": (10, 10),
}

print("blocks: {}", blocks)

rotatable_blocks = {name for name, (w, h) in blocks.items() if w != h and w > 5 and h > 5}

connections = [
    ("Coal Mine", "Copper Smelting", "MM", "LM"),
    ("Copper Mine", "Copper Smelting", "MM", "LM"),

    ("Coal Mine", "Iron Smelting", "MM", "LM"),
    ("Ore Mine", "Iron Smelting", "MM", "LM"),

    ("Iron Smelting", "Steel Smelting", "RM", "LM"),
    ("Coal Mine", "Steel Smelting", "MM", "LM"),

    ("Iron Smelting", "Green Circuit Assembly", "RM", "BM"),
    # TODO - two entrances here, left and right
    ("Copper Smelting", "Green Circuit Assembly", "RM", "BL"),

    ("Advanced Oil Processing", "Plastic", "RM", "TL"),
    ("Light Oil Cracking", "Plastic", "RM", "TL"),
    ("Coal Mine", "Plastic", "MM", "LM"),

    ("Copper Smelting", "Red Circuit Assembly", "RM", "BM"),
    ("Green Circuit Assembly", "Red Circuit Assembly", "BM", "BM"),
    ("Plastic", "Red Circuit Assembly", "RM", "BM"),

    ("Heavy Oil Cracking", "Light Oil Cracking", "MM", "MM"),

    ("Water", "Advanced Oil Processing", "MM", "MM"),
    ("Oil", "Advanced Oil Processing", "MM", "MM"),

    ("Advanced Oil Processing", "Light Oil Cracking", "MM", "MM"),
    ("Advanced Oil Processing", "Heavy Oil Cracking", "MM", "MM"),

    ("Water", "Sulfuric Acid", "MM", "MM"),
    ("Iron Smelting", "Sulfuric Acid", "MM", "MM"),
    ("Light Oil Cracking", "Sulfuric Acid", "MM", "MM"),

    ("Sulfuric Acid", "Blue Circuit Assembly", "MM", "MM"),
    ("Green Circuit Assembly", "Blue Circuit Assembly", "MM", "MM"),
    ("Red Circuit Assembly", "Blue Circuit Assembly", "MM", "MM"),

    ("Steel Smelting", "Low Density Structure", "MM", "MM"),
    ("Plastic", "Low Density Structure", "MM", "MM"),
    ("Copper Smelting", "Low Density Structure", "MM", "MM"),

    ("Green Circuit Assembly", "Speed Module", "MM", "MM"),
    ("Red Circuit Assembly", "Speed Module", "MM", "MM"),

    ("Advanced Oil Processing", "Solid Fuel", "MM", "MM"),
    ("Heavy Oil Cracking", "Solid Fuel", "MM", "MM"),

    ("Advanced Oil Processing", "Rocket Fuel", "MM", "MM"),
    ("Heavy Oil Cracking", "Rocket Fuel", "MM", "MM"),
    ("Solid Fuel", "Rocket Fuel", "MM", "MM"),

    ("Speed Module", "Rocket Control Unit", "MM", "MM"),
    ("Blue Circuit Assembly", "Rocket Control Unit", "MM", "MM"),

    ("Rocket Fuel", "Rocket", "MM", "MM"),
    ("Low Density Structure", "Rocket", "MM", "MM"),
    ("Rocket Control Unit", "Rocket", "MM", "MM"),
]
