import math

def electric_smelter(num_furnaces):
    # https://www.factorio.school/view/-LM4FAS99hG83TEAl_9T

    # we use a basic model and assume you replace stone with electric (so
    # smelter can occupy same physical layout)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/5d7c46cad2773d4b5f185d6b2c5606a8d9e2abf9/position/1

    # 2 electric furnaces take up 39 squares (13*3)

    # 12 smelters on each side fills a yellow belt
    # 24 smelters on each side fills a red belt

    # https://steamcommunity.com/sharedfiles/filedetails/?id=862972621
    num_furnaces = math.ceil(num_furnaces)
    # "4 + 4" covers belts to and from and associated splitting
    if num_furnaces < (24 * 2):
        # if we have fewer than 48, just put them in one long line 13 wide
        return (4 + 4 + math.ceil(num_furnaces/2*3), 13)
    num_stacks = math.ceil(num_furnaces / 48)
    # each "stack" is a collection of 48 furnaces, 24 on either side of a belt
    return (4 + 4 + 24*3, 13*num_stacks)

def green_circuit(num_assemblers):
    packs = math.ceil(num_assemblers/2)

    # https://www.factorio.school/view/-KoqgcmWqjJGLf6csjL4
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/af8b75847d0714575989e1efac4f8cc5e7470f9d/position/0
    width = min(26, packs * 13)

    # lazy https://claude.ai/chat/f936dad3-e427-42a9-b516-da32f2fd5a23
    # add height at the bottom for input and belts
    if packs <= 2:
        height = 13 + 4
    elif packs <= 4:
        height = 26 + 4
    else:
        height = 26 + 4 + 13 * ((packs - 1) // 2 - 1)

    return (width, height)

def red_circuit(num_assemblers):
    # inner belt: left side red circuits, right side half green, half plastic
    # outer belt: one side copper, one side coils
    # https://www.factorio.school/view/-Kp6eLXuhwCqXBXr0ltW
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/87805c2ea48b411ef0f8e561758f6229ffb04cda/position/0
    # https://imgur.com/T5WlY0M
    # need one copper coil for every 6 red circuits
    num_assemblers = math.ceil(num_assemblers)
    copper_coils = math.ceil(num_assemblers/6)
    if copper_coils == 1:
        # 8 wide, 4 for copper, 4 per red assembler
        return (4 + 4*num_assemblers, 8)
    # 4 height for every two assemblers
    # 4 height for every 2 copper coil assemblers
    return (math.ceil(copper_coils/2)*4 + math.ceil(num_assemblers/2)*4, 14)

def blue_circuit(num_assemblers):
    # https://www.factorio.school/view/-KpX1-lyYhE-3-DfxTba
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
        return (4*math.ceil(num_chemical_plants), 7)

    # use both sides of belt
    return (4*math.ceil(num_chemical_plants/2), 12)

def advanced_oil(num_oil_plants):
    # https://www.factorio.school/view/-LZpCwcZo6mMnV7TZdG1
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/6dfc4516b341d0bdbbc56c22a2a74b65b28535a7/
    return (22, 2+5+(5+1)*math.ceil(num_oil_plants))

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

grid_size = (275, 200)

# 2 rocket parts a minute, full rocket silo in 10 minutes
# https://kirkmcdonald.github.io/calc.html#tab=graph&data=1-1-19&items=rocket-part:r:2,rocket-silo:r:1/10
rocket_blocks = {
    "Copper Mine": (1, 1),
    "Ore Mine": (1, 1),
    "Coal Mine": (1, 1),
    "Water": (1, 1),
    "Oil": (1, 1),
    "Stone": (1, 1),

    "Copper Smelting": electric_smelter(72.3),
    "Iron Smelting": electric_smelter(58.6),
    "Steel Smelting": electric_smelter(21.4),
    "Stone Smelting": electric_smelter(1.4),

    "Plastic": plastic(3.9),

    # No separate copper coil block - all assembly part of green or red circuits
    "Green Circuit Assembly": green_circuit(21.7),
    "Red Circuit Assembly": red_circuit(36),
    "Blue Circuit Assembly": blue_circuit(8.9),

    "Advanced Oil Processing": advanced_oil(5.6),

    # these are included in the Advanced Oil processing footprint
    # need 1.5 light oil crackers
    "Light Oil Cracking": (1, 1),
    # 1.2 crackers
    "Heavy Oil Cracking": (1, 1),

    "Sulfur": plastic(1),
    "Sulfuric Acid": (15, 10),

    "Low Density Structure": low_density_structure(13.4),

    "Speed Module": min_speed_module(10),

    "Electric Engine Unit": plastic(4.5),
    "Concrete": plastic(2.3),

    "Solid Fuel": solid_fuel(6.7),
    "Rocket Fuel": rocket_fuel(13.4),
    "Rocket Control Unit": electric_smelter(10),

    "Rocket Silo Assembler": (6, 6),
    "Rocket": (10, 10),
}

# ratios:
#
# https://www.reddit.com/r/factorio/comments/birqnl/boiler_fuel_consumption_and_steam_engine_setup/
# one steam engine can produce 900kW, two steam engines = 1.8MW
# Solid fuel: 360 per minute for 40 boilers

# https://kirkmcdonald.github.io/calc.html#zip=dY1NDsIgEIVvwwoiRRMjCYcZp9hOCgyBYeHtbRcuNJq3+96fwD0sDeqqZhAIk9l1U5lKcCrXxnNwVpHE3AMM4QxCXExHigWjqYCbb/5sdeKFuhD+sHCNmRDSp/Xwk9PHwcA/k0MokTy/a1fdGLcoplPiI3m62Deq0GRH7gU=
blocks = {
    "Copper Mine": (1, 1),
    "Ore Mine": (1, 1),
    "Coal Mine": (1, 1),
    "Water": (1, 1),
    "Oil": (1, 1),
    "Stone Mine": (1, 1),

    "Copper Smelting": electric_smelter(152.7),
    "Iron Smelting": electric_smelter(152.9),
    "Steel Smelting": electric_smelter(72.7),
    "Stone Smelting": electric_smelter(3.7),

    "Advanced Oil Processing": advanced_oil(12.5),
    # 1.2 crackers
    "Heavy Oil Cracking": (10, 10),
    # need 4.9 light oil crackers - these are covered in advanced oil
    "Light Oil Cracking": (10, 10),

    "Plastic": plastic(4.9),

    "Green Circuit Assembly": green_circuit(26.5),
    "Red Circuit Assembly": red_circuit(53),
    "Blue Circuit Assembly": blue_circuit(14.5),

    # https://www.factorio.school/view/-M3UFESzD4DDkv8E__6l
    "Inserter Mall": (7, 28),

    # https://www.factorio.school/view/-L8geV1--kQGYWiMW4v6
    # Add some height for iron gear assembler
    "Belt Mall": (16, 18),

    # This is covered as part of Yellow Science
    # "Low Density Structure": low_density_structure(20),

    # tileable science: https://www.factorio.school/view/-KnQ865j-qQ21WoUPbd3

    # 1 gear assembler
    # only really need one side of the belt
    "Red Science": (19, 12),

    # 2 gear assemblers
    # 1 inserter assembler
    # 1 belt assembler
    "Green Science": (18, 16),

    # 12 blue science factories
    # 10 engine assemblers
    # 1 pipe assembler
    # 1 gear assembler
    # it's 25x18, but add some buffer for belt input/output
    "Blue Science": (27, 22),
    # "Blue Science": blue_science(12),

    # 7 purple science uses:
    # 3 rail assemblers
    # 2 furnace assemblers
    # 5 productivity module assemblers
    # 2 iron assemblers
    #
    # add a third furnace in here
    "Purple Science": (33, 15),

    # 4 engine assemblers
    # 4 electric engine assemblers
    # 7 flying robot frames
    "Yellow Science": (41, 32),

    # 0.2
    "Sulfuric Acid": plastic(1),

    # 0.3 - covered in advanced oil
    "Lubricant": plastic(1),

    "Battery": plastic(1.4),

    # yellow science covers 4 of 5.6
    "Electric Engine Unit": plastic(3),

    "Sulfur": plastic(1),

    "Concrete": plastic(1.7),

    "Solid Fuel": solid_fuel(6.7),
    "Rocket Fuel": rocket_fuel(13.4),
    "Rocket Control Unit": electric_smelter(20),
    "Rocket": (11, 9),

    "Lab": (19, 24),
}

print("blocks: {}".format(blocks))

rotatable_blocks = {name for name, (w, h) in blocks.items() if w != h and w > 5 and h > 5}

connections = [
    ("Coal Mine", "Copper Smelting", "MM", "BM"),
    ("Copper Mine", "Copper Smelting", "MM", "BM"),

    ("Coal Mine", "Iron Smelting", "MM", "LM"),
    ("Ore Mine", "Iron Smelting", "MM", "LM"),

    ("Iron Smelting", "Steel Smelting", "RM", "LM"),
    ("Coal Mine", "Steel Smelting", "MM", "LM"),

    ("Stone Mine", "Stone Smelting", "RM", "LM"),
    ("Coal Mine", "Stone Smelting", "MM", "LM"),

    ("Iron Smelting", "Green Circuit Assembly", "RM", "BM"),
    # TODO - two entrances here, left and right
    ("Copper Smelting", "Green Circuit Assembly", "RM", "BL"),

    ("Iron Smelting", "Inserter Mall", "RM", "BL"),
    ("Green Circuit Assembly", "Inserter Mall", "BM", "BR"),

    ("Iron Smelting", "Belt Mall", "RM", "TM"),
    ("Green Circuit Assembly", "Belt Mall", "BM", "TL"),

    ("Advanced Oil Processing", "Plastic", "TL", "TL"),
    ("Light Oil Cracking", "Plastic", "RM", "TL"),
    ("Coal Mine", "Plastic", "MM", "LM"),

    ("Copper Smelting", "Red Circuit Assembly", "RM", "TL"),
    ("Green Circuit Assembly", "Red Circuit Assembly", "BM", "LM"),
    ("Plastic", "Red Circuit Assembly", "RM", "LM"),

    ("Heavy Oil Cracking", "Light Oil Cracking", "MM", "MM"),

    ("Water", "Advanced Oil Processing", "TL", "TL"),
    ("Oil", "Advanced Oil Processing", "TL", "TL"),

    ("Advanced Oil Processing", "Light Oil Cracking", "TL", "MM"),
    ("Advanced Oil Processing", "Heavy Oil Cracking", "TL", "MM"),

    ("Water", "Sulfur", "MM", "MM"),
    ("Advanced Oil Processing", "Sulfur", "MM", "MM"),

    ("Advanced Oil Processing", "Lubricant", "MM", "MM"),

    ("Water", "Sulfuric Acid", "MM", "MM"),
    ("Iron Smelting", "Sulfuric Acid", "RM", "MM"),
    ("Sulfur", "Sulfuric Acid", "MM", "MM"),

    ("Sulfuric Acid", "Blue Circuit Assembly", "MM", "LT"),
    ("Green Circuit Assembly", "Blue Circuit Assembly", "BM", "BM"),
    ("Red Circuit Assembly", "Blue Circuit Assembly", "LM", "BM"),

    ("Steel Smelting", "Low Density Structure", "RM", "MM"),
    ("Plastic", "Low Density Structure", "RM", "MM"),
    ("Copper Smelting", "Low Density Structure", "RM", "MM"),

    ("Green Circuit Assembly", "Speed Module", "BM", "MM"),
    ("Red Circuit Assembly", "Speed Module", "LM", "MM"),

    ("Iron Smelting", "Red Science", "RM", "TR"),
    ("Copper Smelting", "Red Science", "RM", "TR"),

    ("Iron Smelting", "Green Science", "RM", "TR"),
    ("Green Circuit Assembly", "Green Science", "RM", "TR"),

    ("Iron Smelting", "Blue Science", "RM", "TL"),
    ("Steel Smelting", "Blue Science", "RM", "TM"),
    ("Red Circuit Assembly", "Blue Science", "LM", "TR"),
    ("Sulfur", "Blue Science", "MM", "TR"),

    ("Lubricant", "Yellow Science", "MM", "TL"),
    ("Green Circuit Assembly", "Yellow Science", "MM", "MM"),
    ("Steel Smelting", "Yellow Science", "RM", "TM"),
    ("Iron Smelting", "Yellow Science", "RM", "TL"),
    ("Plastic", "Yellow Science", "MM", "MM"),
    ("Copper Smelting", "Yellow Science", "RM", "TR"),
    ("Battery", "Yellow Science", "MM", "TL"),
    ("Blue Circuit Assembly", "Yellow Science", "MM", "TM"),

    ("Steel Smelting", "Purple Science", "RM", "TL"),
    ("Iron Smelting", "Purple Science", "RM", "TL"),
    ("Stone Mine", "Purple Science", "RM", "TL"),
    ("Stone Smelting", "Purple Science", "RM", "TM"),
    ("Red Circuit Assembly", "Purple Science", "LM", "TM"),
    ("Green Circuit Assembly", "Purple Science", "BM", "TM"),

    ("Red Science", "Lab", "TL", "BL"),
    ("Green Science", "Lab", "TL", "BL"),
    ("Blue Science", "Lab", "TR", "BL"),
    ("Yellow Science", "Lab", "TM", "BL"),
    ("Purple Science", "Lab", "TR", "BL"),

    ("Sulfuric Acid", "Battery", "MM", "MM"),

    ("Advanced Oil Processing", "Solid Fuel", "TL", "MM"),
    ("Heavy Oil Cracking", "Solid Fuel", "MM", "MM"),

    ("Advanced Oil Processing", "Rocket Fuel", "TL", "MM"),
    ("Heavy Oil Cracking", "Rocket Fuel", "MM", "MM"),
    ("Solid Fuel", "Rocket Fuel", "MM", "MM"),

    ("Speed Module", "Rocket Control Unit", "MM", "MM"),
    ("Blue Circuit Assembly", "Rocket Control Unit", "MM", "MM"),

    ("Water", "Concrete", "MM", "MM"),
    ("Iron Ore", "Concrete", "MM", "MM"),
    ("Stone Smelting", "Concrete", "RM", "MM"),

    ("Lubricant", "Electric Engine Unit", "MM", "TL"),
    ("Green Circuit Assembly", "Electric Engine Unit", "MM", "MM"),
    # hack - this reuses the engine assemblers from blue science
    ("Blue Science", "Electric Engine Unit", "MM", "MM"),

    ("Concrete", "Rocket Silo Assembler", "MM", "MM"),
    ("Electric Engine Unit", "Rocket Silo Assembler", "MM", "MM"),
    ("Blue Circuit Assembly", "Rocket Silo Assembler", "MM", "MM"),
    ("Steel Smelting", "Rocket Silo Assembler", "RM", "MM"),

    ("Rocket Fuel", "Rocket", "MM", "MM"),
    ("Low Density Structure", "Rocket", "MM", "MM"),
    ("Rocket Control Unit", "Rocket", "MM", "MM"),
]
